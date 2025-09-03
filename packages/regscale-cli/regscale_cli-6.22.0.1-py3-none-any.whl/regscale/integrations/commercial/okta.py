#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Okta integration"""

# standard python imports
import json
import time
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Tuple

import click
import jwcrypto.jwk as jwk
import python_jwt

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import is_valid
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    parse_url_for_pagination,
    remove_nested_dict,
    save_data_to,
)
from regscale.utils.threading.threadhandler import create_threads, thread_assignment
from regscale.models.app_models.click import file_types, save_output_to

LOGIN_ERROR = "Login Error: Invalid RegScale credentials. Please log in for a new token."
job_progress = create_progress_object()
logger = create_logger()
admin_users = []


#####################################################################################################
#
# Okta Core API Documentation: https://developer.okta.com/docs/reference/core-okta-api/
# Okta API Postman Collections: https://developer.okta.com/docs/reference/postman-collections/
#
#####################################################################################################


@click.group()
def okta():
    """Okta integration to pull Okta users via API."""


@okta.command()
@click.option(
    "--type",
    type=click.Choice(["SSWS", "Bearer"], case_sensitive=False),
    help="The type of authentication method to use for Okta API.",
    prompt="Choose SSWS or Bearer",
    required=True,
)
def authenticate(type: str):
    """
    Authenticate with Okta API by choosing SSWS or Bearer. SSWS is a security token created
    within Okta admin portal and Bearer token needs a private JWK from Okta Admin portal.
    """
    app = check_license()
    api = Api()
    authenticate_with_okta(app, api, type)


@okta.command(name="get_active_users")
@save_output_to()
@file_types([".csv", ".xlsx"])
def get_active_users(save_output_to: Path, file_type: str):
    """
    Get active users from Okta API and save them to a .csv or .xlsx file.
    """
    save_active_users_from_okta(save_output_to=save_output_to, file_type=file_type)


@okta.command(name="get_inactive_users")
@click.option(
    "--days",
    type=click.INT,
    help="The number of days to see if a user hasn't logged in since, default is 30.",
    default=30,
    required=True,
)
@save_output_to()
@file_types([".csv", ".xlsx"])
def get_inactive_users(days: int, save_output_to: Path, file_type: str):
    """
    Get users that haven't logged in X days from Okta API and save the output as a .csv or .xlsx file.
    """
    save_inactive_users_from_okta(days=days, save_output_to=save_output_to, file_type=file_type)


@okta.command(name="get_all_users")
@save_output_to()
@file_types([".csv", ".xlsx"])
def get_all_users(save_output_to: Path, file_type: str):
    """
    Get All users from Okta API and save the output to a .csv or .xlsx file.
    """
    save_all_users_from_okta(save_output_to=save_output_to, file_type=file_type)


@okta.command(name="get_new_users")
@click.option(
    "--days",
    type=click.INT,
    help="The number of days to see if a user has been added to Okta, default is 30",
    default=30,
    required=True,
)
@save_output_to()
@file_types([".csv", ".xlsx"])
def get_recent_users(days: int, save_output_to: Path, file_type: str):
    """
    Get users that were added to Okta in X days.
    """
    save_recently_added_users_from_okta(days=days, save_output_to=save_output_to, file_type=file_type)


@okta.command(name="get_admin_users")
@save_output_to()
@file_types([".csv", ".xlsx"])
def get_admin_users(save_output_to: Path, file_type: str) -> None:
    """
    Get all admin users from Okta API and save the output to .csv or .xlsx file.
    """
    save_admin_users_from_okta(save_output_to=save_output_to, file_type=file_type)


