#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AlienVault OTX RegScale integration"""

import re
import time
from datetime import date, datetime
from typing import Generator

import click

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models import Threat

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

#####################################################################################################
#
# AlienVault API Documentation: https://otx.alienvault.com/api/
#
#####################################################################################################

SERVER = "https://otx.alienvault.com"
API_V1_ROOT = f"{SERVER}/api/v1"
SUBSCRIBED = f"{API_V1_ROOT}/pulses/subscribed"


@click.group()
def alienvault():
    """AlienVault OTX Integration to load pulses to RegScale."""


@alienvault.command(name="ingest_pulses")
@click.option(
    "--modified_since",
    type=click.DateTime(),
    required=False,
    help="Enter a local datetime to pull all pulses identified after.",
)
@click.option(
    "--limit",
    type=click.IntRange(min=1, max=50, clamp=True),
    required=False,
    default=50,
    help="Items per request.",
)
def ingest_pulses(modified_since: click.DateTime, limit: click.INT):
    """
    [BETA] Sync RegScale threats with pulse data from AlienVault OTX.
    """
    pulses(modified_since, limit)


def create_url(url_path: str, **kwargs) -> str:
    """
    Turn a path into a valid fully formatted URL. Supports query parameter formatting as well.

    :param str url_path: Request path (i.e. "/search/pulses")
    :return: a formatted url (i.e. "/search/pulses")
    :rtype: str
    """
    uri = url_path.format(SERVER)
    uri = uri if uri.startswith("http") else SERVER.rstrip("/") + uri
    if kwargs:
        uri += f"?{urlencode(kwargs)}"

    return uri


def walkapi_iter(
    app: Application,
    api: Api,
    url: str,
    args: dict,
) -> Generator:
    """
    Walk OTX API and return results

    :param Application app: Application instance
    :param Api api: Api instance
    :param str url: OTX URL
    :param dict args: OTX API arguments
    :raise ValueError: if unable to log into AlienVault
    :yield Generator: A dictionary representing an AlienVault OTX threat.
    """
    next_page_url = create_url(url, **args)
    item_count = 0
    api.timeout = 30
    headers = {"X-OTX-API-KEY": app.config["otx"]}
    while next_page_url:
        data = []
        try:
            response = api.get(url=next_page_url, headers=headers)
            if response.json() == {"detail": "Authentication required"}:
                raise ValueError("Unable to log into AlienVault, please check your API key")

            if response.ok:
                data = response.json()
                count = data["count"]
                for el in data["results"]:
                    item_count += 1
                    if item_count % 100 == 0:
                        app.logger.info("Processing %i of %i", item_count, count)
                    yield el
        except UnboundLocalError as ex:
            app.logger.warning("Unable to Pull from API, trying again..\n%s", ex)
            time.sleep(2)
            continue

        next_page_url = data["next"]


def extract_id(descrip: str) -> str:
    """Match RegEx of Alienvault ID

    :param str descrip: A string with the AlienVault ID
    :return: A string from the regex match
    :rtype: str
    """
    pattern = r"(?<=AlienVault ID: ).*"
    return match[0] if (match := re.search(pattern, descrip)) else ""


def pulses(modified_since: click.DateTime, limit: click.INT = 50) -> None:
    """
    Process pulses

    :param click.DateTime modified_since: Local Datetime (Converted to ISO_format before GET), defaults to None
    :param click.INT limit: Result limit, defaults to 50
    :rtype: None
    """
    app = Application()
    api = Api()
    args = {"limit": limit}

    existing_threats = Threat.fetch_all_threats()
    today = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
    if modified_since is not None:
        if isinstance(modified_since, (datetime, date)):
            modified_since = modified_since.isoformat()
        args["modified_since"] = modified_since

    for result in walkapi_iter(app=app, api=api, url=SUBSCRIBED, args=args):
        references = result["references"] if "references" in result and result["references"] else ""
        threat = Threat(
            title=result["name"],
            targetType="Other",
            vulnerabilityAnalysis="",
            mitigations="",
            notes=", ".join(result["tags"]) + f" \n{references}" + f" \nAlienVault ID: {result['id']}",
            threatType="Specific",
            source="Open Source",
            threatOwnerId=app.config["userId"],
            status="Under Investigation",
            dateIdentified=result["created"],
            dateCreated=today,
            description=f"{result['description']}\n{SERVER}/pulse/{result['id']}",
        )
        app.logger.debug(threat.notes)
        alienvault_ids = {
            extract_id(thr.notes) for thr in existing_threats if threat.notes and len(extract_id(thr.notes)) > 0
        }
        if result["id"] not in alienvault_ids:
            threat.create(bulk=True)
    Threat.bulk_save()
