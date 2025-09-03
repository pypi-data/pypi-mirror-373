"""Provide low-level, basic login."""

import json
import logging
from os import getenv
from typing import Optional, Tuple
from urllib.parse import urljoin

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import error_and_exit

logger = logging.getLogger("regscale")


def get_regscale_token(
    api: Api,
    username: str = getenv("REGSCALE_USER"),
    password: str = getenv("REGSCALE_PASSWORD"),
    domain: str = getenv("REGSCALE_DOMAIN"),
    mfa_token: Optional[str] = "",
) -> Tuple[str, str]:
    """
    Authenticate with RegScale and return a token

    :param Api api: API Object to use for authentication
    :param str username: a string defaulting to the envar REGSCALE_USERNAME
    :param str password: a string defaulting to the envar REGSCALE_PASSWORD
    :param str domain: a string representing the RegScale domain, checks environment REGSCALE_DOMAIN
    :param Optional[str] mfa_token: MFA token to login with
    :raises EnvironmentError: if domain is not passed or retrieved
    :return: a tuple of user_id and auth_token
    :rtype: Tuple[str, str]
    """
    if domain is None:
        raise EnvironmentError("REGSCALE_DOMAIN must be set if not passed as parameter.")
    if username is None:
        raise EnvironmentError("REGSCALE_USERNAME must be set if not passed as parameter.")
    if password is None:
        raise EnvironmentError("REGSCALE_PASSWORD must be set if not passed as parameter.")

    auth = {  # TODO - HTTP Basic Auth an minimum
        "userName": username,
        "password": password,
        "oldPassword": "",
        "mfaToken": mfa_token,
    }
    logger.info("Logging into: %s", domain)
    # suggest structuring the login paths so that they all exist in one place
    url = urljoin(domain, "/api/authentication/login")
    response = api.post(url=url, json=auth, headers={})
    error_msg = "Unable to authenticate with RegScale. Please check your credentials."
    if response is None:
        logger.error("No response received from api.post(). Possible connection issue or internal error.")
        error_and_exit(error_msg + " (No response received from server)")
    logger.info(response.url)
    if response.status_code == 200:
        response_dict = response.json()
    elif response.status_code == 403:
        error_and_exit(error_msg)
    elif response.status_code == 400 and mfa_token == "":
        error_and_exit(error_msg[:-1] + " and/or if an MFA token is required.")
    else:
        error_and_exit(f"{error_msg}\n{response.status_code}: {response.text}")
    if isinstance(response_dict, str):
        response_dict = json.loads(response_dict)
    return response_dict["id"], response_dict["auth_token"]
