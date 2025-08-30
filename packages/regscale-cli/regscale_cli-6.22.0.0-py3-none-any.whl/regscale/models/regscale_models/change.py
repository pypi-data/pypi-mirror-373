"""
This module contains the Change model for RegScale.
"""

import logging
from enum import Enum
from typing import Optional, List, Dict

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """
    Enum for the ChangeType field in the Change model.
    """

    emergency = "Emergency"
    normal = "Normal"
    standard = "Standard"


class ChangePriority(str, Enum):
    """
    Enum for the ChangePriority field in the Change model.
    """

    critical = "Critical"
    low = "Low"
    moderate = "Moderate"
    high = "High"
    security = "Security"


class ChangeStatus(str, Enum):
    """
    Enum for the ChangeStatus field in the Change model.
    """

    draft = "Draft"
    assess = "Assess"
    pending_approval = "Pending Approval"
    approved = "Approved"
    schedule = "Schedule"
    implement = "Implement"
    review = "Review"
    complete = "Complete"
    cancelled = "Cancelled"


class ChangeOutageRequired(str, Enum):
    """
    Enum for the ChangeOutageRequired field in the Change model.
    """

    yes = "Yes"
    no = "No"


class Change(RegScaleModel):
    """
    A class to represent the Change model in RegScale.
    """

    _module_id = 31
    _module_slug = "changes"
    _parent_id_field = "parentId"

    id: Optional[int] = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    title: str
    changeReason: str
    description: Optional[str] = None
    changeOwnerId: str = Field(default_factory=RegScaleModel.get_user_id)
    dateRequested: str = Field(default_factory=get_current_datetime)
    startChangeWindow: Optional[str] = None
    endChangeWindow: Optional[str] = None
    outageRequired: str = ChangeOutageRequired.no.value
    outageSummary: Optional[str] = None
    status: str = ChangeStatus.draft.value
    dateChangeApproved: Optional[str] = None
    dateWorkCompleted: Optional[str] = None
    changeType: str = ChangeType.standard.value
    priority: str = ChangePriority.moderate.value
    securityImpactAssessment: Optional[str] = None
    changePlan: Optional[str] = None
    riskAssessment: Optional[str] = None
    rollbackPlan: Optional[str] = None
    communicationsPlan: Optional[str] = None
    notes: Optional[str] = None
    leadTesterId: Optional[str] = None
    testPlan: Optional[str] = None
    testResults: Optional[str] = None
    dateTested: Optional[str] = None
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    # now create the _get_additional_endpoints method from this list of endpoints
    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Changes model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            schedule="/api/{model_slug}/schedule/{year}/{strDateField}",
            report="/api/{model_slug}/report/{strReport}",
            filter_changes="/api/{model_slug}/filterChanges",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
        )

    @classmethod
    def filter_change(cls, payload: Dict) -> List["Change"]:
        """
        Filter change based on query parameters.

        :param dict payload: Query parameters
        :return: A list of changes
        """
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("filter_changes").format(model_slug=cls._module_slug), data=payload
        )
        if response and response.ok:
            return [cls(**ci) for ci in response.json().get("items", [])]
        return []

    @staticmethod
    def fetch_all_changes() -> List["Change"]:
        """
        Fetch all changes in RegScale

        :return: List of Changes from RegScale
        :rtype: List[Change]
        """
        from regscale.core.app.api import Api
        from requests import JSONDecodeError

        api = Api()
        body = f"""
        query {{
            changes(take: 50, skip: 0) {{
            items {{
                {Change.build_graphql_fields()}
            }}
            pageInfo {{
                hasNextPage
            }}
            ,totalCount}}
        }}"""
        try:
            api.logger.info("Retrieving all changes from RegScale...")
            existing_changes = api.graph(query=body)["changes"]["items"]
            api.logger.info("Retrieved %i change(s) from RegScale.", len(existing_changes))
        except (JSONDecodeError, KeyError):
            existing_changes = []
        return [Change(**change) for change in existing_changes]
