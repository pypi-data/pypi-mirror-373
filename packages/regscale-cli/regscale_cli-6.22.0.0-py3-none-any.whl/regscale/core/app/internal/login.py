#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to allow user to login to RegScale"""

# standard python imports
import base64
import contextlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from ssl import SSLCertVerificationError
from typing import Optional, TYPE_CHECKING
from urllib.parse import urljoin

if TYPE_CHECKING:
    from regscale.core.app.application import Application
    from regscale.core.app.api import Api

import requests

logger = logging.getLogger("regscale")


def login(
    str_user: Optional[str] = None,
    str_password: Optional[str] = None,
    host: Optional[str] = None,
    app: Optional["Application"] = None,
    token: Optional[str] = None,
    mfa_token: Optional[str] = "",
) -> str:
    """
    Wrapper for Login to RegScale

    :param Optional[str] str_user: username to log in, defaults to None
    :param Optional[str] str_password: password of provided user, defaults to None
    :param Optional[str] host: host to log into, defaults to None
    :param Optional[Application] app: Application object, defaults to None
    :param Optional[str] token: a valid JWT token to pass, defaults to None
    :param Optional[str] mfa_token: a valid MFA token to pass, defaults to ""
    :raises: ValueError if no domain value found in init.yaml
    :raises: TypeError if token or user id doesn't match expected data type
    :raises: SSLCertVerificationError if unable to validate SSL certificate
    :return: JWT Token after authentication
    :rtype: str
    """
    from regscale.models.platform import (
        RegScaleAuth,
    )  # Adding the import here, to avoid a circular import with RegScaleAuth.get_token.

    running_in_airflow = os.getenv("REGSCALE_AIRFLOW") == "true"
    from regscale.core.app.application import Application

    if not app and running_in_airflow:
        app = Application(
            config={
                "domain": host,
                "token": token,
            }
        )
    elif not app:
        app = Application()
    config = app.config
    # check to see if we are running in airflow
    if config and running_in_airflow:
        token = token or os.getenv("REGSCALE_TOKEN") or config.get("token")
        config["domain"] = (host if host and host != "None" else config.get("REGSCALE_DOMAIN")) or os.getenv(
            "REGSCALE_DOMAIN"
        )
        app.logger.debug("Running in Airflow, logging in with token: %s", token)
    else:
        config["domain"] = host or config["domain"]
    token = token or os.getenv("REGSCALE_TOKEN")
    if token is not None:
        token = token if token.startswith("Bearer ") else f"Bearer {token}"
    if config and token:
        try:
            if verify_token(app, token):
                config["userId"] = parse_user_id_from_jwt(app, token)
                config["token"] = token
                if not running_in_airflow:
                    logger.info("RegScale Token and userId has been saved in init.yaml")
                    app.save_config(conf=config)
                return token
            else:
                logger.error("Invalid token provided.")
                sys.exit(1)
        except AttributeError as e:
            logger.error("Unexpected error when verifying token: %s", e)
            sys.exit(1)
    from regscale.core.app.api import Api

    try:
        if str_user and str_password:
            if config and "REGSCALE_DOMAIN" not in os.environ and host is None:
                host = config["domain"]
            regscale_auth = RegScaleAuth.authenticate(
                api=Api(),
                username=str_user,
                password=str_password,
                domain=host,
                mfa_token=mfa_token,
            )
        else:
            regscale_auth = RegScaleAuth.authenticate(Api(), mfa_token=mfa_token)
        if config and config["domain"] is None:
            raise ValueError("No domain set in the init.yaml configuration file.")
        if config and config["domain"] == "":
            raise ValueError("The domain is blank in the init.yaml configuration file.")
    except TypeError as ex:
        logger.error("TypeError: %s", ex)
    except SSLCertVerificationError as sslex:
        logger.error("SSLError, python requests requires a valid ssl certificate.\n%s", sslex)
        sys.exit(1)

    # create object to authenticate
    auth = {
        "userName": regscale_auth.username,
        "password": regscale_auth.password.get_secret_value(),
        "oldPassword": "",
        "mfaToken": mfa_token,
    }
    if auth["password"]:
        # update init file from login
        if config:
            config["token"] = regscale_auth.token
            config["userId"] = regscale_auth.user_id
            config["domain"] = regscale_auth.domain
            # write the changes back to file
            app.save_config(config)
        # set variables
        logger.info("User ID: %s", regscale_auth.user_id)
        logger.info("New RegScale Token has been updated and saved in init.yaml")
        # Truncate token for logging purposes
        logger.debug("Token: %s", regscale_auth.token[:20])
    config["domain"] = host
    app.save_config(config)
    return regscale_auth.token


