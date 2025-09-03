#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync GCP Authentication and Checks"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.cloud import securitycenter
    from google.cloud import asset_v1

import logging
import os

from regscale.core.app.utils.app_utils import error_and_exit
from regscale.integrations.commercial.gcp.variables import GcpVariables

logger = logging.getLogger(__name__)


def ensure_gcp_credentials() -> None:
    """
    Ensures that the GCP credentials are set in the environment

    :rtype: None
    """
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GcpVariables.gcpCredentials


def ensure_gcp_api_enabled(service_name: str) -> None:
    """
    Ensures that the Security Center API is enabled
    Checks if the API is enabled and raises an exception or prints a message if it is not

    :param str service_name: The name of the service to check
    :raises RuntimeError: If the API is not enabled or any other error occurs
    :rtype: None
    """
    from google.auth.exceptions import GoogleAuthError  # Optimize import performance
    from googleapiclient.discovery import build  # Optimize import performance

    ensure_gcp_credentials()  # Assuming this function sets up authentication
    project_id = GcpVariables.gcpProjectId

    try:
        service = build("serviceusage", "v1")
        request = service.services().get(name=f"projects/{project_id}/services/{service_name}")
        response = request.execute()

        if response and response.get("state") == "ENABLED":
            logger.info(f"{service_name} api is enabled for project {project_id}.")
        else:
            error_and_exit(
                f"{service_name} api is not enabled for project {project_id}. Please enable it.\n"
                f"Run the following command:\n"
                f"gcloud services enable {service_name} --project {project_id}"
            )
    except GoogleAuthError as e:
        raise RuntimeError(f"Authentication error: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")


def ensure_security_center_api_enabled() -> None:
    """
    Ensures that the Security Center API is enabled

    :rtype: None
    """
    ensure_gcp_credentials()
    os.system(f"gcloud services enable securitycenter.googleapis.com --project {GcpVariables.gcpProjectId}")


def get_gcp_security_center_client() -> "securitycenter.SecurityCenterClient":
    """
    Gets the GCP Security Center client

    :return: The GCP client
    :rtype: securitycenter.SecurityCenterClient
    """
    from google.cloud import securitycenter  # Optimize import performance

    ensure_gcp_api_enabled("securitycenter.googleapis.com")
    return securitycenter.SecurityCenterClient()


def get_gcp_asset_service_client() -> "asset_v1.AssetServiceClient":
    """
    Gets the GCP Asset Service client

    :return: The GCP client
    :rtype: asset_v1.AssetServiceClient
    """
    from google.cloud import asset_v1  # Optimize import performance

    ensure_gcp_api_enabled("cloudasset.googleapis.com")
    return asset_v1.AssetServiceClient()
