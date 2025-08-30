#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Incident Model"""

from typing import Optional, Any

import requests
from pydantic import ConfigDict, field_validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import camel_case, snake_case
from .regscale_model import RegScaleModel


class Incident(RegScaleModel):
    """RegScale Incident

    :raises ValueError: Validation Error
    :return: RegScale Incident
    """

    _module_slug = "incidents"

    category: str  # Required
    detectionMethod: str  # Required
    dateDetected: str  # Required
    phase: str  # Required
    title: str  # Required
    incidentPOCId: str  # Required
    id: int = 0
    attackVector: Optional[str] = None
    compromiseDate: Optional[str] = None
    cost: float = 0
    dateResolved: Optional[str] = None
    description: Optional[str] = None
    ioc: Optional[str] = None
    impact: Optional[str] = None
    parentId: Optional[int] = None
    responseActions: Optional[str] = None
    sourceCause: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    parentModule: Optional[str] = None
    tenantsId: Optional[int] = None
    facilityId: Optional[int] = None
    # post_incident: Optional[str]
    uuid: Optional[str] = None
    isPublic: bool = True
    orgId: Optional[int] = None
    containmentSteps: Optional[str] = None
    eradicationSteps: Optional[str] = None
    recoverySteps: Optional[str] = None
    severity: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Incidents model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            get_filtered_list="/api/{model_slug}/getFilteredList/{strFind}",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            main_dashboard_chart="/api/{model_slug}/mainDashboardChart/{year}",
            filter_incidents="/api/{model_slug}/filterIncidents",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            report="/api/{model_slug}/report/{strReport}",
            schedule="/api/{model_slug}/schedule/{year}/{dvar}",
            graph_due_date="/api/{model_slug}/graphDueDate/{year}",
            dashboard="/api/{model_slug}/dashboard/{strGroupBy}",
            dashboard_by_parent="/api/{model_slug}/dashboardByParent/{strGroupBy}/{intId}/{strModule}",
        )

    @classmethod
    @field_validator("category")
    def check_category(cls, value: Any) -> str:
        """
        Validate Category

        :param Any value: An incident category
        :raises ValueError: Validation Error if category is not in list
        :return: An incident category
        :rtype: str
        """
        categories = [
            "CAT 0 - Exercise/Network Defense Testing",
            "CAT 1 - Unauthorized Access",
            "CAT 2 - Denial of Service (DoS)",
            "CAT 3 - Malicious Code",
            "CAT 4 - Improper Usage",
            "CAT 5 - Scans/Probes/Attempted Access",
            "CAT 6 - Investigation",
        ]
        if value not in categories:
            cats = "\n".join(categories)
            raise ValueError(f"Category must be one of the following:\n{cats}")
        return value

    @classmethod
    @field_validator("phase")
    def check_phases(cls, value: str) -> str:
        """Validate Phases

        :raises ValueError: Validation Error for Incident Phase
        :param str value: An incident phase
        :return: An incident phase
        :rtype: str
        """
        phases = [
            "Analysis",
            "Closed",
            "Containment",
            "Detection",
            "Eradication",
            "Recovery",
        ]
        if value not in phases:
            phas = "\n".join(phases)
            raise ValueError(f"Phase must be one of the following:\n{phas}")
        return value

    @staticmethod
    def post_incident(incident: "Incident") -> requests.Response:
        """
        Post Incident to RegScale via API

        :param Incident incident: An instance of Incident
        :return: Response object from API post to RegScale
        :rtype: requests.Response
        """
        app = Application()
        config = app.config
        api = Api()
        url = config["domain"] + "/api/incidents"
        incident.id = 0  # ID must be 0 for POST
        incident_d = incident.dict()
        response = api.post(url=url, json=incident_d)
        return response

    @staticmethod
    def get_incident(incident_id: int) -> "Incident":
        """
        Get Incident from RegScale with provided ID

        :param int incident_id: An Incident ID
        :return: RegScale incident object
        :rtype: Incident
        """
        app = Application()
        config = app.config
        api = Api()
        url = config["domain"] + "/api/incidents/" + str(incident_id)
        response = api.get(url=url)
        dat = response.json()
        convert = {
            snake_case(camel_case(key)).lower().replace("pocid", "poc_id"): value for (key, value) in dat.items()
        }
        return Incident(**convert)

    def to_dict(self) -> dict:
        """
        Convert Incident object RegScale friendly dict, used in flask_api application

        :return: RegScale friendly dict for posting to API
        :rtype: dict
        """
        dat = self.dict()
        return {camel_case(key): value for (key, value) in dat.items()}