def save_active_users_from_okta(save_output_to: Path, file_type: str = ".csv") -> None:
    """
    Function to get active users from Okta via API and save them to a .csv or .xlsx file
    :param Path save_output_to: The path to save the output file to
    :param str file_type: The file type to save the output file as, default is .csv, options are .csv or .xlsx
    :rtype: None
    """
    if file_type.lower() not in [".csv", ".xlsx"]:
        error_and_exit("Invalid file type. Please choose .csv or .xlsx.")

    # Get Status of Client Application
    app = check_license()
    api = Api()

    # check if RegScale token is valid:
    if is_valid(app=app):
        # get the token type from init.yaml
        auth_type = app.config["oktaApiToken"].split(" ")

        # authenticate with Okta
        authenticate_with_okta(app, api, auth_type[0])

        # check file path exists, if not create it
        check_file_path(save_output_to)

        # start progress bar to let user know tasks are working
        with job_progress:
            logger.info("Fetching active users from Okta.")
            # add task for fetching users from Okta
            fetching_users = job_progress.add_task("[#f8b737]Fetching active users from Okta...", total=1)
            # fetch active users from Okta
            users = get_okta_data(
                api=api,
                url=f"{api.config['oktaUrl']}/api/v1/users",
                headers={
                    "Content-Type": 'application/json; okta-response="omitCredentials, omitCredentialsLinks"',
                    "Accept": "application/json",
                    "Authorization": api.config["oktaApiToken"],
                },
                params=(("filter", 'status eq "ACTIVE"'), ("limit", "200")),
                task=fetching_users,
            )
            # notify user of how many active users we found
            logger.info("Found %s active user(s).", len(users))

            check_and_save_data(
                data=users,
                file_name="okta_active_users",
                file_path=save_output_to,
                file_type=file_type,
                data_desc="active user(s)",
            )
    # Notify user the RegScale token needs to be updated
    else:
        error_and_exit(LOGIN_ERROR)


def save_inactive_users_from_okta(save_output_to: Path, file_type: str = ".csv", days: int = 30) -> None:
    """
    Function to get users that haven't logged in X days from Okta API
    and saves the output as a .csv or .xlsx file.
    :param Path save_output_to: The path to save the output file to
    :param str file_type: The file type to save the output file as, defaults to .csv, options are .csv or .xlsx
    :param int days: The number of days to check for inactive users
    :rtype: None
    """
    if file_type.lower() not in [".csv", ".xlsx"]:
        error_and_exit("Invalid file type. Please choose .csv or .xlsx.")

    # Get Status of Client Application
    app = check_license()
    api = Api()

    # check if RegScale token is valid:
    if is_valid(app=app):
        # get the token type from init.yaml
        auth_type = app.config["oktaApiToken"].split(" ")

        # authenticate with Okta
        authenticate_with_okta(app, api, auth_type[0])

        # use job_progress for live task progress
        with job_progress:
            # check file path exists, if not create it
            check_file_path(save_output_to)

            # calculate last login date criteria with days provided
            since_date = datetime.now() - timedelta(days=days)

            # get all users from Okta
            users = get_all_okta_users(api)

            # analyze the users
            inactive_users = analyze_okta_users(
                user_list=users,
                key="lastLogin",
                filter_value=since_date,
                user_type="inactive",
            )

            # check, clean and save the data from okta to provided save_output_to and file_type
            check_and_save_data(
                data=inactive_users,
                file_name="okta_inactive_users",
                file_path=save_output_to,
                file_type=file_type,
                data_desc="inactive user(s)",
            )
    # Notify user the RegScale token needs to be updated
    else:
        error_and_exit(LOGIN_ERROR)


def save_all_users_from_okta(save_output_to: Path, file_type: str = ".csv") -> None:
    """
    Function to get all users from Okta via API and saves the output to a .csv or .xlsx file
    :param Path save_output_to: The path to save the output file to
    :param str file_type: The file type to save the output file as, defaults to .csv, options are .csv or .xlsx
    :rtype: None
    """
    if file_type.lower() not in [".csv", ".xlsx"]:
        error_and_exit("Invalid file type. Please choose .csv or .xlsx.")

    # Get status of client application
    app = check_license()
    api = Api()

    # check if RegScale token is valid:
    if is_valid(app=app):
        # get the token type from init.yaml
        auth_type = app.config["oktaApiToken"].split(" ")

        # authenticate with Okta
        authenticate_with_okta(app, api, auth_type[0])

        # check file path exists, if not create it
        check_file_path(save_output_to)

        # get all users from Okta
        users = get_all_okta_users(api)

        # check, clean and save the data from okta to provided save_output_to and file_type
        check_and_save_data(
            data=users,
            file_name="okta_users",
            file_path=save_output_to,
            file_type=file_type,
            data_desc="Okta users",
        )
    # Notify user the RegScale token needs to be updated
    else:
        error_and_exit(LOGIN_ERROR)


