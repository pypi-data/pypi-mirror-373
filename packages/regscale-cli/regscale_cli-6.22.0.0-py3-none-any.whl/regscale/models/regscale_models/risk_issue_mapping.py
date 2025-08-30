#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Risk Issue Mapping Model"""

from pydantic import ConfigDict, Field

from regscale.models.regscale_models.regscale_model import RegScaleModel


class RiskIssueMapping(RegScaleModel):
    """Pydantic model for Risk Issue Mapping."""

    _module_slug = "riskissuemapping"

    id: int = Field(default=0, description="Unique identifier for the risk issue mapping")
    uuid: str = Field(default="", description="UUID for the risk issue mapping")
    riskId: int = Field(description="ID of the associated risk")
    issueId: int = Field(description="ID of the associated issue")

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the RiskIssueMapping model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            filter_mappings="/api/{model_slug}/filterRiskIssueMappings/{intRisk}/{intIssues}/{strSearch}/{intPage}/{intPageSize}",
            find_mappings="/api/{model_slug}/findMappings/{intID}",
            get_mappings_as_issues="/api/{model_slug}/getMappingsAsIssues/{intID}",
            get_mappings_as_risks="/api/{model_slug}/getMappingsAsRisks/{intID}",
        )

    @classmethod
    def get_mappings_as_issue(cls, risk_id: int) -> list[dict]:
        """
        Filter mappings by risk.

        :param int risk_id: The ID of the risk to filter mappings by
        :return: A list of RiskIssueMapping objects
        :rtype: list[dict]
        """
        endpoint = cls.get_endpoint("get_mappings_as_issues").format(model_slug=cls._module_slug, intID=risk_id)
        response = cls._get_api_handler().get(endpoint)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_mappings_as_risks(cls, issue_id: int) -> list[dict]:
        """
        Filter mappings by issue.

        :param int issue_id: The ID of the issue to filter mappings by
        :return: A list of RiskIssueMapping objects
        :rtype: list[dict]
        """
        endpoint = cls.get_endpoint("get_mappings_as_risks").format(model_slug=cls._module_slug, intID=issue_id)
        response = cls._get_api_handler().get(endpoint)
        response.raise_for_status()
        return response.json()
