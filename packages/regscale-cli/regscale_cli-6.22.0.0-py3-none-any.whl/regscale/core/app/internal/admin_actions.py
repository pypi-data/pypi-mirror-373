#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Email Reminders"""

# standard python imports
import re
from typing import Any, List

import click

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import check_license
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models import Email, User, regscale_id, regscale_module


@click.group(name="admin_actions")
def actions():
    """Performs administrative actions on the RegScale platform."""


@actions.command(name="update_compliance_history")
@regscale_id()
@regscale_module()
def update_compliance_history(regscale_id: int, regscale_module: str):
    """
    Update the daily compliance score for a given RegScale System Security Plan.
    """
    verify_provided_module(regscale_module)
    update_compliance(regscale_id, regscale_module)


@actions.command(name="send_reminders")
@click.option(
    "--days",
    type=click.INT,
    help="RegScale will look for Assessments, Tasks, Issues, Security Plans, "
    + "Data Calls, and Workflows using today + # of days entered. Default is 30 days.",
    default=30,
    show_default=True,
    required=True,
)
def send_reminders(days: int):
    """
    Get Assessments, Issues, Tasks, Data Calls, Security Plans, and Workflows
    for the users that have email notifications enabled, email comes
    from support@regscale.com.
    """
    from regscale.models.integration_models.send_reminders import SendReminders  # Optimize import performance

    SendReminders(check_license(), days).get_and_send_reminders()


def validate_email(ctx: click.Context, param: click.Option, value: Any) -> List[str]:
    """
    Validate the email address provided by the users

    :param click.Context ctx: Click Context
    :param click.Option param: Click option
    :param Any value: Email address or a list of addresses
    :rtype: List[str]
    :return: Validated email address or a list of addresses
    """

    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    def is_valid_email(email: str) -> bool:
        """
        Check if the email address is valid

        :param str email: Email address to validate
        :rtype: bool
        """
        return re.match(email_regex, email) is not None

    if isinstance(value, (tuple, list)):
        validated_emails = []
        for email in value:
            while not is_valid_email(email):
                click.echo(f"Incorrect email address given: {email}")
                email = click.prompt("Please enter a valid email address")
            validated_emails.append(email)
        return validated_emails
    else:
        while not is_valid_email(value):
            click.echo(f"Incorrect email address given: {value}")
            value = click.prompt("Please enter a valid email address")
        return [value]


@actions.command(name="user_report")
@click.option(
    "--email",
    type=click.STRING,
    multiple=True,
    help="Enter an email address, use multiple switches, i.e. --email to add more than one.",
    callback=validate_email,
)
@click.option(
    "--days",
    type=click.INT,
    help="Number of days to include in the report. Defaults to 30 if not specified.",
    default=30,
    show_default=True,
    required=False,
)
def user_report(email: List[str], days: int):
    """
    Generate an active user report for your RegScale instance, email comes from support@regscale.com
    """
    api = Api()
    eml = None
    if not email:
        manual_email = set()
        do_prompt = True
        while do_prompt:
            eml, do_prompt = prompt_email()
            manual_email.add(eml)
            if not do_prompt:
                continue
        email = validate_email(ctx=None, param=None, value=list(manual_email))

    api.logger.debug("Sending User report to %s", email)
    email = create_user_email(email, days)
    if email.send():
        api.logger.info("User report sent successfully.")
    else:
        api.logger.info("Unable to send User report.")


def prompt_email() -> tuple[str, bool]:
    """
    Prompt the user for an email address

    :return: Email address and a boolean flag to prompt again
    :rtype: tuple[str, bool]
    """
    email = click.prompt("Please enter an email address")
    ask_prompt = click.prompt("Do you want to add another email address? (y/n)")
    if ask_prompt.lower() == "y":
        do_prompt = True
    else:
        do_prompt = False
    return email, do_prompt


def create_user_email(email: Any, days: int) -> Email:
    """
    Create an email payload for the user report

    :param Any email: RegScale parent ID
    :param int days: RegScale parent module

    :return: Email regscale model
    :rtype: Email
    """
    from datetime import datetime
    from html import escape

    from dateutil.parser import parse

    from regscale.core.app.utils.app_utils import get_css

    config = Application().config
    users = User.get_all()
    tables: str = (
        "<table><tr><th>Username</th><th>First Name</th><th>Last Name<th>Last Login</th></th><th>User Email</th></tr>"
    )
    for user in users:
        try:
            last_login = parse(user.lastLogin)
        except TypeError:
            # NoneType login
            continue
        difference = (datetime.now() - last_login).days
        if difference <= days:
            last_login_str = last_login.strftime("%Y-%m-%d %H:%M:%S")
            rec: str = (
                f"<tr><th>{escape(user.userName)}</th><th>{escape(user.firstName)}</th><th>{escape(user.lastName)}</th><th>{escape(last_login_str)}</th><th>{escape(user.email)}</th></tr>"
            )
            tables += rec

    tables = tables + "</table>"
    email_handle = email if isinstance(email, str) else ", ".join(email)
    # create email payload
    email_payload = Email(
        fromEmail="Support@RegScale.com",
        emailSenderId=config["userId"],
        to=email_handle,
        subject=f"RegScale User Report - Activity in the last {days} days",
        body=get_css("email_style.css") + tables,
    )

    return email_payload


def update_compliance(regscale_parent_id: int, regscale_parent_module: str) -> None:
    """
    Update RegScale compliance history with a System Security Plan ID

    :param int regscale_parent_id: RegScale parent ID
    :param str regscale_parent_module: RegScale parent module
    :rtype: None
    """
    app = Application()
    api = Api()
    headers = {
        "accept": "*/*",
        "Authorization": app.config["token"],
    }

    response = api.post(
        headers=headers,
        url=app.config["domain"]
        + f"/api/controlImplementation/SaveComplianceHistoryByPlan?intParent={regscale_parent_id}&strModule={regscale_parent_module}",
        data="",
    )
    if not response.raise_for_status():
        if response.status_code == 201:
            if "application/json" in response.headers.get("content-type") and "message" in response.json():
                app.logger.warning(response.json()["message"])
            else:
                app.logger.warning("Resource not created.")
        if response.status_code == 200:
            app.logger.info(
                "Updated Compliance Score for RegScale Parent ID: %i.\nParent module: %s.",
                regscale_parent_id,
                regscale_parent_module,
            )