def save_recently_added_users_from_okta(save_output_to: Path, file_type: str = ".csv", days: int = 30) -> None:
    """
    Function to download users added in the last X days from Okta via API, defaults to last 30 days
    and saves the output to a .csv or .xlsx file
    :param Path save_output_to: The path to save the output file to
    :param str file_type: The file type to save the output file as, .csv or .xlsx, defaults to .csv
    :param int days: The number of days to check for recently added users, defaults to 30
    :rtype: None
    """
    if file_type.lower() not in [".csv", ".xlsx"]:
        error_and_exit("Invalid file type. Please choose .csv or .xlsx.")
    # Get Status of Client Application
    app = check_license()
    api = Api()

    # check if RegScale token is valid:
    if is_valid(app=app):
        # get the token type from init.yaml
        auth_type = app.config["oktaApiToken"].split(" ")

        # authenticate with Okta
        authenticate_with_okta(app, api, auth_type[0])

        # use job_progress for live task progress
        with job_progress:
            # check file path exists, if not create it
            check_file_path(save_output_to)

            # calculate last login date criteria with days provided
            since_date = datetime.now() - timedelta(days=days)

            # get all users from Okta
            users = get_all_okta_users(api)

            # analyze the users
            created_users = analyze_okta_users(
                user_list=users,
                key="created",
                filter_value=since_date,
                user_type="new",
            )

            # check, clean and save the data from Okta to provided save_output_to and file_type
            check_and_save_data(
                data=created_users,
                file_name="okta_new_users",
                file_path=save_output_to,
                file_type=file_type,
                data_desc="new user(s)",
            )
    # Notify user the RegScale token needs to be updated
    else:
        error_and_exit(LOGIN_ERROR)


def save_admin_users_from_okta(save_output_to: Path, file_type: str = ".csv") -> None:
    """
    Function to get all admin users from Okta via API and save the output to .csv or .xlsx file
    :param Path save_output_to: The path to save the output file to
    :param str file_type: The file type to save the output file as, defaults to .csv, options are .csv or .xlsx
    :rtype: None
    """
    if file_type.lower() not in [".csv", ".xlsx"]:
        error_and_exit("Invalid file type. Please choose .csv or .xlsx.")

    # Get Status of Client Application
    app = check_license()
    api = Api()

    # check if RegScale token is valid:
    if is_valid(app=app):
        # get the token type from init.yaml
        auth_type = app.config["oktaApiToken"].split(" ")

        # authenticate with Okta
        authenticate_with_okta(app, api, auth_type[0])

        # use job_progress for live task progress
        with job_progress:
            # check file path exists, if not create it
            check_file_path(save_output_to)

            # get all users from Okta
            users = get_all_okta_users(api)

            # create task for fetching user roles
            fetch_user_roles = job_progress.add_task(
                f"[#ef5d23]Fetching user roles for {len(users)} user(s)...",
                total=len(users),
            )

            # create threads to get user roles for each user
            create_threads(
                process=get_user_roles,
                args=(api, users, fetch_user_roles),
                thread_count=len(users),
            )

            # check, clean and save the data from Okta to provided save_output_to and file_type
            check_and_save_data(
                data=admin_users,
                file_name="okta_admin_users",
                file_path=save_output_to,
                file_type=file_type,
                data_desc="admin user(s)",
            )
    # Notify user the RegScale token needs to be updated
    else:
        error_and_exit(LOGIN_ERROR)


def get_user_roles(args: Tuple, thread: int) -> None:
    """
    Function used by threads to get the roles for each Okta user
    :param Tuple args: args for the threads to use during the function
    :param int thread: Number of the current thread
    :rtype: None
    """
    # set up my args from the args tuple
    api, all_users, task = args

    # set the headers for the Okta API Call
    headers = {
        "Content-Type": 'application/json; okta-response="omitCredentials, omitCredentialsLinks"',
        "Accept": "application/json",
        "Authorization": api.config["oktaApiToken"],
    }

    # get the thread assignment for the current thread
    threads = thread_assignment(thread=thread, total_items=len(all_users))

    # fetch the roles from Okta to get all the user's roles
    for i in range(len(threads)):
        user = all_users[threads[i]]

        # get all the roles for the user
        user_roles = get_okta_data(
            api=api,
            task=task,
            url=f"{api.config['oktaUrl']}/api/v1/users/{user['id']}/roles",
            headers=headers,
        )
        roles = [role["label"] for role in user_roles]
        # add concatenated user roles to their entry in all_users
        user["roles"] = ", ".join(roles)

        # add user to global admin_user list if, admin is in their concatenated role list
        (admin_users.append(user) if any("admin" in val.lower() for val in roles) else None)

        # update the progress bar
        job_progress.update(task, advance=1)


