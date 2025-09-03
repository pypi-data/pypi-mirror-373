"""
This module contains functions for interacting with the NIST CPE API.
"""

from typing import List, Optional, Tuple, Dict
import requests
from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import error_and_exit

logger = create_logger()


def get_cpe_titles(search_str: str, lang: Optional[str] = "en", timeout: int = 30) -> List[str]:
    """
    Get CPE titles from NIST CPE API for a given search string

    :param str search_str: the search string to use
    :param Optional[str] lang: the language to use, default is "en"
    :param int timeout: the timeout to use, default is 30
    :return: a list of CPE titles
    :rtype: List[str]
    """
    try:
        api = Api()
        config = api.config
        api_key = config.get("nistCpeApiKey")
        if not api_key:
            error_and_exit("NIST CPE API key not found in config")
        headers = {"api_key": api_key}
        nist_api_url = f"https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString={search_str}"
        response = requests.get(nist_api_url, headers=headers, timeout=timeout)
        cpe_names = []
        if response and response.ok:
            raw = response.json()
            logger.debug(raw)
            if "products" in raw:
                for product in raw["products"]:
                    if "cpe" in product:
                        cpe = product.get("cpe")
                        names = [name.get("title") for name in cpe.get("titles") if name.get("lang") == lang]
                        cpe_names.extend(names)
            return cpe_names
    except requests.RequestException as ex:
        logger.warning(f"Unable to get CPE title at this time: {ex}")
    return []


def get_cpe_title_by_version(cpe_title_list: List[str], version: str, take_first: bool = False) -> Optional[str]:
    """
    Get CPE title from a list of CPE titles for a given version

    :param List[str] cpe_title_list: the list of CPE titles to use
    :param str version: the version to use
    :param bool take_first: whether to take the first title if no match is found, default is False
    :return: a CPE title
    :rtype: Optional[str]
    """
    for title in cpe_title_list:
        if version in title:
            return title
    return cpe_title_list[0] if take_first and len(cpe_title_list) > 0 else None


def get_cpe_title(cpe_name: str, version: str) -> Optional[str]:
    """
    Get CPE title from NIST CPE API for a given CPE name and version

    :param str cpe_name: the CPE name to use
    :param str version: the version to use
    :return: a CPE title
    :rtype: Optional[str]
    """
    try:
        cpe_title_list = get_cpe_titles(cpe_name)
        if cpe_title_list:
            return get_cpe_title_by_version(cpe_title_list, version)
        return None
    except requests.RequestException as ex:
        logger.error("Error getting CPE title: %s", ex)
        return None


def extract_search_term_from_22_cpe(cpe_string: str) -> Tuple[str, str]:
    """
    Extracts the search term from a CPE 2.2 string and removes version for search.

    :param str cpe_string: CPE string
    :return: Search term and version
    :rtype: Tuple[str, str]
    """
    cpe_info_dict = extract_product_name_and_version(cpe_string)
    return (
        build_search_term(
            cpe_info_dict.get("part"),
            cpe_info_dict.get("software_vendor"),
            cpe_info_dict.get("software_name"),
        ),
        cpe_info_dict.get("software_version"),
    )


def extract_product_name_and_version(cpe_string: str) -> Dict:
    """
    Extracts the product name and version from a CPE string.

    :param str cpe_string: CPE string
    :return: Dict containing part, vendor_name, product_name and version
    :rtype: Dict
    """
    # convert to version 2.3 if 2.2
    # TODO: Note this is an incomplete conversion as the additional properties
    # in the URI format (which is still supported in 2.3) are separated by
    # tildes (~) after the final colon. We should extend this to support them
    # at some point to be safe. Example from NISTIR7697 the 2.3 dictionary
    # specification:
    #
    # WFN:
    #     wfn:[part="o",vendor="microsoft",product="windows_vista",version="6\.0",
    #     update="sp1",edition=NA,language=NA,sw_edition="home_premium",
    #     target_sw=NA,target_hw="x64",other=NA]
    #
    # WFN bound to a URI:
    #     cpe:/o:microsoft:windows_vista:6.0:sp1:~-~home_premium~-~x64~-
    #
    # WFN bound to a formatted string:
    #     cpe:2.3:o:microsoft:windows_vista:6.0:sp1:-:-:home_premium:-:x64:-
    #
    if cpe_string.startswith("cpe:/"):
        cpe_string = cpe_string.replace("cpe:/", "cpe:2.3:")

    # Split the CPE string by ':'
    parts = cpe_string.split(":")

    # Extract the product name and version
    # parts[3] is the product name, parts[4] is the version
    part = parts[2] if len(parts) > 2 else None
    logger.debug(f"part: {part}")
    vendor_name = parts[3] if len(parts) > 3 else None
    product_name = parts[4] if len(parts) > 4 else None
    version = parts[5] if len(parts) > 5 else None
    cpe_info_dict = {
        "part": part,
        "software_vendor": vendor_name,
        "software_name": product_name,
        "software_version": version,
    }
    return cpe_info_dict


def build_search_term(part: str, vendor_name: str, product_name: str) -> str:
    """
    Build a search term for the NIST CPE API

    :param str part: the part to use
    :param str vendor_name: the vendor name to use
    :param str product_name: the product name to use
    :return: a search term
    :rtype: str
    """
    return f"cpe:2.3:{part}:{vendor_name}:{product_name}:"
