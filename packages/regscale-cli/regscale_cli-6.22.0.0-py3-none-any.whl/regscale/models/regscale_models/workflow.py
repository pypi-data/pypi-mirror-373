"""RegScale Workflow model"""

from typing import List, Optional

from pydantic import BaseModel, Field
from requests import JSONDecodeError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import create_logger


class Workflow(BaseModel):
    id: int = 0
    name: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    currentStep: int = 0
    comments: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: bool = True
    dateLastUpdated: Optional[str] = None
    ownerId: Optional[str] = None
    atlasModule: Optional[str] = None
    parentId: Optional[int] = None
    workflowInstanceSteps: List[str] = Field(default_factory=list)

    def insert_workflow(self, app: Application, template_id: int) -> Optional["Workflow"]:
        """
        Insert a workflow into the database

        :param Application app: Application instance
        :param int template_id: Workflow template ID in RegScale
        :return: Newly created Workflow object, or None if unsuccessful
        :rtype: Optional[Workflow]
        """
        api = Api()
        # Convert the model to a dictionary
        data = self.dict()
        url = f"{app.config['domain']}/api/workflowInstances/createFromTemplate/{template_id}"
        # Make the API call
        response = api.post(url=url, json=data)

        # Check the response
        if not response.ok:
            response.raise_for_status()
        try:
            workflow = Workflow(**response.json())
        except JSONDecodeError as jex:
            logger = create_logger()
            logger.error("Unable to read workflow:\n%s", jex)
        return workflow or None
