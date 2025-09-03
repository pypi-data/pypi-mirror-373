"""Wiz Authentication Module"""

from typing import Optional

import requests

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    error_and_exit,
    check_license,
)
from regscale.integrations.commercial.wizv2.variables import WizVariables

logger = create_logger()
AUTH0_URLS = [
    "https://auth.wiz.io/oauth/token",
    "https://auth0.gov.wiz.io/oauth/token",
    "https://auth0.test.wiz.io/oauth/token",
    "https://auth0.demo.wiz.io/oauth/token",
    "https://auth.gov.wiz.io/oauth/token",
]
COGNITO_URLS = [
    "https://auth.app.wiz.io/oauth/token",
    "https://auth.test.wiz.io/oauth/token",
    "https://auth.demo.wiz.io/oauth/token",
    "https://auth.app.wiz.us/oauth/token",
]


def wiz_authenticate(client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Optional[str]:
    """
    Authenticate to Wiz

    :param Optional[str] client_id: Wiz client ID, defaults to None
    :param Optional[str] client_secret: Wiz client secret, defaults to None
    :raises ValueError: No Wiz Client ID provided in system environment or CLI command
    :return: token
    :rtype: Optional[str]
    """
    app = check_license()
    api = Api()
    # Login with service account to retrieve a 24hr access token that updates YAML file
    logger.info("Authenticating - Loading configuration from init.yaml file")

    # load the config from YAML
    config = app.config

    # get secrets
    client_id = WizVariables.wizClientId if client_id is None else client_id
    if not client_id:
        error_and_exit("No Wiz Client ID provided in system environment or CLI command.")
    client_secret = WizVariables.wizClientSecret if client_secret is None else client_secret
    if not client_secret:
        error_and_exit("No Wiz Client Secret provided in system environment or CLI command.")
    wiz_auth_url = config.get("wizAuthUrl")
    if not wiz_auth_url:
        error_and_exit("No Wiz Authentication URL provided in the init.yaml file.")

    # login and get token
    logger.info("Attempting to retrieve OAuth token from Wiz.io.")
    token, scope = get_token(
        api=api,
        client_id=client_id,
        client_secret=client_secret,
        token_url=wiz_auth_url,
    )

    # assign values

    config["wizAccessToken"] = token
    config["wizScope"] = scope

    # write our the result to YAML
    # write the changes back to file
    app.save_config(config)
    return token


def get_token(api: Api, client_id: str, client_secret: str, token_url: str) -> tuple[str, str]:
    """
    Return Wiz.io token

    :param Api api: api instance
    :param str client_id: Wiz client ID
    :param str client_secret: Wiz client secret
    :param str token_url: token url
    :return: tuple of token and scope
    :rtype: tuple[str, str]
    """
    app = api.app
    config = api.config
    status_code = 500
    logger.info("Getting a token")
    response = api.post(
        url=token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data=generate_authentication_params(client_id, client_secret, token_url),
    )
    if response.ok:
        status_code = 200
    logger.info(response.reason)
    # If response is unauthorized, try the first cognito url
    if response.status_code == requests.codes.unauthorized:
        try:
            response = api.post(
                url=COGNITO_URLS[0],
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                json=None,
                data=generate_authentication_params(client_id, client_secret, COGNITO_URLS[0]),
            )
            if response.ok:
                status_code = 200
                logger.info(
                    "Successfully authenticated using the authorization url: %s, now updating init.yaml..",
                    COGNITO_URLS[0],
                )
                config["wizAuthUrl"] = COGNITO_URLS[0]
                app.save_config(config)
        except requests.RequestException:
            error_and_exit(f"Wiz Authentication: {response.reason}")
    if status_code != requests.codes.ok:
        error_and_exit(f"Error authenticating to Wiz [{response.status_code}] - {response.text}")
    response_json = response.json()
    token = response_json.get("access_token")
    scope = response_json.get("scope")
    if not token:
        error_and_exit(f'Could not retrieve token from Wiz: {response_json.get("message")}')
    logger.info("SUCCESS: Wiz.io access token successfully retrieved.")
    return token, scope


def generate_authentication_params(client_id: str, client_secret: str, token_url: str) -> dict:
    """
    Create the Correct Parameter format based on URL

    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param str token_url: Wiz URL
    :raises Exception: A generic exception if token_url provided is invalid
    :return: Dictionary containing authentication parameters
    :rtype: dict
    """
    if token_url in AUTH0_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "beyond-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    if token_url in COGNITO_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    raise ValueError("Invalid Token URL")
