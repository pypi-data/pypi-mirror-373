#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enables comparison of catalogs from the master catalog list and the user's RegScale instance"""
import json
import logging
import re
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def get_new_catalog(url: str) -> dict:
    """
    Function to download a catalog via API call

    :param str url: URL to download the catalog from
    :return: Catalog API response as a dictionary
    :rtype: dict
    """
    # make sure url is stripped
    url = url.strip()
    new_catalog = {}
    try:
        # call curl command to download the catalog
        response = requests.get(url, timeout=60)
        # parse into a dictionary
        new_catalog = response.json()
    except (requests.exceptions.MissingSchema, json.JSONDecodeError, requests.exceptions.RequestException) as ex:
        logger.error("Error: %s on Catalog URL: %s", ex, url)
    # return from the function
    return new_catalog


def is_valid_url(url: str) -> bool:
    """
    Function to validate URL

    :param str url: URL to validate
    :return: Whether the URL is valid
    :rtype: bool
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def dot_to_parentheses(input_string: str) -> str:
    """
    Converts dot-separated issue identifiers to parentheses format.

    :param str input_string: The string containing issue identifiers in dot-separated format.
    :return: A string with issue identifiers converted to parentheses format.
    :rtype: str
    """
    return re.sub(r"([A-Z]+-\d+)\.(\d+)", r"\1(\2)", input_string.upper())


def parentheses_to_dot(input_string: str) -> str:
    """
    Converts parentheses-separated issue identifiers back to dot format.

    :param str input_string: The string containing issue identifiers in parentheses format.
    :return: A string with issue identifiers converted back to dot format.
    :rtype: str
    """
    return re.sub(r"([A-Z]+-\d+)\((\d+)\)", r"\1.\2", input_string.upper()).lower()


def objective_to_control_dot(input_string: str) -> str:
    """
    Converts objective identifiers to control identifiers in dot format.

    :param str input_string: The string containing objective identifiers.
    :return: A string with objective identifiers converted to control identifiers in dot format.
    :rtype: str
    """
    # Convert the input string to lowercase
    input_string = input_string.lower()

    # Use regex to find the pattern and extract the desired part
    match = re.match(r"([a-z]+-\d+(\.\d+)?)", input_string)

    if match:
        return match.group(1)
    else:
        logger.error(f"Failed to convert objective to control: {input_string}")
        return input_string
