from enum import Enum
from typing import Optional

from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class CaseStatus(str, Enum):
    """
    Enum for the CaseStatus field in the Case model.
    """

    in_progress = "In Progress"
    closed = "Closed"
    pending = "Pending"
    resolved = "Resolved"
    complete = "Complete"
    cancelled = "Cancelled"
    on_hold = "On Hold"


class Case(RegScaleModel):
    _module_slug = "cases"
    _module_id = 28

    id: Optional[int] = None
    title: str
    uuid: Optional[str] = None
    description: Optional[str] = None
    status: str = CaseStatus.pending
    caseNumber: Optional[str] = None
    caseWorkerId: str = Field(default_factory=RegScaleModel.get_user_id)
    dateReported: str = Field(default_factory=get_current_datetime)
    dateResolved: Optional[str] = None
    notes: Optional[str] = None
    reportedBy: str = Field(default_factory=RegScaleModel.get_user_id)
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
