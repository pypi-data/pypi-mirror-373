#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a RegScale Threat"""

# standard python imports
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, List, Optional, Union

from pydantic import ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Threat(RegScaleModel):
    """Threat Model"""

    _module_slug = "threats"
    _exclude_graphql_fields = ["tenantsId"]

    threatType: str  # Required
    status: Optional[str] = "Under Investigation"  # Required
    source: Optional[str] = "Open Source"  # Required
    title: Optional[str] = ""  # Required
    targetType: Optional[str] = ""  # Required
    threatOwnerId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)  # Required
    id: Optional[int] = 0
    uuid: Optional[str] = None
    investigationResults: Optional[str] = ""
    notes: Optional[str] = ""
    dateIdentified: str = Field(default_factory=get_current_datetime)
    dateResolved: Optional[str] = ""
    dateCreated: str = Field(default_factory=get_current_datetime)
    description: Optional[str] = ""
    targets: Optional[str] = ""
    vulnerabilityAnalysis: Optional[str] = ""
    mitigations: Optional[str] = ""
    threatTypeUnintentional: Optional[bool] = True
    threatTypePurposeful: Optional[bool] = True
    threatTypeEnvironmental: Optional[bool] = True
    threatTypeInsider: Optional[bool] = True
    threatImpactConfidentiality: Optional[bool] = True
    threatImpactIntegrity: Optional[bool] = True
    threatImpactAvailability: Optional[bool] = True
    investigated: Optional[bool] = True
    exploitable: Optional[bool] = True
    isPublic: Optional[bool] = True
    facilityId: Optional[int] = None  # This has to be None for default or else the server returns a 500 error
    orgId: Optional[int] = None  # This has to be None for default or else the server returns a 500 error
    parentModule: Optional[str] = ""
    parentId: Optional[int] = 0
    tenantsId: Optional[int] = 1

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Issues model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/count",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentId}/{strModule}",
            get_filtered_list="/api/{model_slug}/getFilteredList/{strFind}",
            get_all_by_parent_module="/api/{model_slug}/getAllByParentModule/{strModule}",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            filter_threats="/api/{model_slug}/filterThreats",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            report="/api/{model_slug}/report/{strReport}",
            schedule="/api/{model_slug}/schedule/{year}/{dvar}",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            main_dashboard_chart="/api/{model_slug}/mainDashboardChart/{year}",
            dashboard="/api/{model_slug}/dashboard/{strGroupBy}",
            dashboard_by_parent="/api/{model_slug}/dashboardByParent/{strGroupBy}/{intId}/{strModule}",
        )

    @staticmethod
    def xstr(str_eval: Any) -> str:
        """
        Replaces string with None value to ""

        :param Any str_eval: key to replace None value to ""
        :return: Updates provided str field to ""
        :rtype: str
        """
        return "" if str_eval is None else str_eval

    @staticmethod
    def bulk_insert(api: Optional[Api], threats: list[Union[dict, "Threat"]]) -> List["Threat"]:
        """
        Bulk insert Threats to the RegScale API

        :param Optional[Api] api: RegScale API
        :param list[Union[dict, Threat]] threats: List of Threats to insert
        :return: List of Threat objects from RegScale API
        :rtype: List[Threat]
        """
        if api:
            import warnings

            warnings.warn(
                "Api parameter is deprecated and will be removed in future versions.",
                DeprecationWarning,
                stacklevel=2,
            )

        results = []
        threat_objects = []
        for threat in threats:
            if isinstance(threat, dict):
                threat_objects.append(Threat(**threat))
            else:
                threat_objects.append(threat)

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [
                executor.submit(
                    threat.create,
                )
                for threat in threat_objects
            ]
            for future in as_completed(futures):
                results.append(future.result())
        return results

    @staticmethod
    def bulk_update(api: Optional[Api], threats: list[Union[dict, "Threat"]]) -> List["Threat"]:
        """
        Bulk insert Threats to the RegScale API

        :param Optional[Api] api: RegScale API
        :param list[Union[dict, Threat]] threats: List of Threats to update
        :return: List of Threat objects from RegScale API
        :rtype: List[Threat]
        """
        if api:
            import warnings

            warnings.warn(
                "Api parameter is deprecated and will be removed in future versions.",
                DeprecationWarning,
                stacklevel=2,
            )
        results = []
        threat_objects = []
        for threat in threats:
            if isinstance(threat, dict):
                threat_objects.append(Threat(**threat))
            else:
                threat_objects.append(threat)

        # use threadpoolexecutor to speed up inserts
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [
                executor.submit(
                    threat.save,
                )
                for threat in threat_objects
            ]
            for future in as_completed(futures):
                results.append(future.result())
        return results

    @staticmethod
    def fetch_all_threats() -> List["Threat"]:
        """
        Find all Threats in RegScale

        :return: List of Threats from RegScale
        :rtype: List[Threat]
        """
        from json import JSONDecodeError

        api = Api()
        body = f"""
            query {{
                threats(take: 50, skip: 0) {{
                items {{
                    {Threat.build_graphql_fields()}
                }}
                pageInfo {{
                    hasNextPage
                }}
                ,totalCount}}
            }}
            """
        try:
            api.logger.info("Retrieving all threats from RegScale...")
            existing_threats = api.graph(query=body)["threats"]["items"]
            api.logger.info("Retrieved %i threat(s) from RegScale.", len(existing_threats))
        except (JSONDecodeError, KeyError):
            existing_threats = []
        return [Threat(**threat) for threat in existing_threats]
