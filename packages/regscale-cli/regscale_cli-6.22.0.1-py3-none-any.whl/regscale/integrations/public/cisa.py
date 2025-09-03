#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CISA into RegScale"""

# standard python imports
import logging
import re
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from datetime import date, datetime
from typing import List, Optional, Tuple, Any, Dict, Union
from urllib.error import URLError
from urllib.parse import urlparse

import click
import dateutil.parser as dparser
import requests
from bs4 import BeautifulSoup, Tag
from requests import exceptions
from rich.console import Console

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import is_valid
from regscale.models import Link, Threat
from regscale.core.app.utils.app_utils import error_and_exit
from regscale.utils.string import extract_url

logger = logging.getLogger("regscale")
console = Console()
CISA_THREATS_URL = (
    "https://www.cisa.gov/news-events/cybersecurity-advisories"
    "?search_api_fulltext=&sort_by=field_release_date&f%5B0%5D="
    "advisory_type%3A94&f%5B1%5D=release_date_year%3A"
)
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
THREATS_SUFFIX = "/api/threats"
DEFAULT_STR = "See Link for details."


@click.group()
def cisa():
    """Update CISA."""


@cisa.command(name="ingest_cisa_kev")
def ingest_cisa_kev():
    """Update RegScale threats with the latest Known Exploited \
    Vulnerabilities (KEV) feed from cisa.gov."""
    data = pull_cisa_kev()
    update_regscale(data)


@cisa.command(name="ingest_cisa_alerts")
@click.option(
    "--year",
    type=click.INT,
    help="Enter the year to search for CISA alerts.",
    default=date.today().year,
    show_default=True,
    required=True,
)
def ingest_cisa_alerts(year: int):
    """Update RegScale threats with alerts from cisa.gov."""
    alerts(year)


def update_regscale_links(threats: List[Threat]) -> None:
    """
    Create RegScale links from Threat Responses

    :param List[Threat] threats: List of Responses from RegScale API
    :rtype: None
    """

    links = []
    for threat in threats:
        if url := extract_url(threat.description):
            link = Link(
                parentID=threat.id,
                parentModule="threats",
                url=url,
                title=threat.title,
            )
            links.append(link)
    Link.batch_update(links)


def process_threats(threats: list[Threat], unique_threats: set[str], reg_threats: list[Threat]) -> Tuple[list, list]:
    """
    Process threats

    :param list[Threat] threats: List of threats to process
    :param set[str] unique_threats: Set of unique threat descriptions
    :param list[Threat] reg_threats: List of RegScale threats
    :return: Tuple of insert and update threats
    :rtype: Tuple[list, list]
    """
    insert_threats = []
    update_threats = []
    for threat in threats:
        if threat and threat.description in unique_threats:
            old_dict = [reg.dict() for reg in reg_threats if reg.description == threat.description][0]
            update_dict = threat.dict()
            update_dict = merge_old(update_dict, old_dict)
            update_threats.append(update_dict)  # Update
        elif threat:
            insert_threats.append(threat.dict())  # Post
    return insert_threats, update_threats


def alerts(year: int) -> None:
    """
    Return CISA alerts for the specified year

    :param int year: A target year for CISA alerts
    :rtype: None
    """
    app = Application()
    update_threats = []
    insert_threats = []
    # Check to make sure we have a valid token
    if not is_valid(app=app):
        error_and_exit("Login Error: Invalid Credentials, please login for a new token.")

    reg_threats = Threat.fetch_all_threats()
    unique_threats = {reg.description for reg in reg_threats}
    logger.info("Fetching CISA threats for %i...", year)
    threats = parse_html(CISA_THREATS_URL + str(year), app=app)
    logger.info("Found %i threats from CISA.", len(threats))

    if len(threats) > 0:
        logger.info("Processing %i threat(s)...", len(threats))
        insert_threats, update_threats = process_threats(threats, unique_threats, reg_threats)

    logging.getLogger("urllib3").propagate = False
    if insert_threats:
        logger.info("Inserting %i threats to RegScale...", len(insert_threats))
        threats = Threat.bulk_insert(api=None, threats=insert_threats)
        update_regscale_links(threats)
    if update_threats:
        update_regscale_threats(json_list=[Threat(**threat) for threat in update_threats])


