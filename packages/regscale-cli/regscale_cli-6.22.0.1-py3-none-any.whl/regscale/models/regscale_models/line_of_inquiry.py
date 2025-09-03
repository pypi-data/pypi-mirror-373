from enum import Enum
from typing import Optional, Union

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class LoIType(str, Enum):
    """Lines of Inquiry Type Enum"""

    Audit = "Audit Question"
    Data = "Data Collection"


class LinesOfInquiry(RegScaleModel):
    """Lines of Inquiry Model"""

    _module_slug = "lines-of-inquiry"
    _unique_fields = ["id"]
    _parent_id_field = "assessmentPlanId"

    id: int = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    inquiry: Optional[str] = None
    requirement: Optional[str] = None
    assessmentPlanId: int = 0
    weight: Optional[int] = 1
    lineType: Union[LoIType, str] = LoIType.Audit
    dataType: Optional[str] = Field(default_factory=get_current_datetime)
    choiceList: Optional[str] = None
    requiresScoring: bool = True
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
