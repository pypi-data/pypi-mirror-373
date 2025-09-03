import logging
from enum import Enum
from typing import Optional, List

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel
from workflow_instance_step import WorkflowInstanceStep
from workflow_template import WorkflowTemplate

logger = logging.getLogger(__name__)


class WorkflowInstanceStatus(Enum):
    """
    Enum for workflow instance status.
    """

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETE = "Complete"


class WorkflowInstance(RegScaleModel):
    _module_slug = "workflowInstances"

    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = Field(default=WorkflowInstanceStatus.PENDING.value)
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    currentStep: Optional[int] = None
    comments: Optional[str] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: Optional[bool] = True
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    ownerId: Optional[str] = None
    parentId: Optional[int] = None
    atlasModule: Optional[str] = None
    workflowInstanceSteps: Optional[List[WorkflowInstanceStep]] = None
    tenantsId: Optional[int] = 1

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the WorkflowInstance model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_by_parent="/api/{model_slug}/filterWorkflowInstanceByParentId/{intParentID}/{strModule}/id/descending/1/100",
            get_count="/api/{model_slug}/getCount",
            get_open="/api/{model_slug}/getOpen",
            get_by_status="/api/{model_slug}/getByStatus",
            user_open_items_days="/api/{model_slug}/userOpenItemsDays/{strOwner}/{intDays}",
            filter_workflow_instances="/api/{model_slug}/filterWorkflowInstances/{strSearch}/{strStatus}/{strOwner}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            filter_workflow_instances_by_user="/api/{model_slug}/filterWorkflowInstancesByUser/{strUser}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            approve_step_put="/api/{model_slug}/approveStep/{strUserId}",
            submit_put="/api/{model_slug}/submit/{userId}",
            create_from_module_post="/api/{model_slug}/createFromModule/{intTemplateId}/{strUserId}",
            create_custom_workflow_post="/api/{model_slug}/createCustomWorkflow/{strModule}/{intParentId}",
            reject_step_put="/api/{model_slug}/rejectStep/{strUserId}",
            create_from_template_post="/api/{model_slug}/createFromTemplate/{intTemplateId}",
        )

    @classmethod
    def get_workflows_by_parent(cls, parent_id: int, parent_module: str) -> List["WorkflowInstance"]:
        """
        Get all workflows by parent.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of workflows
        :rtype: List[WorkflowInstance]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_parent").format(intParentID=parent_id, strModule=parent_module)
        )
        if response and response.ok:
            json_data = response.json()
            items = json_data.get("items", [])
            return [WorkflowInstance(**workflow) for workflow in items]
        return []

    @classmethod
    def find_by_unique(cls, parent_id: int, parent_module: str, name: str) -> Optional["WorkflowInstance"]:
        """
        Find a object by unique query.
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :param str name: The name of the object
        :return: The functional role
        :rtype: FunctionalRole
        """
        for instance in cls.get_all_by_parent(parent_id=parent_id, parent_module=parent_module):
            if instance.name == name:
                return instance
        return None

    @classmethod
    def create_from_template(cls, template_id: int) -> Optional[int]:
        """
        Create a workflow instance from a template.

        :param int template_id: The ID of the template
        :return: The created workflow instance id
        :rtype: Optional[int]
        """
        workflow_template = WorkflowTemplate.get_object(object_id=template_id)
        if not workflow_template:
            logger.error(f"Failed to find workflow template {template_id}")
            return None
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("create_from_template_post").format(
                model_slug=cls._module_slug, intTemplateId=template_id
            ),
            data=workflow_template.model_dump(),
        )
        if response and response.ok:
            return int(response.text)
        else:
            logger.error(f"Failed to create workflow instance from template {template_id}")
            return None

    @classmethod
    def create_custom_workflow_from_template(
        cls, template_id: int, parent_id: int, parent_module: str
    ) -> Optional["WorkflowInstance"]:
        """
        Create a workflow instance from a template.

        :param int template_id: The ID of the template
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: The created workflow instance id
        :rtype: Optional[int]
        """
        workflow_template = WorkflowTemplate.get_object(object_id=template_id)
        steps = workflow_template.workflowTemplateSteps
        if not workflow_template:
            logger.error(f"Failed to find workflow template {template_id}")
            return None
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("create_custom_workflow_post").format(
                model_slug=cls._module_slug, strModule=parent_module, intParentId=parent_id
            ),
            data=[step.model_dump() for step in steps],
        )
        if response and response.ok:
            return WorkflowInstance(**response.json())
        else:
            logger.error(f"Failed to create workflow instance from template {template_id}")
            return None

    @classmethod
    def create_custom_workflow_from_template_with_group(
        cls, template_id: int, parent_id: int, parent_module: str, group_id: int, group_name: str
    ) -> Optional["WorkflowInstance"]:
        """
        Create a workflow instance from a template.

        :param int template_id: The ID of the template
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :param int group_id: The ID of the group
        :param str group_name: The name of the group
        :return: The created workflow instance id
        :rtype: Optional[int]
        """
        workflow_template = WorkflowTemplate.get_object(object_id=template_id)
        steps = workflow_template.workflowTemplateSteps
        for step in steps:
            if step.name == "Automated Conflict of Interest Check":
                continue
            step.name = f"{step.name} - {group_name}" if group_name else step.name
            step.groupsId = group_id

        if not workflow_template:
            logger.error(f"Failed to find workflow template {template_id}")
            return None
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("create_custom_workflow_post").format(
                model_slug=cls._module_slug, strModule=parent_module, intParentId=parent_id
            ),
            data=[step.model_dump() for step in steps],
        )
        if response and response.ok:
            return WorkflowInstance(**response.json())
        else:
            logger.error(f"Failed to create workflow instance from template {template_id}")
            return None

    def create_custom_workflow(self, module: str, parent_id: int) -> Optional[int]:
        """
        Create a custom workflow instance.

        :param str module: The module of the parent
        :param int parent_id: The ID of the parent
        :return: The created workflow instance id
        :rtype: Optional[int]
        """
        response = selfcls._get_api_handler().post(
            endpoint=self.get_endpoint("create_custom_workflow_post").format(
                model_slug=self._module_slug, strModule=module, intParentId=parent_id
            ),
            data=self.dict(),
        )
        if response and response.ok:
            return int(response.text)
        else:
            logger.error(f"Failed to create custom workflow instance from module {module}. Error: {response.text}")
            return None

    def approve_step(self, user_id: str) -> bool:
        """
        Approve a step in a workflow instance.

        :param str user_id: The ID of the user
        :return: True if successful
        :rtype: bool
        """
        response = selfcls._get_api_handler().put(
            endpoint=self.get_endpoint("approve_step_put").format(model_slug=self._module_slug, strUserId=user_id),
            data=self.dict(),
        )
        if getattr(response, "ok", False):
            return True
        else:
            logger.error(f"Failed to approve step for {self.name}")
            return False

    def reject_step(self, user_id: str) -> bool:
        """
        Reject a step in a workflow instance.

        :param str user_id: The ID of the user
        :return: True if successful
        :rtype: bool
        """
        response = selfcls._get_api_handler().put(
            endpoint=self.get_endpoint("reject_step_put").format(model_slug=self._module_slug, strUserId=user_id),
            data=self.dict(),
        )
        if getattr(response, "ok", False):
            return True
        else:
            logger.error(f"Failed to reject step for {self.name}")
            return False

    def approve_all_steps(self, user_id: str) -> None:
        """
        Approve all steps in a workflow instance.

        :param str user_id: The ID of the user
        :rtype: None
        """
        for step in WorkflowInstanceStep.get_all_by_parent(
            parent_id=self.id,
            parent_module=self.get_module_slug(),
        ):
            if step.order not in [0, 1000]:
                self.currentStep = step.order
                self.comments = "<p>I Approve</p>"
                self.approve_step(user_id=user_id)