def analyze_okta_users(user_list: list, key: str, filter_value: Any, user_type: str) -> list:
    """
    Function to analyze users with the provided key and value
    and returns users that match the criteria in a list
    :param list user_list: Initial list of Okta users before being filtered
    :param str key: Key to use to filter the Okta users
    :param Any filter_value: Value used to filter Okta users with provided key
    :param str user_type: Type of user we are filtering for, used for log outputs
    :return: List of filtered Okta users using provided key and value
    :rtype: list
    """
    logger.info("Analyzing %s Okta user(s).", len(user_list))
    # create list to store the users that match the provided criteria
    filtered_users = []

    # create task for analyzing user's data
    analyze_login = job_progress.add_task(f"[#ef5d23]Analyzing {len(user_list)} user(s) data...", total=len(user_list))
    # iterate through all users and check user's with the provided criteria
    for user in user_list:
        if data_filter := user[key]:
            # verify comparing filter_value date against a string
            if isinstance(filter_value, datetime) and isinstance(data_filter, str):
                # try to convert it
                try:
                    data_filter = datetime.strptime(data_filter, "%Y-%m-%dT%H:%M:%S.%fZ")
                # if an error is encountered, make it an old date
                except (TypeError, KeyError, AttributeError):
                    error_and_exit("Incorrect date format. Please follow this format: '%Y-%m-%dT%H:%M:%S.%fZ'")
                # compare the values as date objects instead of datetime objects
                # if the user_type provided is inactive, make sure the provided date
                # is between the correct date field and today
                compare_dates_and_user_type(user, filtered_users, filter_value, user_type, data_filter, datetime.now())
        elif data_filter is None:
            filtered_users.append(user)
        # update analyzing user task
        job_progress.update(analyze_login, advance=1)
    # notify user of how many inactive users we found
    logger.info("Found %s %s user(s) in Okta.", len(filtered_users), user_type)

    # return the users that match the provided criteria
    return filtered_users


def compare_dates_and_user_type(
    user: dict, filtered_users: list, filter_value: datetime, user_type: str, data_filter: Any, today: datetime
):
    """
    Function to determine if the user matches the provided criteria and adds them to the filtered_users list

    :param dict user: User to determine if they match the provided criteria
    :param list filtered_users: List of users that match the provided criteria
    :param datetime filter_value: Date to compare the user's date with
    :param str user_type: Type of user we are filtering for, used to determine the correct date logic
    :param Any data_filter: Date to compare the user's date with
    :param datetime today: Today's date
    """
    # compare the values as date objects instead of datetime objects
    # if the user_type provided is inactive, make sure the provided date
    # is between the correct date field and today
    if user_type == "inactive" and filter_value.date() >= data_filter.date() <= today.date():
        # add user to filtered users list
        filtered_users.append(user)
    elif user_type == "new" and filter_value.date() <= data_filter.date() <= today.date():
        # add user to filtered users list
        filtered_users.append(user)


def check_and_save_data(data: list, file_name: str, file_path: Path, file_type: str, data_desc: str) -> None:
    """
    Function to check data returned from Okta API and cleans the response data and will save it
    to the provided file_path as the provided file_type
    :param list data: Raw data returned from Okta API
    :param str file_name: Desired name of the output file
    :param Path file_path: Directory to save the cleaned data to
    :param str file_type: Desired file type to output the data to
    :param str data_desc: Description of the data, used in output and logs
    :rtype: None
    """
    logger.info("Starting to clean and format data from Okta.")

    # check Okta data has data
    if len(data) >= 1:
        # use job_progress for live task progress
        with job_progress:
            # generate file name with today's date
            file_name = f"{file_name}_{get_current_datetime('%m%d%Y')}"

            # create task for cleaning the data response from Okta
            clean_data_task = job_progress.add_task("[#21a5bb]Cleaning data from Okta...", total=1)
            # clean the data from Okta
            clean_data = clean_okta_output(data=data, skip_keys=["_links"])

            # update the task as complete
            job_progress.update(clean_data_task, advance=1)

            # create task for saving file
            saving_file_task = job_progress.add_task(
                f"[#0866b4]Saving {len(clean_data)} {data_desc} to {file_path}/{file_name}{file_type}...",
                total=1,
            )
            # save the output to the provided file_path
            save_data_to(
                file=Path(f"{file_path}/{file_name}{file_type}"),
                data=clean_data,
            )
            # mark saving_file_task as complete
            job_progress.update(saving_file_task, advance=1)
            logger.info(
                "Saved %s %s successfully to %s%s!",
                len(clean_data),
                data_desc,
                file_path,
                file_type,
            )
    else:
        logger.info("No %s to save to %s!", data_desc, file_path)


