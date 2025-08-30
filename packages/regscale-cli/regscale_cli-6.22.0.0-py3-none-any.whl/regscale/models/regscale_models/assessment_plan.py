from enum import Enum
from typing import Optional, Union

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class AssesmentPlanArea(str, Enum):
    """Assessment Plan Functional Area Type Enum"""

    Safety = "Safety"
    Security = "Security"
    Quality = "Quality"
    Financial = "Financial"
    Maintenance = "Maintenance"
    Operational = "Operational"
    Environmental = "Environmental"


class AssessmentPlan(RegScaleModel):
    """Lines of Inquiry Model"""

    _module_slug = "assessmentplans"
    _unique_fields = ["id"]

    id: int = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    planOwnerId: str = Field(default_factory=RegScaleModel.get_user_id)
    title: str
    functionalArea: Union[AssesmentPlanArea, str] = AssesmentPlanArea.Financial
    description: Optional[str] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Components model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
        )
