#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for milestone model in RegScale platform"""

from typing import Optional

from pydantic import Field, field_validator, model_validator

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Milestone(RegScaleModel):
    """Milestone Model"""

    _module_slug = "milestones"
    _module_string = "milestones"
    _unique_fields = ["title", "parentModule"]

    title: str
    id: int = 0
    isPublic: Optional[bool] = True
    milestoneDate: Optional[str] = Field(default_factory=get_current_datetime)
    responsiblePersonId: Optional[str] = None
    predecessorStepId: Optional[int] = None
    completed: Optional[bool] = False
    dateCompleted: Optional[str] = None
    notes: Optional[str] = ""
    parentID: Optional[int] = None
    parentModule: str = ""

    @field_validator("milestoneDate")
    @classmethod
    def validate_milestone_date(cls, v: Optional[str]) -> str:
        """Ensure milestoneDate is never empty."""
        if not v or v == "":
            return get_current_datetime()
        return v

    @field_validator("dateCompleted")
    @classmethod
    def set_date_completed(cls, v: Optional[str], info) -> Optional[str]:
        """Set dateCompleted based on completed field."""
        completed = info.data.get("completed", False)
        if completed and (v is None or v == ""):
            return get_current_datetime()
        if not completed:
            return None
        return v

    @model_validator(mode="after")
    def validate_completion(self):
        """Ensure dateCompleted is set when completed is True."""
        if self.completed and (self.dateCompleted is None or self.dateCompleted == ""):
            self.dateCompleted = get_current_datetime()
        elif not self.completed:
            self.dateCompleted = None
        return self