def parse_html(page_url: str, app: Application) -> list:
    """
    Convert HTML from a given URL to a RegScale threat

    :param str page_url: A URL to parse
    :param Application app: Application object
    :return: List of RegScale threats
    :rtype: list
    """
    control = {"page": 0, "items": 999, "links": []}
    while control["items"] > 0:
        soup = gen_soup(page_url + f"&page={control['page']}")

        articles = soup.find_all("article")
        for article in articles:
            try:
                title = article.text.strip("\n").replace("\n", " ").split("|")[1].strip(" ").replace("    ", " ")
            except IndexError:
                continue
            short_description = ""
            article_soup = article.find_all("a", href=True)
            link = ("https://www.cisa.gov" + article_soup[0]["href"]) if article_soup else None
            if is_url(link):
                logger.debug("Short Description: %s", short_description)
                control["links"].append((link, short_description, title))
                logger.info("Building RegScale threat from %s.", link)

        control["items"] = len(articles)
        control["page"] += 1
        # check if max threads <= 20 to prevent IP ban from CISA
        max_threads_config = app.config.get("maxThreads", 100)
        if not isinstance(max_threads_config, int):
            try:
                max_threads_config = int(max_threads_config)
            except (ValueError, TypeError):
                max_threads_config = 100
        max_threads = min(max_threads_config, 20)
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for link in control["links"]:
                logger.debug("Building RegScale threat from %s.", link[0])
                futures.append(
                    executor.submit(
                        build_threat,
                        app=app,
                        detailed_link=link[0],
                        short_description=link[1],
                        title=link[2],
                    )
                )
    wait(futures, return_when=ALL_COMPLETED)
    threats = [future.result() for future in futures if future.result()]
    # Log errors
    for error_ix in (ix for (ix, fut) in enumerate(futures) if not fut.result()):
        logger.warning("Unable to fetch: %s", control["links"][error_ix][0])
    return threats


def build_threat(app: Application, detailed_link: str, short_description: str, title: str) -> Threat:
    """
    Parse HTML from a given URL/link and build a RegScale threat.

    :param Application app: Application object
    :param str detailed_link: URL of the CISA threat
    :param str short_description: Description of the threat
    :param str title: Title for the threat
    :return: RegScale threat class
    :rtype: Threat
    """
    dat = parse_details(detailed_link)
    if not dat:
        return None

    date_created = dat[0]
    vulnerability = dat[1]
    mitigation = dat[2]
    notes = dat[3]

    return Threat(
        uuid=Threat.xstr(None),
        title=title,
        threatType="Specific",
        threatOwnerId=app.config["userId"],
        dateIdentified=date_created,
        targetType="Other",
        source="Open Source",
        description=short_description or f"""<p><a href="{detailed_link}" title="">{detailed_link}</a></p>""",
        vulnerabilityAnalysis="".join(vulnerability),
        mitigations="".join(mitigation),
        notes="".join(notes),
        dateCreated=date_created,
        status="Initial Report/Notification",
    )


def filter_elements(element: Tag) -> Optional[Tag]:
    """
    Filter elements

    :param Tag element: A BeautifulSoup Tag
    :return: The given tag if it is a Tag and has children
    :rtype: Optional[Tag]
    """
    filter_lst = [
        "c-figure__media",
        "c-product-survey__text-area",
        "l-full__footer",
        "usa-navbar",
    ]
    found = False
    if element.attrs.get("class"):
        found = any(item in element.attrs["class"] for item in filter_lst)
    if element.name in ("p", "li", "div", "table") and not found:
        return element
    return None