def get_all_okta_users(api: Api) -> list:
    """
    Function to get all Okta users using the Okta API

    :param Api api: API object
    :return: List of all Okta users
    :rtype: list
    """
    logger.info("Fetching all users from Okta.")
    # add task for fetching users from Okta
    fetching_users = job_progress.add_task("[#f8b737]Fetching all users from Okta...", total=1)

    # fetch active users from Okta
    users = get_okta_data(
        api=api,
        url=f"{api.config['oktaUrl']}/api/v1/users",
        headers={
            "Content-Type": 'application/json; okta-response="omitCredentials, omitCredentialsLinks"',
            "Accept": "application/json",
            "Authorization": api.config["oktaApiToken"],
        },
        task=fetching_users,
    )
    # notify user of how many active users we found
    logger.info("Found %s Okta user(s).", len(users))
    # return all users from Okta
    return users


def get_okta_data(api: Api, task: int, url: str, headers: dict, params: Tuple = None) -> list:
    """
    Function to use the Okta core API to get data, also handles pagination for Okta requests

    :param Api api: API object
    :param int task: task to update to show user live progress
    :param str url: URL to use while using Okta API
    :param dict headers: Headers for the Okta API call
    :param Tuple params: Parameters for Okta API call, defaults to None
    :return: List of data received from the API call to Okta
    :rtype: list
    """
    # get data from Okta with provided information
    okta_response = api.get(url=url, headers=headers, params=params)
    # check the response
    if okta_response.status_code == 403:
        error_and_exit(
            "RegScale CLI wasn't granted the necessary permissions for this action."
            + "Please verify permissions in Okta admin portal and try again."
        )
    elif okta_response.status_code != 200:
        error_and_exit(
            f"Received unexpected response from Okta API.\n{okta_response.status_code}: {okta_response.text}"
        )
    try:
        # try to read the response and convert it to a JSON object
        okta_data = okta_response.json()
    except JSONDecodeError as ex:
        # notify user if there was a json decode error from API response and exit
        error_and_exit(f"JSON decode error.\n{ex}")
    # check if pagination required to fetch all data
    response_links = okta_response.headers.get("link")
    if okta_response.status_code == 200 and "next" in response_links:
        # get the url for the next pagination
        url = parse_url_for_pagination(response_links)

        # get the next page of data
        okta_data.extend(get_okta_data(api=api, task=task, url=url, headers=headers))
    elif okta_response.status_code != 200:
        error_and_exit(
            f"Received unexpected response from Okta!\nReceived: {okta_response.status_code}\n{okta_response.text}"
        )
    # mark the provided task as complete
    job_progress.update(task, advance=1)

    # return the Okta data
    return okta_data


def clean_okta_output(data: list, skip_keys: list = None) -> dict:
    """
    Function to remove nested dictionaries and the provided skip_key of the
    list data from Okta API response and returns a clean dictionary without any nested dictionaries

    :param list data: List of raw data from Okta
    :param list skip_keys: List of Keys to skip while cleaning the raw data
    :return: Dictionary of clean Okta data
    :rtype: dict
    """
    logger.info("Cleaning Okta data.")
    logger.debug("\nRaw data: %s\n", data)
    # create empty dictionary to store clean data
    clean_data = {}
    # iterate through each item in the provided list
    for row in data:
        # get a row of data with nested dictionaries as key value pairs
        # while also remove the _links nested dictionary
        new_row_data = remove_nested_dict(data=row, skip_keys=skip_keys)
        # iterate through the original data of nested dicts and remove them
        # from our clean data
        for item in reversed(row):
            # check if the item is a nested dictionary and exists in our clean data
            if isinstance(row[item], dict) and item in new_row_data:
                # remove the nested dictionary from the clean data
                del new_row_data[item]
        # update the old data with the new data
        clean_data[data.index(row)] = new_row_data
    logger.info("Okta data has been cleaned successfully.")
    logger.debug("\nClean data: %s\n", clean_data)
    # return the clean data set without nested dictionaries
    return clean_data


