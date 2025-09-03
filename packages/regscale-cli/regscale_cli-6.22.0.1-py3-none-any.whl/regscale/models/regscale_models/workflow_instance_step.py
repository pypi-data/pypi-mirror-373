"""
This module contains the WorkflowInstanceStep model class that represents a workflow instance step in the RegScale application.
"""

from typing import Optional, Union

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel
from enum import Enum


class WorkflowInstanceStepType(str, Enum):
    """
    Enum for workflow instance step type.
    """

    MANAGER = "Manager"
    GROUP = "Group"


class WorkflowInstanceStepExecutionType(str, Enum):
    """
    Enum for workflow instance step execution type.
    """

    SEQUENTIAL = "Sequential"
    PARALLEL = "Parallel"


class WorkflowInstanceStepStatus(str, Enum):
    """
    Enum for workflow instance step status.
    """

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETE = "Complete"
    SUBMITTED = "Submitted"


class WorkflowInstanceStep(RegScaleModel):
    _module_slug = "workflowInstanceSteps"

    id: Optional[int] = None
    workflowInstanceId: Optional[int] = None
    name: Optional[str] = None
    comments: Optional[str] = None
    order: Optional[int] = 1
    status: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    actionType: Optional[str] = None
    executionType: Optional[str] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: Optional[bool] = True
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    groupsId: Optional[int] = None
    tenantsId: Optional[int] = 1
    stepType: Optional[str] = None
    assignedToId: Optional[str] = None
    functionalRoleId: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the WorkflowInstanceStep model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_by_parent="/api/{model_slug}/getByParent/{intParentID}",
            filter_workflow_instance_steps_by_parent="/api/{model_slug}/filterWorkflowInstanceStepsByParent/{intWorkflowInstanceID}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            update_workflow_instance_step_put="/api/{model_slug}/{id}",
            get_workflow_instance_step="/api/{model_slug}/{id}",
        )

    @classmethod
    def find_by_unique(cls, workflow_instance_id: int, field_name: str, field_value: Union[str, int]):
        """
        Find a object by unique query.
        :param workflow_instance_id: The workflow instance ID
        :param field_name: The field name
        :param field_value: The field value
        :return: The functional role
        :rtype: FunctionalRole
        """
        for instance in cls.get_all_by_parent(parent_id=workflow_instance_id, parent_module=None):
            if getattr(instance, field_name) == field_value:
                return instance
        return None

    @classmethod
    def get_by_parent(cls, parent_id: int):
        """
        Get workflow instance steps by parent ID.

        :param parent_id: The parent ID
        :return: A list of workflow instance steps
        :rtype: List[WorkflowInstanceStep]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_parent").format(model_slug=cls._module_slug, intParentID=parent_id)
        )
        if response and response.ok:
            return [WorkflowInstanceStep(**step) for step in response.json()]
        return []
