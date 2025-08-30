#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Azure Integrations"""
import os
import msal
from regscale.core.app.application import Application


def get_token(app: Application) -> str:
    """
    Fetch Azure AD Token

    :param Application app: The application
    :rtype: str
    """

    scope = ["https://graph.microsoft.com/.default"]
    try:
        azure_tenant_id = os.environ["AZURE_TENANT_ID"]
        client_id = os.environ["AZURE_CLIENT_ID"]
        client_secret = os.environ["AZURE_CLIENT_SECRET"]
    except KeyError:
        # Azure environment is not set, use init.yaml
        client_id = app.config["azureCloudClientId"]
        client_secret = app.config["azureCloudSecret"]
        azure_tenant_id = app.config["azureCloudTenantId"]
    authority = f"https://login.microsoftonline.com/{azure_tenant_id}"
    client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    token_result = client.acquire_token_for_client(scopes=scope)
    token = token_result["access_token"]

    return token
