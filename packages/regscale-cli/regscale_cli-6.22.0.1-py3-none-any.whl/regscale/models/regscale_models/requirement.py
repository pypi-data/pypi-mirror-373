#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for Requirement in the application"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Requirement:
    title: str  # Required
    status: str  # Required
    lastUpdatedById: str  # Required
    controlID: int  # Required
    requirementOwnerId: str  # Required
    parentId: int  # Required
    id: int = 0
    assessmentPlan: str = ""
    dateLastAssessed: str = ""
    lastAssessmentResult: str = ""
    parentRequirementId: Optional[int] = None
    parentModule: str = "implementations"
    createdById: str = ""
    dateCreated: str = ""
    dateLastUpdated: str = ""
    isPublic: bool = True
    description: str = ""
    implementation: str = ""
    uuid: str = ""