def is_valid(host: Optional[str] = None, app: Optional["Application"] = None) -> bool:
    """
    Quick endpoint to check login status

    :param Optional[str] host: host to verify login, defaults to None
    :param Optional[Application] app: Application object, defaults to None
    :return: Boolean if user is logged in or not
    :rtype: bool
    """
    from regscale.core.app.api import Api

    if not app:
        from regscale.core.app.application import Application

        app = Application()
    config = app.config
    login_status = False
    api = Api()
    token_body = {"accessToken": ""}
    try:
        # Make sure url isn't default
        # login with token
        token_body["accessToken"] = config["token"]
        app.logger.debug("config: %s", config)
        url_login = urljoin(host or config["domain"], "/api/authentication/validateToken")
        app.logger.debug("is_valid url: %s", url_login)
        app.logger.debug("token_body: %s", token_body)
        if response := api.post(url=url_login, headers={}, json=token_body):
            app.logger.debug("is_valid response: %s", response.status_code)
            login_status = response.status_code == 200
    except KeyError as ex:
        if str(ex).replace("'", "") == "token":
            app.logger.debug("Token is missing, we will generate this")
    except ConnectionError:
        app.logger.error("ConnectionError: Unable to login user to RegScale, check the server domain.")
    except json.JSONDecodeError as decode_ex:
        app.logger.error(
            "Login Error: Unable to login user to RegScale instance:  %s.\n%s",
            config["domain"],
            decode_ex,
        )
    finally:
        app.logger.debug("login status: %s", login_status)
    return login_status


def is_licensed(app: "Application") -> bool:
    """
    Verify if the application is licensed

    :param Application app: Application object
    :return: License status
    :rtype: bool
    """
    from regscale.core.app.api import Api

    api = Api()
    try:
        with contextlib.suppress(requests.RequestException):
            if res := app.get_regscale_license(api=api):
                lic = res.json()
            else:
                return False
            license_date = parse_date(lic["expirationDate"])
            if lic["licenseType"] == "Enterprise" and license_date > datetime.now():
                return True
    except (KeyError, ValueError, TypeError, AttributeError):
        return False
    return False


def verify_token(app: "Application", token: str) -> bool:
    """
    Function to verify if the provided JWT for RegScale is valid

    :param Application app: Application object
    :param str token: the JWT to verify
    :return: Boolean if the token is valid or not
    :rtype: bool
    """
    from regscale.core.app.api import Api

    api = Api()
    response = api.post(url=f"{app.config['domain']}/api/authentication/validateToken", json={"accessToken": token})
    return response.status_code == 200


def parse_user_id_from_jwt(app: "Application", jwt_token: str) -> str:
    """
    Decode JWT from RegScale to get the user id from the payload

    :param Application app: Application object
    :param str jwt_token: the JWT to decode
    :raises ValueError: if the JWT token is invalid
    :return: the user id
    :rtype: str
    """
    parts = jwt_token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format. Provided token is not a valid JWT token. Token: %s", jwt_token)

    payload = json.loads(_decode_base64(parts[1]).decode("utf-8"))
    if "id" not in payload:
        # iterate the payload to find the user id by using any uuid found and validating it
        for value in payload.values():
            try:
                if uuid.UUID(value) and validate_user_id(app, value):
                    return value
            except (ValueError, AttributeError):
                continue
    else:
        return payload["id"]
    app.logger.warning("No user id found in JWT token, please update userId manually in init.yaml.")
    return ""


def validate_user_id(app: "Application", user_id: str) -> bool:
    """
    Validate the user id provided by the user in RegScale

    :param Application app: Application object
    :param str user_id: User id to validate
    :return: Whether the provided user id is valid or not
    :rtype: bool
    """
    from regscale.core.app.api import Api

    api = Api()
    response = api.get(
        url=f"{app.config['domain']}/api/accounts/find/{user_id}",
    )
    return response.status_code == 200


def _decode_base64(data: str) -> bytes:
    """
    Decode base64, padding being optional

    :param str data: the data to decode
    :return: the decoded data
    :rtype: bytes
    """
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return base64.urlsafe_b64decode(data)


def parse_date(date_str: str) -> datetime:
    """
    Parse a date string in one of the supported formats

    :param str date_str: the date string to parse
    :raises ValueError: if unable to parse the provided date_str
    :return: the parsed date
    :rtype: datetime
    """
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date  # Return the parsed date as soon as parsing is successful
        except ValueError:
            continue  # Continue to the next format if parsing fails

    raise ValueError(
        f"Could not parse the date string {date_str} in any of the provided formats: {', '.join(formats)}."
    )