def process_params(
    element: Tag, nav_string: str, vulnerability: list, mitigation: list, notes: list
) -> Tuple[list, list, list]:
    """
    Process Parameters

    :param Tag element: A BeautifulSoup Tag
    :param str nav_string: A string to filter on
    :param list vulnerability: A list of vulnerabilities
    :param list mitigation: A list of mitigations
    :param list notes: A list of notes
    :return: Tuple[vulnerability, mitigation, notes]
    :rtype: Tuple[list, list, list]
    """
    # Filter out UL, seems to be duplicated with li tag.
    if filter_elements(element):
        content = str(element)
        if nav_string.lower() == "summary" and content not in notes:
            notes.append(content)
        if nav_string.lower() == "technical details" and content not in vulnerability:
            vulnerability.append(content)
        if nav_string.lower() == "mitigations" and content not in mitigation:
            mitigation.append(content)
    return vulnerability, mitigation, notes


def process_element(*args) -> Tuple[dict, str, str]:
    """
    Loop elements and determine last header, last_h3, and nav_string

    :return: Tuple[last_header, last_h3, nav_string]
    :rtype: Tuple[dict, str, str]
    """
    # Unpack tuple args
    (
        dat,
        last_header,
        last_h3,
        nav_string,
        div_list,
        vulnerability,
        mitigation,
        notes,
    ) = args[0]

    last_header = {"type": dat.name, "title": dat.text} if re.match(r"^h[1-6]$", dat.name) else last_header
    last_h3 = dat.text if dat.name == "h3" else last_h3
    if last_header and isinstance(dat, Tag) and dat.text.lower() in div_list:
        nav_string = dat.text.lower()
    if last_h3 and nav_string and dat.text.lower().replace("\n", "") not in div_list and last_h3.lower() in div_list:
        process_params(dat, nav_string, vulnerability, mitigation, notes)
    return last_header, last_h3, nav_string


def parse_details(link: str) -> Optional[Tuple[str, list, list, list]]:
    """
    Parse the details of a given link

    :param str link: A URL to parse
    :return: A tuple of date created, vulnerability, mitigation, and notes
    :rtype: Optional[Tuple[str, list, list, list]]
    """
    div_list = ["technical details", "mitigations", "summary", "executive summary"]
    vulnerability = []
    mitigation = []
    notes = []
    detailed_soup = gen_soup(link)
    if not (date_created := fuzzy_find_date(detailed_soup)):
        return None
    last_header = None
    last_h3 = None
    nav_string = ""

    for ele in detailed_soup.find_all("div", {"class": "l-full__main"}):
        for dat in ele.find_all():
            args = (
                dat,
                last_header,
                last_h3,
                nav_string,
                div_list,
                vulnerability,
                mitigation,
                notes,
            )
            last_header, last_h3, nav_string = process_element(args)

    if len(vulnerability) == 0:
        vulnerability.append(DEFAULT_STR)
    if len(notes) == 0:
        notes.append(DEFAULT_STR)
    if len(mitigation) == 0:
        mitigation.append(DEFAULT_STR)

    return date_created, unique(vulnerability), unique(mitigation), unique(notes)


def fuzzy_find_date(detailed_soup: BeautifulSoup, location: int = 2, attempts: int = 0) -> str:
    """
    Perform a fuzzy find to pull a date from a bs4 object

    :param BeautifulSoup detailed_soup: A BeautifulSoup object representing a webpage
    :param int location: The location of the date in the webpage, defaults to 2
    :param int attempts: Number of attempts to find a date, defaults to 0
    :return: An ISO-formatted datetime string
    :rtype: str
    """

    fuzzy_dt = None

    try:
        if matches := re.search(r"(Last Revised|Release Date)\s*(.*)", detailed_soup.text):
            fuzzy_dt = dparser.parse(matches.group(2), fuzzy=True).isoformat()
            return fuzzy_dt
        fuzzy_dt = dparser.parse(
            str(detailed_soup.find_all("div", {"class": "c-field__content"})[location].text)
            .strip("\n")
            .strip()
            .split("|", maxsplit=1)[0]
            .strip(),
            fuzzy=True,
        ).isoformat()
    except dparser.ParserError as pex:
        logger.error("Error Processing Alert date created: %s.", pex)
    if not fuzzy_dt and attempts < 5:
        fuzzy_dt = fuzzy_find_date(detailed_soup, location + 1, attempts + 1)
    if not fuzzy_dt and attempts >= 5:
        logger.error("Unable to find date created in CISA alert.")
    return fuzzy_dt


