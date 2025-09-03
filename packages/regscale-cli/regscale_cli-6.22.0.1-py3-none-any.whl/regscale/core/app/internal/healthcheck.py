#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Healthcheck Status"""

# standard python imports
import sys
from json import JSONDecodeError
from urllib.parse import urljoin

from regscale.core.app.logz import create_logger

logger = create_logger()


def status() -> None:
    """
    Get Status of Client Application via RegScale API

    :raises: FileNotFoundError if init.yaml was unable to be loaded
    :raises: ValueError if domain in init.yaml is missing or null
    :raises: General Error if unable to retrieve health check from RegScale API
    :rtype: None
    """
    from regscale.core.app.api import Api
    from regscale.core.app.application import Application

    app = Application()
    api = Api()
    config = app.config

    if "domain" not in config or config["domain"] == "":
        raise ValueError("No domain set in the initialization file.")
    if "token" not in config or config["token"] == "":
        raise ValueError("The token has not been set in the initialization file.")

    url_login = urljoin(config["domain"], "health")
    response = api.get(url=url_login)

    if not response or not response.ok:
        logger.error("Unable to retrieve health check data from RegScale. Please check your domain value in init.yaml.")
        sys.exit(1)

    try:
        health_data = response.json()
    except JSONDecodeError:
        logger.error("Unable to decode health check data from RegScale.")
        sys.exit(1)

    status_loggers = {
        "Healthy": logger.info,
        "Degraded": logger.warning,
        "Unhealthy": logger.error,
    }

    reg_status = health_data.get("status", "Unknown")
    status_loggers.get(reg_status, logger.info)(f"System Status: {reg_status}")

    if "entries" not in health_data:
        logger.error("No data returned from system health check.")
        sys.exit(1)

    checks = health_data["entries"]
    for chk in checks:
        logger.info(f"System: {chk}, Status: " + checks[chk]["status"])

    return health_data
