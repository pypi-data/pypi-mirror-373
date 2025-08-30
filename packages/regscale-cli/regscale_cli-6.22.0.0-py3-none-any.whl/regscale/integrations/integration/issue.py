#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration issue module
"""
from abc import ABC, abstractmethod
from datetime import time
from time import sleep
from typing import Callable, Dict, List, Set

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models import Issue, Vulnerability


class IntegrationIssue(ABC):
    """
    Integration issue class
    """

    # TOMOO This needs to be refactored to use ScannerIntegration.
    # ScannerIntegration will have to be refactored to handle missing field mappings

    def __init__(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def pull(self):
        """
        Pull inventory from an Integration platform into RegScale
        """

    def create_issues(
        self,
        issues: list[Issue],
    ):
        """
        Create issues in RegScale

        :param list[Issue] issues: list of issues to create
        """
        Issue.batch_create(items=issues)

    @staticmethod
    def create_or_update_issues(
        issues: list[Issue],
        parent_id: int,
        parent_module: str,
    ):
        """
        Create issues in RegScale

        :param list[Issue] issues: list of issues to create or update
        :param int parent_id: parent id
        :param str parent_module: parent module
        """
        existing_issues: List[Issue] = Issue.get_all_by_parent(parent_id=parent_id, parent_module=parent_module)
        # otherIdentifier is the real key with coalfire/fedramp
        insert_issues = [
            item for item in issues if item.otherIdentifier not in {iss.otherIdentifier for iss in existing_issues}
        ]
        update_issues: List[Issue] = []
        for issue in issues:
            if issue.otherIdentifier in {iss.otherIdentifier for iss in existing_issues}:
                # get index of the issue
                issue.id = [iss for iss in existing_issues if iss.otherIdentifier == issue.otherIdentifier].pop().id
                # update the update_issues list
                update_issues.append(issue)
        if insert_issues:
            Issue.batch_create(items=insert_issues)
        if update_issues:
            Issue.batch_update(items=list(update_issues))

    @staticmethod
    def close_issues(issue_vuln_map: Dict[int, Dict[int, List[Vulnerability]]]) -> None:
        """
        Close issues in RegScale based on the newest vulnerabilities

        :param Dict[int, Dict[int, List[Vulnerability]]] issue_vuln_map: map of issues to
            vulnerabilities by way of assets!
        """

        update_issues: List[Issue] = []
        for key in issue_vuln_map.keys():
            # close existing_issues in RegScale if they are no longer relevant
            for asset_key in issue_vuln_map[key].keys():
                vulns = issue_vuln_map[key][asset_key]
                if not [vuln for vuln in vulns if str(vuln.severity or "").lower() in ["moderate", "high", "critical"]]:
                    # Close issue
                    update_issue = Issue.get_object(object_id=key)
                    if update_issue:
                        update_issue.status = "Closed"
                        update_issue.dateCompleted = get_current_datetime()
                        update_issues.append(update_issue)
        if update_issues:
            Issue.batch_update(items=update_issues)
