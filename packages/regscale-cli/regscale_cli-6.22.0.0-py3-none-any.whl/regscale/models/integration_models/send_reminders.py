#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Email Reminders Class used in admin_actions.py"""

# standard python imports
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Tuple, Optional
from urllib.parse import urljoin

from requests import JSONDecodeError
from rich.console import Console

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    create_progress_object,
    error_and_exit,
    flatten_dict,
    get_css,
    reformat_str_date,
    uncamel_case,
)
from regscale.models import Email, User
from regscale.models.app_models.pipeline import Pipeline
from regscale.utils.threading.threadhandler import create_threads, thread_assignment


class SendReminders:
    """
    Class to send reminders to users with upcoming and/or outstanding Tasks, Assessments,
    Data Calls, Issues, Security Plans, and Workflows

    :param Application app: CLI Application
    :param int days: # of days to look for upcoming and/or outstanding items, default is 30 days
    """

    def __init__(self, app: Application, days: int = 30):
        self.app = app
        self.logger = self.app.logger
        self.api = Api()
        self.config = self.app.config
        self.days = days
        self.base_url = urljoin(self.config["domain"], "/api/")
        self.users = []
        self.activated_users = []
        self.email_data = None
        self.tenant_pipeline = []
        self.final_pipeline = []
        self.emails = []
        self.job_progress = create_progress_object()

    def get_and_send_reminders(self) -> None:
        """
        Function to get and send reminders for users in RegScale that have email notifications
        enabled and have upcoming or outstanding Tasks, Assessments, Data Calls, Issues, Security Plans,
        and Workflows

        :rtype: None
        """
        import pandas as pd  # Optimize import performance

        # make sure config is set before processing
        if self.config["domain"] == "":
            error_and_exit("The domain is blank in the initialization file.")
        if self.config["token"] == "":
            error_and_exit("The token has not been set in the initialization file.")

        # get the user's tenant id, used to get all active
        # users for that instance of the application
        url = urljoin(self.base_url, f"accounts/find/{self.config['userId']}")
        self.logger.debug("Fetching tenant information from %s.", url)
        try:
            res = self.api.get(url=url)
            self.logger.debug("Response: %i: %s=%s", res.status_code, res.reason, res.text)
            self.logger.debug(res.json())
            res = res.json()
        except JSONDecodeError as ex:
            error_and_exit(f"Unable to retrieve tenant information from RegScale.\n{ex}")
        ten_id = res["tenantId"]

        # Use the api to get a list of all active users
        # with emailNotifications set to True for
        # the tenant id of the current user
        response = self.api.get(url=urljoin(self.base_url, f"accounts/{ten_id}/True"))
        activated_users_response = self.api.get(url=urljoin(self.base_url, "accounts"))
        # try to convert the response to a json file, exit if it errors
        try:
            self.users = response.json()
            self.activated_users = activated_users_response.json()
        # if error encountered, exit the application
        except JSONDecodeError as ex:
            error_and_exit(f"Unable to retrieve active users from RegScale.\n{ex}")

        # start a console progress bar and threads for the given task
        # create the threads with the given function, arguments and thread count
        with self.job_progress:
            if len(self.users) == 0:
                self.logger.warning("No users have email notifications enabled!")
                return
            self.logger.info("Fetching pipeline for %s user(s).", len(self.users))
            getting_items = self.job_progress.add_task(
                f"[#f8b737]Fetching pipeline for {len(self.users)} user(s)...",
                total=len(self.users),
            )
            max_workers = self.config.get("maxThreads", 30)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self.get_upcoming_or_expired_items,
                        user,
                    )
                    for user in self.users
                ]
                for future in as_completed(futures):
                    pipeline = future.result()
                    self.tenant_pipeline.append(pipeline)
                    self.job_progress.update(getting_items, advance=1)

            if len(self.tenant_pipeline) > 0:
                self.logger.info("Analyzing pipeline for %s user(s).", len(self.tenant_pipeline))
                # start a console progress bar and threads for the given task
                analyze_items = self.job_progress.add_task(
                    f"[#ef5d23]Analyzing pipeline for {len(self.tenant_pipeline)} user(s)...",
                    total=len(self.tenant_pipeline),
                )
                # convert user list into a dictionary using ID as the key for each user dictionary
                dict_users = {
                    self.activated_users[i]["id"]: self.activated_users[i] for i in range(len(self.activated_users))
                }

                create_threads(
                    process=self.analyze_pipeline,
                    args=(self.config, analyze_items, dict_users),
                    thread_count=len(self.tenant_pipeline),
                )
                self.logger.info("Sending an email to %s user(s).", len(self.final_pipeline))
                # start a console progress bar and threads for the given task
                emailing_users = self.job_progress.add_task(
                    f"[#21a5bb]Sending an email to {len(self.final_pipeline)} user(s)...",
                    total=len(self.final_pipeline),
                )
                create_threads(
                    process=self.format_and_email,
                    args=(self.api, self.config, emailing_users),
                    thread_count=len(self.final_pipeline),
                )
            else:
                self.logger.info("No outstanding or upcoming items!")
                sys.exit()

        # create one data table from all pandas data tables in emails
        self.email_data = pd.concat(self.emails)

        # create console variable and print # of emails sent successfully
        self.logger.info("Successfully sent an email to %s user(s)...", self.email_data.Emailed.sum())
        console = Console()
        console.print(f"[green]Successfully sent an email to {self.email_data.Emailed.sum()} user(s)...")

        # format email to notify person that called the command of the outcome
        email = Email(
            fromEmail="Support@RegScale.com",
            emailSenderId=self.config["userId"],
            to=res["email"],
            subject=f"RegScale Reminders Sent to {self.email_data.Emailed.sum()} User(s)",
            body=get_css("email_style.css")
            + self.email_data.to_html(justify="left", index=False)
            .replace('border="1"', 'border="0"')
            .replace("&amp;", "&")
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("’", "'"),
        )

        # send the email to the user
        email.send()

    def get_upcoming_or_expired_items(self, user: dict) -> Optional[Pipeline]:
        """
        Function used by threads to send emails to users with upcoming and/or outstanding
        Tasks, Assessments, Data Calls, Issues, Security Plans, and Workflows

        :param dict user: Dictionary of user to get upcoming and/or outstanding items for
        :return: Pipeline object for the provided user, if they have one or more items
        :rtype: Optional[Pipeline]
        """
        # calculate date with the # of days provided
        # have to explicitly convert the days to an int because of Airflow
        before_date = datetime.now() + timedelta(days=int(self.days))
        after_date = datetime.now() - timedelta(days=int(self.days))

        # format the date to a string the server will recognize
        before_date = before_date.strftime("%Y-%m-%dT%H:%M:%S")
        after_date = after_date.strftime("%Y-%m-%dT%H:%M:%S")

        # get all the assessments, issues, tasks, data calls, security plans and workflows
        # for the user we can email, using the # of days entered by the user using graphql,
        # if no days were entered, the default is 30 days
        query = f"""
            query {{
              assessments(
                take: 50
                skip: 0
                order: {{ plannedFinish: DESC }}
                where: {{
                  leadAssessorId: {{ eq: "{user["id"]}" }}
              plannedFinish: {{ lte: "{before_date}" }}
              status: {{ nin: ["Complete", "Cancelled"] }}
            }}
          ) {{
            items {{
              uuid
              id
              title
              leadAssessorId
              assessmentType
              plannedFinish
              createdById
              dateCreated
              status
              assessmentResult
              actualFinish
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
          dataCalls(
            take: 50
            skip: 0
            order: {{ dateDue: DESC }}
            where: {{
              createdById: {{ eq: "{user["id"]}" }}
              dateDue: {{ lte: "{before_date}" }}
              status: {{ nin: ["Completed", "Cancelled"] }}
            }}
          ) {{
            items {{
              uuid
              id
              title
              dataCallLeadId
              dateDue
              createdById
              dateCreated
              status
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
          securityPlans(
            take: 50
            skip: 0
            order: {{ expirationDate: DESC }}
            where: {{
              systemOwnerId: {{ eq: "{user["id"]}" }}
              expirationDate: {{ lte: "{before_date}" }}
            }}
          ) {{
            items {{
              uuid
              id
              systemName
              systemOwnerId
              status
              systemType
              expirationDate
              overallCategorization
              createdById
              dateCreated
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
          workflowInstances(
            take: 50
            skip: 0
            order: {{ startDate: DESC }}
            where: {{
              ownerId: {{ eq: "{user["id"]}" }}
              status: {{ neq: "Complete" }}
              startDate: {{ gte: "{after_date}" }}
              endDate: {{ eq: null }}
            }}
          ) {{
            items {{
              id
              name
              status
              startDate
              endDate
              comments
              currentStep
              createdById
              dateCreated
              lastUpdatedById
              ownerId
              atlasModule
              parentId
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
          tasks(
            take: 50
            skip: 0
            order: {{ dueDate: DESC }}
            where: {{
              assignedToId: {{ eq: "{user["id"]}" }}
              dueDate: {{ lte: "{before_date}" }}
              status: {{ nin: ["Closed", "Cancelled"] }}
            }}
          ) {{
            items {{
              uuid
              id
              title
              assignedToId
              dueDate
              createdById
              status
              percentComplete
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
          issues(
            take: 50
            skip: 0
            order: {{ dueDate: DESC }}
            where: {{
              issueOwnerId: {{ eq: "{user["id"]}" }}
              dueDate: {{ lte: "{before_date}" }}
              status: {{ nin: ["Closed", "Cancelled"] }}
            }}
          ) {{
            items {{
              uuid
              id
              title
              issueOwnerId
              severityLevel
              createdById
              dateCreated
              status
              dueDate
            }}
            totalCount
            pageInfo {{
              hasNextPage
            }}
          }}
        }}
        """
        # get the data from GraphQL
        res_data = self.api.graph(query=query)

        # create list that has dictionaries of the user's pipeline and categories
        pipelines = {
            "Assessments": {"Pipeline": res_data["assessments"]["items"]},
            "Issues": {"Pipeline": res_data["issues"]["items"]},
            "Tasks": {"Pipeline": res_data["tasks"]["items"]},
            "Data Calls": {"Pipeline": res_data["dataCalls"]["items"]},
            "Security Plans": {"Pipeline": res_data["securityPlans"]["items"]},
            "Workflow": {"Pipeline": res_data["workflowInstances"]["items"]},
        }
        # iterate through the user's pipeline tallying their items and check the amount
        total_tasks = sum(len(pipeline["Pipeline"]) for pipeline in pipelines.values())
        if total_tasks > 0:
            # map and add the data to a self variable
            return Pipeline(
                email=user["email"],
                fullName=f'{user["firstName"]} {user["lastName"]}',
                pipelines=pipelines,
                totalTasks=total_tasks,
            )
        return None

    # flake8: noqa: C901
    def analyze_pipeline(self, args: Tuple, thread: int) -> None:
        """
        Function to set up data tables from the user's pipeline while using threading

        :param Tuple args: Tuple of args to use during the process
        :param int thread: Thread number of current thread
        :rtype: None
        """
        import pandas as pd  # Optimize import performance

        config, task, users = args

        id_fields = ["leadassessorid", "assignedtoid", "datacallleadid"]

        # get the assigned threads
        threads = thread_assignment(
            thread=thread,
            total_items=len(self.tenant_pipeline),
        )
        for i in range(len(threads)):
            # get the pipeline from the self.tenant_pipeline
            pipelines = self.tenant_pipeline[threads[i]].pipelines

            # set up local variable for user pipeline
            user_pipeline = []

            # check if the user has already been analyzed
            if not self.tenant_pipeline[threads[i]].analyzed:
                # change the user's status to analyzed
                self.tenant_pipeline[threads[i]].analyzed = True

                # start out in the beginning of the pipelines
                # and iterate through all of their items
                for pipe in pipelines:
                    # creating variable to store html table for the user's email
                    prelim_pipeline = []

                    # iterate through the items in the pipeline category while
                    # creating legible table headers
                    for item in pipelines[pipe]["Pipeline"]:
                        # flatten the dict to remove nested dictionaries
                        item = flatten_dict(item)

                        # create list variable to store the renamed column names
                        headers = []
                        # iterate through all columns for the item and see if the header
                        # has to be changed to Title Case and if the data has to revalued
                        for key in item.keys():
                            # change the camelcase header to a Title Case Header
                            fixed_key = uncamel_case(key)

                            # check the keys to revalue the data accordingly
                            if key.lower() == "uuid" or (pipe.lower() == "workflow" and key.lower() == "id"):
                                # create html url using data for the html table
                                href = f'{config["domain"]}/form/{pipe.lower().replace(" ", "")}/{item["id"]}'
                                # have to add an if clause for mso to display the view button correctly
                                url = (
                                    '<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"'
                                    f'xmlns:w="urn:schemas-microsoft-com:office:word" href="{href}" '
                                    'style="height:40px;v-text-anchor:middle;width:60px;" arcsize="5%" '
                                    'strokecolor="#22C2DC" fillcolor="#1DC3EB"><w:anchorlock/><center'
                                    ' style="color:#ffffff;font-family:Roboto, Arial, sans-serif;font'
                                    '-size:14px;">View</center></v:roundrect><![endif]-->'
                                )
                                url += f'<a href="{href}" style="mso-hide:all;">View</a>'

                                headers.append("Action")
                                if pipe.lower() == "workflow":
                                    update_dict = {"UUID": url}
                                    item = {**update_dict, **item}
                                    headers.append("ID")
                                else:
                                    # replace the UUID with the HTML url
                                    item[key] = url
                            elif ("ById" in key or "ownerid" in key.lower() or key.lower() in id_fields) and item[key]:
                                # remove ById from the key
                                new_key = key.replace("Id", "")

                                # uncamel_case() the key
                                new_key = uncamel_case(new_key)

                                # replace the user id string with a user's name
                                user_id = item[key]
                                try:
                                    # try to replace the ID with a user from all active users
                                    item[key] = f'{users[user_id]["firstName"]} {users[user_id]["lastName"]}'
                                except KeyError:
                                    # means the user is not activated, fetch them via API
                                    user = User.get_user_by_id(user_id)
                                    item[key] = f"{user.firstName} {user.lastName}"
                                # add the updated key to the table headers
                                headers.append(new_key)
                            elif key.lower() == "atlasmodule":
                                headers.append("Parent Module")
                            elif ("date" in key.lower() or "finish" in key.lower()) and item[key]:
                                try:
                                    # convert string to a date & reformat the date to a legible string
                                    item[key] = reformat_str_date(item[key], "%b %d, %Y")
                                except ValueError:
                                    headers.append(fixed_key)
                                    continue
                                # append the Title Case header to the headers list
                                headers.append(fixed_key)
                            elif key == "id":
                                # change the key to all uppercase
                                headers.append(key.upper())
                            elif isinstance(item[key], str) and "<" in item[key]:
                                # replace </br> with \n
                                text = item[key].replace("</br>", "\n")

                                # strip other html codes from string values
                                item[key] = re.sub("<[^<]+?>", "", text)

                                # append the Title Case header to headers
                                headers.append(fixed_key)
                            elif key.lower() == "currentstep":
                                item[key] += 1
                                headers.append(fixed_key)
                            elif key.lower() == "workflowinstancesteps":
                                del item[key]
                            else:
                                headers.append(fixed_key)
                        # add it to the final pipeline for the user
                        prelim_pipeline.append(item)
                    # check to see if there is an item for the bucket before
                    # appending it to the self.final_pipeline for the email
                    if len(prelim_pipeline) > 0:
                        # convert the item to a pandas data table
                        data = pd.DataFrame(prelim_pipeline)

                        # replace the columns with our legible data headers
                        data.columns = headers

                        # append the data item and bucket to our local user_pipeline list
                        user_pipeline.append({"bucket": pipe, "items": data})
                # add the user's pipeline data to the self.pipeline for the emails
                self.final_pipeline.append(
                    Pipeline(
                        email=self.tenant_pipeline[threads[i]].email,
                        fullName=self.tenant_pipeline[threads[i]].fullName,
                        pipelines=user_pipeline,
                        totalTasks=self.tenant_pipeline[threads[i]].totalTasks,
                        analyzed=True,
                    )
                )
            self.job_progress.update(task, advance=1)

    def format_and_email(self, args: Tuple, thread: int) -> None:
        """
        Function to email all users with an HTML formatted email

        :param Tuple args: Tuple of args to use during the process
        :param int thread: Thread number of current thread
        :rtype: None
        """
        # set up my args from the args tuple
        import pandas as pd  # Optimize import performance

        api, config, task = args

        threads = thread_assignment(
            thread=thread,
            total_items=len(self.final_pipeline),
        )

        # update api pool limits to max_thread count from init.yaml
        max_threads = config.get("maxThreads", 100)
        if not isinstance(max_threads, int):
            try:
                max_threads = int(max_threads)
            except (ValueError, TypeError):
                max_threads = 100
        api.pool_connections = max_threads
        api.pool_maxsize = max_threads

        # get assigned threads
        for i in range(len(threads)):
            # get the user's pipeline details
            email = self.final_pipeline[threads[i]].email
            total_tasks = self.final_pipeline[threads[i]].totalTasks

            # create list to store the html tables
            tables = []

            # see if the user has been emailed already
            if not self.final_pipeline[threads[i]].emailed:
                # set the emailed flag to true
                self.final_pipeline[threads[i]].emailed = True

                # iterate through all items in self.final_pipeline to
                # set up data tables as a html tables using pandas
                for item in self.final_pipeline[threads[i]].pipelines:
                    tables.extend(
                        (
                            f'<h1>{item["bucket"]}</h1>',
                            item["items"].to_html(justify="left", index=False).replace('border="1"', 'border="0"'),
                        )
                    )
                # join all the items in tables and separate them all with a </br> tag
                tables = "</br>".join(tables)

                # fix any broken html tags
                tables = tables.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("’", "'")

                # create email payload
                email_notification = Email(
                    fromEmail="Support@RegScale.com",
                    emailSenderId=config["userId"],
                    to=email,
                    subject=f"RegScale Reminder: {total_tasks} Upcoming Items",
                    body=get_css("email_style.css") + tables,
                )

                # send the email and get the response
                if email_notification.send():
                    emailed = True
                else:
                    emailed = False

                # set up dict to use for pandas data
                data = {
                    "Email Address": '<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"'
                    'xmlns:w="urn:schemas-microsoft-com:office:word" href="mailto:'
                    f'{email}"style="height:auto;v-text-anchor:middle;mso-width-'
                    'percent:150;" arcsize="5%" strokecolor="#22C2DC" fillcolor='
                    '"#1DC3EB"><w:anchorlock/><center style="color:#ffffff;font-'
                    f'family:Roboto, Arial, sans-serif;font-size:14px;">{email}'
                    '</center></v:roundrect><![endif]--><a href="mailto:'
                    f'{email}" style="mso-hide:all;">{email}</a>',
                    "User Name": self.final_pipeline[threads[i]].fullName,
                    "Total Tasks": total_tasks,
                    "Emailed": emailed,
                }
                table = pd.DataFrame([data])
                self.emails.append(table)
            self.job_progress.update(task, advance=1)