def authenticate_with_okta(app: Application, api: Api, type: str) -> None:
    """
    Function to authenticate with Okta via API and the provided method in type

    :param Application app: Application object
    :param Api api: API object
    :param str type: type of authentication for the Okta API
    :rtype: None
    """
    config = app.config
    if type.lower() == "ssws":
        # verify the provided SSWS token from init.yaml
        verify_response = api.get(
            url=f"{config['oktaUrl']}/api/v1/users",
            headers={
                "Content-Type": 'application/json; okta-response="omitCredentials, omitCredentialsLinks"',
                "Accept": "application/json",
                "Authorization": config["oktaApiToken"],
            },
        )
        if verify_response.ok:
            logger.info("Okta SSWS Token has been verified.")
        else:
            error_and_exit(
                "Please verify SSWS Token from Okta is entered correctly in init.yaml, "
                + "and it has okta.users.read & okta.roles.read permissions granted and try again."
            )
    elif type.lower() == "bearer":
        # check if secret key is in the init.yaml config
        key = config.get("oktaSecretKey")

        # if it exists try to get a bearer token from Okta API
        if key:
            token = get_okta_token(config=config, api=api, app=app)
            logger.info("New Okta Token: %s", token)
        else:
            # create the init.yaml entry for the oktaSecretKey and prompt user to get it from admin portal
            config["oktaSecretKey"] = {
                "d": "get from Okta",
                "p": "get from Okta",
                "q": "get from Okta",
                "dp": "get from Okta",
                "dq": "get from Okta",
                "qi": "get from Okta",
                "kty": "get from Okta",
                "e": "get from Okta",
                "kid": "get from Okta",
                "n": "get from Okta",
            }
            config["oktaScopes"] = "okta.users.read okta.roles.read"
            app.save_config(config)
            logger.info(
                "Please enter the private key for the application created in Okta admin"
                + "portal into init.yaml file and try again."
            )
    else:
        error_and_exit(
            "Please enter a valid authentication type for Okta API and try again. Please choose from SSWS or Bearer."
        )


def get_okta_token(config: dict, api: Api, app: Application) -> str:
    """
    Function to create a JWT to get a bearer token from Okta via API

    :param dict config: Application configuration (init.yaml)
    :param Api api: API object
    :param Application app: Application object
    :return: JWT token for future requests
    :rtype: str
    """
    okta_token = ""

    # get the Okta private JWK
    jwk_token = jwk.JWK.from_json(json.dumps(config["oktaSecretKey"]))

    # get the url from config without any trailing /
    url = config["oktaUrl"].strip("/") + "/oauth2/v1/token"

    # set the payload for the to be signed JWT while setting the signed JWT to expire in 10 minutes
    payload_data = {
        "aud": url,
        "iss": config["oktaClientId"],
        "sub": config["oktaClientId"],
        "exp": int(time.time()) + 600,
    }

    # create a signed JWT
    token = python_jwt.generate_jwt(payload_data, jwk_token, "RS256", timedelta(minutes=5))

    # set the headers for the API call
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # set up the data to the expected format for Okta API call
    payload = (
        f'grant_type=client_credentials&scope={config["oktaScopes"]}&client_assertion_type='
        + f"urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion={token}"
    )

    # post the data to get a bearer token for future requests
    token_response = api.post(url=url, headers=headers, data=payload)

    # see if the API call was successful
    if token_response.status_code == 200:
        try:
            # convert response to a JSON object
            token = token_response.json()

            # format the bearer token returned
            okta_token = f'{token["token_type"]} {token["access_token"]}'

            # update the config with the newly received JWT
            config["oktaApiToken"] = okta_token

            # save it to init.yaml
            app.save_config(config)
        except JSONDecodeError:
            # unable to convert the API response to a json object
            error_and_exit("Unable to retrieve data from Okta API.")
    else:
        error_and_exit(
            f"Received unexpected response from Okta API.\n{token_response.status_code}: {token_response.text}\n{token}"
        )
    return okta_token
