#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrate Azure Active Directory in RegScale"""


# standard python imports
from json import JSONDecodeError
from pathlib import Path

import click

from regscale import __version__
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    error_and_exit,
    save_data_to,
)
from regscale.models.regscale_models.user import User

logger = create_logger()
new_users = []
remove_users = []

######################################################################################################
#
# Microsoft MSAL Documentation:
#   https://learn.microsoft.com/en-us/python/api/overview/azure/active-directory?view=azure-python
# Microsoft AD Github Repo:
#   https://github.com/AzureAD/microsoft-authentication-library-for-python
#
######################################################################################################


# Create group to handle Active Directory processing
@click.group()
def ad():
    """Performs directory and user synchronization functions with Azure Active Directory."""
    check_license()


@ad.command()
def authenticate():
    """Obtains an access token using the credentials provided."""
    # authenticate the user
    get_access_token()


# Get Active Directory groups
@ad.command(name="list_groups")
def list_groups():
    """Prints the lists of available RegScale groups the CLI can read."""
    # authenticate the user
    get_access_token()

    # list all groups
    list_ad_groups()


# Sync RegScale admins from Active Directory
@ad.command(name="sync_admins")
def sync_admins():
    """Syncs members of the RegScale-admins group and assigns roles."""
    # authenticate the user
    get_access_token()

    # set the Microsoft Graph Endpoint
    get_group("RegScale-admin")


# Sync RegScale general users from Active Directory
@ad.command(name="sync_general")
def sync_general():
    """Syncs members of the RegScale-general group and assigns roles."""
    # authenticate the user
    get_access_token()

    # set the Microsoft Graph Endpoint
    get_group("RegScale-general")


# Sync RegScale read only from Active Directory
@ad.command(name="sync_readonly")
def sync_readonly():
    """Syncs members of the RegScale-readonly group and assigns roles."""
    # authenticate the user
    get_access_token()

    # set the Microsoft Graph Endpoint
    get_group("RegScale-readonly")


# Supporting Functions
def get_access_token() -> dict:
    """
    Function to authenticate in Active Directory and updates init.yaml with the returned JWT

    :return: JWT from Azure Directory
    :rtype: dict
    """
    import msal
    from regscale.core.app.application import Application

    app = Application()

    # get the config from the application
    config = app.config

    # generate the endpoint
    auth_url = config["adAuthUrl"] + config["adTenantId"]
    graph_url = config["adGraphUrl"]
    version = __version__

    # configure the Microsoft MSAL library to authenticate and gain an access token
    ad_app = msal.ConfidentialClientApplication(
        client_id=config["adClientId"],
        app_name="RegScale CLI",
        app_version=version,
        authority=auth_url,
        client_credential=config["adClientSecret"],
    )

    # use MSAL to get the token (no caching for security)
    try:
        token = ad_app.acquire_token_for_client(scopes=graph_url)
        config["adAccessToken"] = "Bearer " + token["access_token"]

        # write the changes back to file
        app.save_config(config)
        logger.info("Azure AD Login Successful!")
        logger.info("Init.yaml file updated successfully with the access token.")
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to authenticate to Azure AD.\nError: {ex}")
    except KeyError as ex:
        error_and_exit(f"Unable to obtain access token! Please verify credentials.\nError: {ex}\n{token}")
    # return the result
    return token


def list_ad_groups() -> None:
    """
    Function that lists all RegScale groups in Active Directory

    :rtype: None
    """
    from regscale.core.app.api import Api
    from regscale.core.app.application import Application

    app = Application()
    api = Api()

    # load the config from YAML
    config = app.config

    # trim the URL
    graph_url = config["adGraphUrl"].replace(".default", "")

    # set the endpoint
    groups_url = f"{graph_url}v1.0/groups?$filter=startswith(displayName,'RegScale')"

    # configure the headers for the API call
    ad_headers = {"Authorization": config["adAccessToken"]}

    # get the AD group info
    logger.info("Fetching relevant AD Groups from Azure for RegScale.")
    try:
        groups_response = api.get(url=groups_url, headers=ad_headers)
        groups_data = groups_response.json()
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to retrieve group information from Azure Active Directory.\n{ex}")
    # loop through the groups and log the results
    if "value" in groups_data:
        for g in groups_data["value"]:
            logger.info("GROUP: " + g["displayName"])
        logger.info("%s total group(s) retrieved.", len(groups_data["value"]))
    elif "error" in groups_data:
        try:
            error_and_exit(f'{groups_data["error"]["code"]}: {groups_data["error"]["message"]}')
        except Exception as ex:
            error_and_exit(f"Unknown Error! {ex}\nData: {groups_data}")

    # verify artifacts directory exists
    check_file_path("artifacts")

    # save group data to a json file
    save_data_to(
        file=Path("./artifacts/RegScale-AD-groups.json"),
        data=groups_data,
    )