def gen_soup(url: Union[str, Tuple[str, ...]]) -> BeautifulSoup:
    """
    Generate a BeautifulSoup instance for the given URL

    :param str url: URL string
    :raises: URLError if URL is invalid
    :rtype: BeautifulSoup
    """
    if isinstance(url, tuple):
        url = url[0]
    if is_url(url):
        req = Api().get(url)
        req.raise_for_status()
        content = req.content
        return BeautifulSoup(content, "html.parser")
    raise URLError("URL is invalid, exiting...")


def _load_from_package() -> dict:
    """
    Load the cisa_kev_data.json from the RegScale CLI package

    :return: The cisa_kev_data.json
    :rtype: dict
    """
    import json
    import importlib.resources as pkg_resources

    # check if the filepath exists before trying to open it
    with pkg_resources.open_text("regscale.models.integration_models", "cisa_kev_data.json") as file:
        data = json.load(file)
    return data


def pull_cisa_kev() -> Dict[Any, Any]:
    """
    Pull the latest Known Exploited Vulnerabilities (KEV) data from CISA

    :return: Dictionary of known vulnerabilities via API
    :rtype: Dict[Any, Any]
    """
    # Use module-level variable for caching
    if not hasattr(pull_cisa_kev, "_cached_data"):
        app = Application()
        api = Api()
        config = app.config
        result = []

        # Get URL from config or use default
        if "cisaKev" in config:
            cisa_url = config["cisaKev"]
        else:
            cisa_url = CISA_KEV_URL
            config["cisaKev"] = cisa_url
            app.save_config(config)

        try:
            response = api.get(url=cisa_url, headers={}, retry_login=False)
            if not response:
                logger.error("Failed to get response from %s\nUsing KEV data from RegScale CLI package.", cisa_url)
                data = _load_from_package()
                pull_cisa_kev._cached_data = data
                return data
            response.raise_for_status()
            result = response.json()

            # Cache the result
            pull_cisa_kev._cached_data = result

        except exceptions.RequestException as ex:
            # Whoops it wasn't a 200
            logger.error("Error retrieving CISA KEV data: %s.\nUsing KEV data from RegScale CLI package.", str(ex))
            data = _load_from_package()
            pull_cisa_kev._cached_data = data
            return data

    return pull_cisa_kev._cached_data


def convert_date_string(date_str: str) -> str:
    """
    Convert the given date string for use in RegScale

    :param str date_str: date as a string
    :return: RegScale accepted datetime string format
    :rtype: str
    """
    fmt = "%Y-%m-%d"
    result_dt = datetime.strptime(date_str, fmt)  # 2022-11-03 to 2022-08-23T03:00:39.925Z
    return f"{result_dt.isoformat()}.000Z"


