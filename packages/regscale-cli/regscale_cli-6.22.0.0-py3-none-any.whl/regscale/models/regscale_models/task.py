#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Task in the application"""

from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.utils.date import date_str
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Task(RegScaleModel):
    """
    Task model class
    """

    _module_slug = "tasks"
    _unique_fields = [
        ["title", "description", "parentID", "parentModule"],
    ]
    status: str  # Required
    title: str  # Required
    dueDate: str  # Required
    id: int = 0  # Required
    uuid: Optional[str] = None
    otherIdentifier: Optional[str] = None
    taskType: Optional[str] = None
    assignedToId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    description: Optional[str] = None
    results: Optional[str] = None
    originalDueDate: Optional[str] = None
    dateSlide: Optional[int] = None
    dateClosed: Optional[str] = None
    percentComplete: Optional[int] = None
    statusUpdate: Optional[str] = None
    orgId: Optional[int] = None
    levelOfEffort: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    isPublic: bool = True
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)  # FK to AspNetUsers
    dateCreated: str = Field(default_factory=get_current_datetime)  # Required
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)  # FK to AspNetUsers
    dateLastUpdated: str = Field(default_factory=get_current_datetime)  # Required

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Task model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            create="/api/{model_slug}",
            other_identifier_starts_with="/api/{model_slug}/otherIdentifierStartsWith/{strId}",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            get_by_date_range="/api/{model_slug}/getByDateRangeAll/{dtStart}/{dtEnd}",
        )

    @classmethod
    def other_identifier_starts_with(cls, starts_with: str) -> List["Task"]:
        """
        Get tasks based on otherIdentifier field, starts with.

        :param str starts_with: The starting characters of a string.
        :return: A list of Task instances matching the query
        :rtype: List[Task]
        """
        endpoint = cls.get_endpoint("other_identifier_starts_with").format(strId=starts_with)
        response = cls._get_api_handler().get(endpoint=endpoint)
        return cls._handle_list_response(response)

    @classmethod
    def query_by_custom_field(cls, field_name: str, field_value: str) -> List["Task"]:
        """
        Query tasks by a custom field.

        :param str field_name: The name of the custom field to query
        :param str field_value: The value of the custom field to match
        :return: A list of Task instances matching the query
        :rtype: List[Task]
        """
        endpoint = cls.get_endpoint("query_by_custom_field").format(strFieldName=field_name, strValue=field_value)
        response = cls._get_api_handler().get(endpoint=endpoint)
        return cls._handle_list_response(response)

    @classmethod
    def get_by_date_range(cls, start_date: str, end_date: str) -> List["Task"]:
        """
        Query tasks within a specified date range.

        :param str start_date: The start date of the range
        :param str end_date: The end date of the range
        :return: A list of Task instances within the specified date range
        :rtype: List[Task]
        """

        endpoint = cls.get_endpoint("get_by_date_range").format(dtStart=date_str(start_date), dtEnd=date_str(end_date))
        response = cls._get_api_handler().get(endpoint=endpoint)
        return cls._handle_list_response(response)

    def __eq__(self, other: "Task") -> bool:
        """
        Equality of items in Task class

        :param Task other: Task object to compare to
        :return: Whether the two tasks are equal
        :rtype: bool
        """
        return (
            self.title == other.title
            and self.otherIdentifier == other.otherIdentifier
            and self.description == other.description
            and self.parentId == other.parentId
            and self.parentModule == other.parentModule
        )

    def __hash__(self) -> int:
        """
        Hash function for Task class

        :return: Hash of the Task object
        :rtype: int
        """

        return hash((self.title, self.description, self.parentId, self.parentModule, self.otherIdentifier))

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        Validate the status of the task

        :param str v: The status of the task
        :raises ValueError: If the status is not one of the allowed values
        :return: The status of the task
        :rtype: str

        """
        if v not in ["Backlog", "Open", "Closed", "Cancelled"]:
            raise ValueError("Task status must be either 'Backlog', 'Open', 'Closed', or 'Cancelled'")
        return v