# retrieves the RegScale groups from Azure AD
# flake8: noqa: C901
def get_group(str_group: str) -> None:
    """
    Syncs members of the RegScale-admins group and assigns appropriate roles

    :param str str_group: RegScale user group
    :rtype: None
    """
    from regscale.core.app.api import Api
    from regscale.core.app.application import Application

    # initialize app and api
    app = Application()
    api = Api()

    # see if readonly
    b_read_only = True if str_group == "RegScale-readonly" else False

    # load the config from app
    config = app.config

    # trim the Graph URL
    str_graph_url = config["adGraphUrl"].replace(".default", "")

    # set the Microsoft Graph Endpoint
    if str_group == "RegScale-admin":
        groups_url = f"{str_graph_url}v1.0/groups?$filter=startswith(displayName,'RegScale-admin')"
    elif str_group == "RegScale-general":
        groups_url = f"{str_graph_url}v1.0/groups?$filter=startswith(displayName,'RegScale-general')"
    elif str_group == "RegScale-readonly":
        groups_url = f"{str_graph_url}v1.0/groups?$filter=startswith(displayName,'RegScale-readonly')"
    else:
        error_and_exit(f"Unknown RegScale group ({str_group}) requested for sync")

    # set up the headers for the api call
    ad_headers = {"Authorization": config["adAccessToken"]}

    # get the AD group info
    logger.info("Fetching relevant AD Groups from Azure for RegScale.")
    try:
        groups_response = api.get(groups_url, headers=ad_headers)
        groups_data = groups_response.json()
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to retrieve group information from Azure Active Directory.\n{ex}")
    # verify artifacts directory exists
    check_file_path("artifacts")

    # save group data to json file
    save_data_to(
        file=Path(f"./artifacts/adGroupList-{str_group}.json"),
        data=groups_data,
    )

    # loop through each group to find admins
    if len(groups_data) == 0:
        error_and_exit(f"{str_group} group has not been setup yet in Azure AD.")
    else:
        # get group info
        if "value" in groups_data:
            found_group = groups_data["value"][0]
            group_id = found_group["id"]
        else:
            # error handling (log error)
            if "error" in groups_data:
                try:
                    error_and_exit(f'{groups_data["error"]["code"]}: {groups_data["error"]["message"]}')
                except Exception as ex:
                    error_and_exit(f"Unknown Error! {ex}\nData: {groups_data}")

        # get AD group members
        members_url = f"{str_graph_url}v1.0/groups/{group_id}/members"

        # get the member list for the AD group
        logger.info("Fetching the list of members for this AD group - %s", str(group_id))
        try:
            member_response = api.get(members_url, headers=ad_headers)
            member_data = member_response.json()
        except JSONDecodeError:
            error_and_exit(f"Unable to retrieve member list for Azure Active Directory group - {group_id}.")
        # verify artifacts directory exists
        check_file_path("artifacts")

        # save member data to json file
        save_data_to(
            file=Path(f"./artifacts/adMemberList-{group_id}.json"),
            data=member_data,
        )
        logger.debug(member_data)
        # retrieve the list of RegScale users
        url_users = f'{config["domain"]}/api/accounts/getList'
        try:
            user_response = api.get(url_users)
            user_data = user_response.json()
        except JSONDecodeError:
            error_and_exit("Unable to retrieve user list from RegScale.")

        # retrieve the list of RegScale roles
        url_roles = f'{config["domain"]}/api/accounts/getRoles'
        try:
            role_response = api.get(url_roles)
            role_data = role_response.json()
        except JSONDecodeError:
            error_and_exit("Unable to retrieve roles from RegScale.")

        # loop through the members of the AD group (create new user if not in RegScale)
        for m in member_data["value"]:
            # see if it exists
            member_found = False
            for u in user_data:
                if "externalId" in u and m["id"] == u["externalId"]:
                    member_found = True

            # handle new user flow
            if not member_found:
                # create a new user
                new_user = User(
                    userName=m["userPrincipalName"],
                    email=m["mail"],
                    firstName=m["givenName"],
                    lastName=m["surname"],
                    workPhone=m["mobilePhone"],
                    activated=True,
                    jobTitle=m["jobTitle"],
                    tenantId=1,
                    ldapUser=True,
                    externalId=m["id"],
                    readOnly=b_read_only,
                )
                new_users.append(new_user.dict())
        # loop through the users (disable if not in AD group)
        for u in user_data:
            if "externalId" in u:
                disable_flag = True
                for m in member_data["value"]:
                    if m["id"] == u["externalId"]:
                        disable_flag = False
                if disable_flag:
                    remove_users.append(u)
        # write out new user list to file
        save_data_to(file=Path("./artifacts/newUsers.json"), data=new_users)

        # write out disabled user list to file
        save_data_to(file=Path("./artifacts/removeUsers.json"), data=remove_users)

        # Logging
        logger.info("%s new user(s) to process.", str(len(new_users)))

        # loop through each user
        regscale_new = []
        for us in new_users:
            # add new users in bulk
            url_new_users = f'{config["domain"]}/api/accounts/azureAD'
            try:
                new_user = api.post(url_new_users, json=us)
                user_new = {"id": new_user.text}
                regscale_new.append(user_new)
                logger.info("User created or updated: %s", us["userName"])
            except Exception as ex:
                error_and_exit(f"Unable to create new user {us['userName']}.\nError: {ex}")

        # write out new user list to file
        save_data_to(
            file=Path("./artifacts/newRegScaleUsers.json"),
            data=regscale_new,
        )

        # set the role
        user_role = ""
        if str_group == "RegScale-admin":
            user_role = "Administrator"
        elif str_group == "RegScale-general":
            user_role = "GeneralUser"
        elif str_group == "RegScale-readonly":
            user_role = "ReadOnly"

        # set the RegScale role based on the AD group
        regscale_role = None
        for role in role_data:
            if role["name"] == user_role:
                regscale_role = role
        if role is None:
            error_and_exit(f"Unable to locate RegScale role for group: {str_group}.")

        # loop through the users and assign roles
        int_roles = 0
        for us in regscale_new:
            # check the role
            url_check_role = f'{config["domain"]}/api/accounts/checkRole/{us["id"]}/{regscale_role["id"]}'
            try:
                role_check = api.get(url=url_check_role)
                str_check = role_check.text
            except Exception as ex:
                error_and_exit(f"Unable to check role: {us['id']}, {regscale_role['id']}.\nError: {ex}")

            # add the role
            if str_check == "false":
                # add the role
                url_assign_role = config["domain"] + "/api/accounts/assignRole/"
                # role assignment object
                assign = {"roleId": regscale_role["id"], "userId": us["id"]}
                try:
                    api.post(url=url_assign_role, json=assign)
                    int_roles += 1
                except Exception as ex:
                    error_and_exit(f"Unable to assign role: {us['id']}/{regscale_role['id']}.\nError: {ex}")

        # output results
        if int_roles > 0:
            logger.info("Total Roles Assigned: %s.", str(int_roles))

        # loop through and remove users
        int_removals = 0
        for us in remove_users:
            # check the role
            url_check_role = f'{config["domain"]}/api/accounts/checkRole/{us["id"]}/{regscale_role["id"]}'
            try:
                role_check = api.get(url=url_check_role)
                str_check = role_check.text
            except Exception as ex:
                error_and_exit(f"Unable to check role: {us['id']}/{regscale_role['id']}.\nError: {ex}")

            # add the role
            if str_check == "true":
                # remove the role
                url_remove_role = f'{config["domain"]}/api/accounts/deleteRole/{us["id"]}/{regscale_role["id"]}'
                try:
                    api.delete(url=url_remove_role)
                    int_removals += 1
                except Exception as ex:
                    error_and_exit(f"Unable to remove role: {us['id']}/{regscale_role['id']}.\nError: {ex}")

                # deactivate the user if they were in this role
                url_deactivate = f'{config["domain"]}/api/accounts/changeUserStatus/{us["id"]}/false'
                try:
                    api.get(url_deactivate)
                    logger.warning("%s account deactivated.", us["userName"])
                except Exception as ex:
                    error_and_exit(f"Unable to check role: {us['id']}/{regscale_role['id']}.\nError: {ex}")
        # output results
        logger.info(str(int_removals) + " users had roles removed and accounts disabled.")