def update_regscale(data: dict) -> None:
    """
    Update RegScale threats with the latest Known Exploited Vulnerabilities (KEV) data

    :param dict data: Threat data from CISA
    :rtype: None
    """
    app = Application()
    api = Api()
    reg_threats = Threat.fetch_all_threats()
    unique_threats = {reg.description for reg in reg_threats}
    matching_threats = [d for d in data["vulnerabilities"] if d["vulnerabilityName"] in unique_threats]
    threats_inserted = []
    threats_updated = []
    new_threats = [dat for dat in data["vulnerabilities"] if dat not in matching_threats]
    console.print(f"Found {len(new_threats)} new threats from CISA")
    if new_threats:
        for rec in new_threats:
            threat = Threat(
                uuid=Threat.xstr(None),
                title=rec["cveID"],
                threatType="Specific",
                threatOwnerId=app.config["userId"],
                dateIdentified=convert_date_string(rec["dateAdded"]),
                targetType="Other",
                source="Open Source",
                description=rec["vulnerabilityName"],
                vulnerabilityAnalysis=rec["shortDescription"],
                mitigations=rec["requiredAction"],
                notes=rec["notes"].strip() + " Due Date: " + rec["dueDate"],
                dateCreated=(datetime.now()).isoformat(),
                status="Initial Report/Notification",
            )
            threats_inserted.append(threat.dict())
    update_threats = [dat for dat in data["vulnerabilities"] if dat in matching_threats]
    if len(matching_threats) > 0:
        for rec in update_threats:
            update_vuln = Threat(
                uuid=Threat.xstr(None),
                title=rec["cveID"],
                threatType="Specific",
                threatOwnerId=app.config["userId"],
                dateIdentified=convert_date_string(rec["dateAdded"]),
                targetType="Other",
                description=rec["vulnerabilityName"],
                vulnerabilityAnalysis=rec["shortDescription"],
                mitigations=rec["requiredAction"],
                dateCreated=convert_date_string(rec["dateAdded"]),
            ).dict()
            old_vuln = [threat.dict() for threat in reg_threats if threat.description == update_vuln["description"]][0]
            update_vuln = merge_old(update_vuln=update_vuln, old_vuln=old_vuln)
            if old_vuln:
                threats_updated.append(update_vuln)
    if len(threats_inserted) > 0:
        logging.getLogger("urllib3").propagate = False
        # Update Matching Threats
        logger.info("Inserting %i threats to RegScale...", len(threats_inserted))
        Threat.bulk_insert(api, threats_inserted)
    update_regscale_threats(json_list=threats_updated)


def merge_old(update_vuln: dict, old_vuln: dict) -> dict:
    """
    Merge dictionaries of old and updated vulnerabilities

    :param dict update_vuln: An updated vulnerability dictionary
    :param dict old_vuln: An old vulnerability dictionary
    :return: A merged vulnerability dictionary
    :rtype: dict
    """
    fields_to_preserve = [
        "id",
        "uuid",
        "status",
        "source",
        "threatType",
        "threatOwnerId",
        "notes",
        "targetType",
        "dateCreated",
        "isPublic",
        "investigated",
        "investigationResults",
    ]
    merged = update_vuln.copy()

    # Preserve specified fields from old dictionary if they exist
    for field in fields_to_preserve:
        if field in old_vuln:
            merged[field] = old_vuln[field]

    return merged


def insert_or_upd_threat(threat: dict, app: Application, threat_id: int = None) -> requests.Response:
    """
    Insert or update the given threats in RegScale

    :param dict threat: RegScale threat
    :param Application app: Application object
    :param int threat_id: RegScale ID of the threat, defaults to none
    :return: An API response based on the PUT or POST action
    :rtype: requests.Response
    """
    api = Api()
    config = app.config
    url_threats = config["domain"] + THREATS_SUFFIX
    headers = {"Accept": "application/json", "Authorization": config["token"]}
    return (
        api.put(url=f"{url_threats}/{threat_id}", headers=headers, json=threat)
        if threat_id
        else api.post(url=url_threats, headers=headers, json=threat)
    )


def update_regscale_threats(
    json_list: Optional[list] = None,
) -> None:
    """
    Update the given threats in RegScale via concurrent POST or PUT of multiple objects

    :param Optional[list] json_list: list of threats to be updated, defaults to None
    :rtype: None
    """
    if json_list and len(json_list) > 0:
        logger.info("Updating %i threats to RegScale...", len(json_list))
        Threat.bulk_update(None, json_list)


def unique(lst: List[str]) -> List[str]:
    """
    Make a list unique, but don't change the order

    :param List[str] lst: List to make unique
    :return: List with unique values
    :rtype: List[str]
    """
    unique_list = []
    seen = set()
    for item in lst:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list


def is_url(url: str) -> bool:
    """
    Determines if the given string is a URL

    :param str url: A candidate URL string
    :return: Whether the given string is a valid URL
    :rtype: bool
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
