"""
This module contains the TaskSync class, which is used to sync tasks between RegScale and Jira.
"""

from typing import Literal

from regscale.models import Task


class TaskSync:
    """
    This class is used to sync tasks between RegScale and Jira.
    """

    tasks: list[Task] = []
    operation: Literal["create", "update", "close"] = ""
    progress_message: str = ""

    def __init__(self, tasks: list[Task], operation: Literal["create", "update", "close"]):
        self.tasks = tasks
        self.operation = operation
        if operation == "create":
            self.progress_message = f"[#f8b737]Creating {len(tasks)} task(s) in RegScale..."
        elif operation == "update":
            self.progress_message = f"[#f8b737]Updating {len(tasks)} task(s) in RegScale..."
        elif operation == "close":
            self.progress_message = f"[#f8b737]Closing {len(tasks)} task(s) in RegScale..."
