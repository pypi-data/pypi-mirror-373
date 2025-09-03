#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for evidence model in RegScale platform"""

from typing import Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Evidence(RegScaleModel):
    """Evidence Model"""

    _module_slug = "evidence"
    _unique_fields = [["title"]]

    id: int = 0
    isPublic: Optional[bool] = True
    uuid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    evidenceOwnerId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    evidenceApproverId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    status: Optional[str] = None
    updateFrequency: Optional[int] = 365
    lastEvidenceUpdate: Optional[str] = Field(default_factory=get_current_datetime)
    dueDate: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastApproved: Optional[str] = Field(default_factory=get_current_datetime)

    _unique_fields = ["title"]

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Evidence model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            get_evidence_by_date="/api/{model_slug}/getEvidenceByDate/{intDays}",
            get_controls_by_evidence="/api/{model_slug}/getControlsByEvidence/{intEvidenceId}",
            get_evidence_by_control="/api/{model_slug}/getEvidenceByControl/{intControl}",
            get_evidence_by_security_plan="/api/{model_slug}/getEvidenceBySecurityPlan/{intId}",
            filter_evidence="/api/{model_slug}/filterEvidence",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            get_my_evidence_due_soon="/api/{model_slug}/getMyEvidenceDueSoon/{intDays}/{intPage}/{intPageSize}",
        )

    @classmethod
    def filter_evidence(
        cls,
        field: Optional[str] = None,
        type: Optional[str] = None,
        operator: Optional[str] = None,
        value: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> list:
        """
        Filter evidence based on the given filter parameters.

        :param Optional[str] field: Filter field
        :param Optional[str] type: Filter type
        :param Optional[str] operator: Filter operator
        :param Optional[str] value: Filter value
        :param Optional[int] page: Page number, defaults to 1
        :param Optional[int] page_size: Page size, defaults to 10
        :return: A list of filtered evidence
        :rtype: list
        """
        query = {
            "parentID": 0,
            "module": "",
            "friendlyName": "",
            "workbench": "",
            "base": "",
            "sort": "dueDate",
            "direction": "Ascending",
            "simpleSearch": "",
            "page": "",
            "pageSize": "",
            "query": {
                "id": 0,
                "viewName": "",
                "module": "",
                "scope": "",
                "createdById": "",
                "dateCreated": "",
                "parameters": [
                    {"id": 0, "field": "", "type": "", "operator": "", "value": "", "viewName": "", "name": ""}
                ],
            },
            "groupBy": "",
            "intDays": 0,
            "subTab": False,
        }
        query["page"] = page
        query["pageSize"] = page_size
        query["query"]["parameters"][0]["field"] = field
        query["query"]["parameters"][0]["type"] = type
        query["query"]["parameters"][0]["operator"] = operator
        query["query"]["parameters"][0]["value"] = value

        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("filter_evidence").format(module_slug=cls._module_slug), data=query
        )
        if not response.raise_for_status():
            return response.json()
        return []
