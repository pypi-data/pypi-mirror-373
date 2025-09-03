#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Assessment"""
from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field

from regscale.models.regscale_models.assessment import Assessment
from regscale.models.regscale_models.regscale_model import RegScaleModel


class MasterAssessmentStatus(Enum):
    """Enum representing different status states with string values."""

    InProgress = "In Progress"
    Completed = "Completed"


class MasterAssessment(RegScaleModel):
    """
    Model for a RegScale Assessment
    """

    _module_slug = "masterassessments"
    _unique_fields = [["title", "parentId", "parentModule"]]

    id: int = Field(default=0, description="Internal identifier for the assessment")
    # Relationship and metadata fields
    parentId: int = Field(description="ID of the parent record")
    parentModule: str = Field(description="Module of the parent record")

    leadAssessorId: str = Field(default="", description="Identifier for the lead assessor")
    title: str = Field(default=None, description="Title of the assessment")
    instructions: str = Field(default=None, description="Instructions for the assessment")
    plannedFinish: str = Field(default=None, description="Planned finish date of the assessment")
    status: str = Field(default=None, description="Current status of the assessment")
    actualFinish: Optional[str] = Field(default=None, description="Actual finish date of the assessment")
    dateAdjustedForCorrections: bool = Field(
        default=False, description="Flag indicating if dates were adjusted for corrections"
    )
    percentComplete: float = Field(default=0.0, description="Percentage of assessment completed", ge=0, le=100)
    complianceScore: Optional[int] = Field(default=None, description="Compliance score of the assessment")

    # Assessment documentation
    assessmentPlan: Optional[str] = Field(default=None, description="The assessment plan document")
    methodology: Optional[str] = Field(default=None, description="Methodology used for the assessment")
    rulesOfEngagement: Optional[str] = Field(default=None, description="Rules of engagement for the assessment")
    disclosures: Optional[str] = Field(default=None, description="Disclosures related to the assessment")
    scopeIncludes: Optional[str] = Field(default=None, description="What is included in the assessment scope")
    scopeExcludes: Optional[str] = Field(default=None, description="What is excluded from the assessment scope")
    limitationsOfLiability: Optional[str] = Field(
        default=None, description="Limitations of liability for the assessment"
    )
    documentsReviewed: Optional[str] = Field(default=None, description="Documents reviewed during the assessment")
    activitiesObserved: Optional[str] = Field(default=None, description="Activities observed during the assessment")
    fixedDuringAssessment: Optional[str] = Field(default=None, description="Issues fixed during the assessment")
    summaryOfResults: Optional[str] = Field(default=None, description="Summary of assessment results")
    assessmentReport: Optional[str] = Field(default=None, description="Full assessment report")

    # FedRAMP specific fields
    fedrampAssessmentType: Optional[str] = Field(default=None, description="Type of FedRAMP assessment")
    fedrampSignificantChanges: Optional[str] = Field(default=None, description="Significant changes for FedRAMP")
    fedrampSubmitter: Optional[str] = Field(default=None, description="FedRAMP submitter information")
    fedrampScope: Optional[str] = Field(default=None, description="FedRAMP assessment scope")
    fedrampVulnerabilitySampling: Optional[str] = Field(
        default=None, description="FedRAMP vulnerability sampling methodology"
    )
    fedrampTestingSampling: Optional[str] = Field(default=None, description="FedRAMP testing sampling methodology")
    fedrampTestingNotification: Optional[str] = Field(default=None, description="FedRAMP testing notification details")
    fedrampTestingDays: Optional[int] = Field(default=None, description="Number of FedRAMP testing days")
    fedrampDatabaseDiscrepanicies: Optional[str] = Field(default=None, description="FedRAMP database discrepancies")
    fedrampDatabaseDiscrepaniciesDescription: Optional[str] = Field(
        default=None, description="Description of FedRAMP database discrepancies"
    )
    fedrampWebDiscrepanicies: Optional[str] = Field(default=None, description="FedRAMP web discrepancies")
    fedrampWebDiscrepaniciesDescription: Optional[str] = Field(
        default=None, description="Description of FedRAMP web discrepancies"
    )
    fedrampContainerDiscrepanicies: Optional[str] = Field(default=None, description="FedRAMP container discrepancies")
    fedrampContainerDiscrepaniciesDescription: Optional[str] = Field(
        default=None, description="Description of FedRAMP container discrepancies"
    )

    @staticmethod
    def _get_additional_endpoints() -> dict[str, str]:
        """
        Get additional endpoints for the Assessments model.

        :return: A dictionary of additional endpoints
        :rtype: dict[str, str]
        """
        return ConfigDict(  # type: ignore
            get_all_by_master="/api/{model_slug}/getAllByMaster/{masterAssessmentId}",
            get_history="/api/{model_slug}/getHistory/{parentId}/{parentModuleName}",
        )

    @classmethod
    def get_history(cls, parent_id: int, parent_module: str) -> List[Assessment]:
        """
        Get a list of master assessments ordered by planned finish date.

        :param int parent_id: The ID of the parent record
        :param str parent_module: The module of the parent record
        :return: A list of assessments
        :rtype: List[Assessment]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_history").format(parentId=parent_id, parentModuleName=parent_module)
        )
        master_assessments = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    master_assessments.append(ci)
        return master_assessments

    @classmethod
    def get_all_by_master(cls, master_assessment_id: int) -> List["Assessment"]:
        """
        Get a list of assessments by id.

        :param int master_assessment_id: The ID of the master assessment
        :return: A list of assessments
        :rtype: List[Assessment]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_master").format(masterAssessmentId=master_assessment_id)
        )
        assessments = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    assessments.append(ci)
        return assessments

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: bool if the field should be formatted as a date
        :rtype: bool
        """
        return field_name in ["plannedStart", "plannedFinish", "actualFinish"]
