from enum import Enum
from typing import Optional, Union
from datetime import datetime

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class AssessmentResult(RegScaleModel):
    """Assessment Results Model"""

    _module_slug = "assessmentresults"
    _unique_fields = ["id"]

    id: int = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    status: Optional[str] = None
    loqId: Optional[int] = 0
    lineOfInquiry: Optional[str] = None
    requirement: Optional[str] = None
    citation: Optional[str] = None
    weight: Optional[int] = 0
    responsibility: Optional[str] = None
    guidance: Optional[str] = None
    observations: Optional[str] = None
    recommendations: Optional[str] = None
    issuesIdentified: Optional[str] = None
    riskAssessment: Optional[str] = None
    samplingMethodology: Optional[str] = None
    fixedDuringAssessment: bool = False
    bComplete: bool = False
    parentAssessmentId: Optional[int] = 0
    dataDate: Optional[str] = Field(default_factory=get_current_datetime)
    dataString: Optional[datetime] = None
    dataDecimal: Optional[float] = 0.0
    dataBoolean: Optional[bool] = False
