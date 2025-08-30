#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Assessment"""
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, List, Optional, Union

from requests import JSONDecodeError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel


class AssessmentStatus(Enum):
    """
    Enum for acceptable Assessment Statuses
    """

    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"
    CANCELLED = "Cancelled"


class AssessmentType(Enum):
    """
    Enum for acceptable Assessment Types in RegScale
    """

    SELF = "Self"
    INDEPENDENT = "Independent"
    EFFECTIVENESS_REVIEW = "Effectiveness Review"
    IMPLEMENTATION_VERIFICATION_REVIEW = "Implementation Verification Review"
    MANAGEMENT = "Management"
    READINESS_REVIEW = "Readiness Review"
    SUPPLIER_QUALITY_EVALUATION = "Supplier Quality Evaluation"
    QA_SURVEILLANCE = "QA Surveillance"
    RP_SURVEILLANCE = "RP Surveillance"
    SH_SURVEILLANCE = "SH Surveillance"


class AssessmentResultsStatus(str, Enum):
    """
    Enum for acceptable Assessment Result Statuses in RegScale
    """

    NOT_YET_ASSESSED = "Not Yet Assessed"
    PASS = "Pass"
    FAIL = "Fail"
    PARTIAL = "Partial Pass"
    NOT_APPLICABLE = "Not Applicable"


class Assessment(RegScaleModel):
    """
    Model for a RegScale Assessment
    """

    _module_slug = "assessments"

    id: int = 0
    leadAssessorId: str = ""
    title: Optional[str] = None
    assessmentType: Optional[Union[AssessmentType, str]] = None
    plannedStart: Optional[str] = None
    plannedFinish: Optional[str] = None
    status: Union[AssessmentStatus, str] = AssessmentStatus.SCHEDULED
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    assessmentResult: Optional[Union[str, AssessmentResultsStatus]] = ""
    actualFinish: Optional[str] = None
    assessmentReport: Optional[str] = None
    masterId: Optional[int] = None
    complianceScore: Optional[float] = None
    targets: Optional[str] = None
    automationInfo: Optional[str] = None
    automationId: Optional[str] = None
    metadata: Optional[str] = None
    assessmentPlan: Optional[str] = None
    methodology: Optional[str] = None
    rulesOfEngagement: Optional[str] = None
    disclosures: Optional[str] = None
    scopeIncludes: Optional[str] = None
    scopeExcludes: Optional[str] = None
    limitationsOfLiability: Optional[str] = None
    documentsReviewed: Optional[str] = None
    activitiesObserved: Optional[str] = None
    fixedDuringAssessment: Optional[str] = None
    summaryOfResults: Optional[str] = None
    oscalsspId: Optional[int] = None
    oscalComponentId: Optional[int] = None
    controlId: Optional[int] = None
    requirementId: Optional[int] = None
    securityPlanId: Optional[int] = None
    projectId: Optional[int] = None
    supplyChainId: Optional[int] = None
    policyId: Optional[int] = None
    componentId: Optional[int] = None
    incidentId: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    isPublic: bool = True
    verificationStatus: Optional[str] = None
    otherIdentifier: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> dict[str, str]:
        """
        Get additional endpoints for the Assessments model.

        :return: A dictionary of additional endpoints
        :rtype: dict[str, str]
        """
        return {  # type: ignore
            "user_open_items_days": "/api/{model_slug}/userOpenItemsDays/{strUserId}/{intDays}",
            "get_existing_lightning_by_parent": "/api/{model_slug}/getExistingLightningByParent/{intParentID}/{strModule}",
            "get_all_by_grandparent": "/api/{model_slug}/getAllByGrandParent/{intParentID}/{strModule}",
            "get_all_by_master": "/api/{model_slug}/getAllByMaster/{intMaster}",
            "get_count": "/api/{model_slug}/getCount",
            "batch_recurring": "/api/{model_slug}/batchRecurring/{intID}/{dtStart}/{dtEnd}/{repeatUntil}/{strFrequency}",
            "process_lineage": "/api/{model_slug}/processLineage/{intAssessmentID}",
            "assessment_first_and_last": "/api/{model_slug}/assessmentFirstAndLast/{intId}/{strModule}",
            "assessment_timeline": "/api/{model_slug}/assessmentTimeline/{intId}/{strModule}/{strType}",
            "calendar_assessments": "/api/{model_slug}/calendarAssessments/{dtDate}/{fId}/{orgId}/{userId}",
            "graph": "/api/{model_slug}/graph",
            "graph_by_date": "/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            "schedule": "/api/{model_slug}/schedule/{year}/{strField}",
            "get_by_date_range_all": "/api/{model_slug}/GetByDateRangeAll/{dtStart}/{dtEnd}",
            "get_by_date_range_open": "/api/{model_slug}/getByDateRangeOpen/{dtStart}/{dtEnd}",
            "get_by_date_range_closed": "/api/{model_slug}/getByDateRangeClosed/{dtStart}/{dtEnd}",
            "graph_by_owner_then_status": "/api/{model_slug}/graphByOwnerThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "graph_by_type_then_status": "/api/{model_slug}/graphByTypeThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "group_by_owner_then_status": "/api/{model_slug}/groupByOwnerThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "main_dashboard_chart": "/api/{model_slug}/mainDashboardChart/{year}",
            "main_dashboard": "/api/{model_slug}/mainDashboard/{intYear}",
            "main_dashboard_overdue": "/api/{model_slug}/mainDashboardOverdue",
            "main_dashboard_upcoming": "/api/{model_slug}/mainDashboardUpcoming",
            "graph_due_date": "/api/{model_slug}/graphDueDate/{year}",
            "graph_due_date_by_status": "/api/{model_slug}/graphDueDateByStatus/{year}",
            "report": "/api/{model_slug}/report/{strReport}",
            "query_by_custom_field": "/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            "filter_assessments": "/api/{model_slug}/filterAssessments",
            "batch_create": "/api/{model_slug}/batchCreate",
            "heimdall": "/api/{model_slug}/heimdall/{intID}",
            "find_by_other_identifier": "/api/{model_slug}/findByOtherIdentifier/{strID}",
            "other_identifier_starts_with": "/api/{model_slug}/otherIdentifierStartsWith/{strID}",
            "get_completed_on_schedule": "/api/{model_slug}/getCompletedOnSchedule/{intYear}",
        }

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value from
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :rtype: None
        """
        return setattr(self, key, value)

    def insert_assessment(self, app: Application) -> Optional["Assessment"]:
        """
        Function to create a new assessment in RegScale and returns the new assessment's ID

        :param Application app: Application object
        :return: New Assessment object created in RegScale
        :rtype: Optional[Assessment]
        """
        api = Api()
        url = f"{app.config['domain']}/api/assessments"
        response = api.post(url=url, json=self.dict())
        if not response.ok:
            app.logger.debug(response.status_code)
            app.logger.error(f"Failed to insert Assessment.\n{response.text}")
        return Assessment(**response.json()) if response.ok else None

    @classmethod
    def bulk_insert(
        cls,
        app: Application,
        assessments: list["Assessment"],
        max_workers: int = 5,
    ) -> list["Assessment"]:
        """
        Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param list[Assessment] assessments: Assessment List
        :param int max_workers: Max Workers, defaults to 5
        :return: List of Assessments created in RegScale
        :rtype: list["Assessment"]
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            workers = [
                executor.submit(
                    assessment.create,
                )
                for assessment in assessments
            ]
        return list(filter(None, [worker.result() for worker in workers]))

    @staticmethod
    def fetch_all_assessments(app: Application) -> list["Assessment"]:
        """
        Function to retrieve all assessments from RegScale

        :param Application app: Application Object
        :return: List of assessments from RegScale
        :rtype: list[Assessment]
        """
        query = f"""
            query {{
              assessments (take: 50, skip: 0) {{
                items {{
                  {Assessment.build_graphql_fields()}
                }}
                pageInfo {{
                  hasNextPage
                }}
                totalCount
              }}
            }}
        """
        api = Api()
        try:
            app.logger.info("Retrieving all assessments in RegScale...")
            existing_assessments = api.graph(query=query)["assessments"]["items"]
            app.logger.info("%i assessment(s) retrieved from RegScale.", len(existing_assessments))
        except (JSONDecodeError, KeyError):
            existing_assessments = []
        return [Assessment(**assessment) for assessment in existing_assessments]

    @classmethod
    def get_all_by_master(cls, master_id: int) -> List["Assessment"]:
        """
        Get a list of objects by master assessment.

        :param int master_id: The ID of the Master Assessment/ConMon
        :return: A list Assessment objects
        :rtype: List[Assessment]
        """
        endpoint = cls.get_endpoint("get_all_by_master").format(intMaster=master_id)
        return cls._handle_list_response(cls._get_api_handler().get(endpoint=endpoint))

    @staticmethod
    def fetch_all_assessments_by_parent(
        app: Application,
        parent_id: int,
        parent_module: str,
        org_and_facil: Optional[bool] = False,
    ) -> dict:
        """
        Function to retrieve all assessments from RegScale by parent

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :param Optional[bool] org_and_facil: If True, return org and facility names, defaults to False
        :return: GraphQL response from RegScale
        :rtype: dict
        """
        api = Api()
        # The indentation is important here
        org_and_facil_query = """
                  facility {
                    name
                  }
                  org {
                    name
                  }
        """
        body = f"""
            query {{
              assessments (skip: 0, take: 50, where: {{parentId: {{eq: {parent_id}}} parentModule: {{eq: "{parent_module}"}}}}) {{
                items {{
                  id
                  title
                  leadAssessor {{
                    firstName
                    lastName
                    userName
                  }}
                  {org_and_facil_query if org_and_facil else ""}
                  assessmentType
                  plannedStart
                  plannedFinish
                  status
                  actualFinish
                  assessmentResult
                  parentId
                  parentModule
                }}
                totalCount
                pageInfo {{
                  hasNextPage
                }}
              }}
            }}
        """
        assessments = api.graph(query=body)
        if parent_module not in [
            "securityplans",
            "incidents",
            "policies",
            "components",
            "requirements",
            "supplychain",
        ]:
            return assessments

        replacements = {
            "securityplans": "securityPlanId",
            "incidents": "incidentId",
            "policies": "policyId",
            "components": "componentId",
            "requirements": "requirementId",
            "supplychain": "supplyChainId",
        }
        if replacement_key := replacements.get(parent_module):
            body = body.replace(
                f'parentId: {{eq: {parent_id}}} parentModule: {{eq: "{parent_module}"}}',
                f"{replacement_key}: {{eq: {parent_id}}}",
            )
        return {**assessments, **api.graph(query=body)}

    @classmethod
    def get_sort_position_dict(cls) -> dict:
        """
        Overrides the base method.

        :return: dict The sort position in the list of properties
        :rtype: dict
        """
        return {
            "id": 1,
            "leadAssessorId": 2,
            "title": 3,
            "assessmentType": 4,
            "plannedStart": 5,
            "plannedFinish": 6,
            "status": 7,
            "facilityId": 8,
            "orgId": 9,
            "assessmentResult": 10,
            "actualFinish": 11,
            "assessmentReport": 12,
            "masterId": 13,
            "complianceScore": 14,
            "targets": 15,
            "automationInfo": 16,
            "automationId": 17,
            "metadata": 18,
            "assessmentPlan": 19,
            "methodology": 20,
            "rulesOfEngagement": 21,
            "disclosures": 22,
            "scopeIncludes": 23,
            "scopeExcludes": 24,
            "limitationsOfLiability": 25,
            "documentsReviewed": 26,
            "activitiesObserved": 27,
            "fixedDuringAssessment": 28,
            "summaryOfResults": 29,
            "oscalsspId": 30,
            "oscalComponentId": 31,
            "controlId": 32,
            "requirementId": 33,
            "securityPlanId": 34,
            "projectId": 35,
            "supplyChainId": 36,
            "policyId": 37,
            "componentId": 38,
            "incidentId": 39,
            "parentId": 40,
            "parentModule": 41,
            "isPublic": 42,
            "verificationStatus": 43,
            "otherIdentifier": 44,
        }

    @classmethod
    def get_enum_values(cls, field_name: str) -> list:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: list of strings
        :rtype: list
        """
        if field_name == "assessmentType":
            return [assessment_type.value for assessment_type in AssessmentType]
        if field_name == "status":
            return [status.value for status in AssessmentStatus]
        if field_name == "assessmentResult":
            return [result for result in AssessmentResultsStatus]
        return cls.get_bool_enums(field_name)

    @classmethod
    def get_lookup_field(cls, field_name: str) -> str:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: str the field name to look up
        :rtype: str
        """
        lookup_fields = {
            "leadAssessorId": "user",
            "leadAssessor": "user",
            "facilityId": "facilities",
            "facility": "facilities",
            "orgId": "organizations",
            "org": "organizations",
            "parentModule": "module",
            "controlId": "",
            "requirementId": "",
            "securityPlanId": "",
            "projectId": "",
            "supplyChainId": "",
            "policyId": "",
            "componentId": "",
            "incidentId": "",
        }
        if field_name in lookup_fields.keys():
            return lookup_fields[field_name]
        return ""

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: bool if the field should be formatted as a date
        :rtype: bool
        """
        return field_name in ["plannedStart", "plannedFinish", "actualFinish"]

    @classmethod
    def get_export_query(cls, app: Application, parent_id: int, parent_module: str) -> list:
        """
        Overrides the base method.

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :return: list GraphQL response from RegScale
        :rtype: list
        """
        existing_assessment_data = cls.fetch_all_assessments_by_parent_for_export(app, parent_id, parent_module, True)
        if (
            existing_assessment_data["assessments"]["totalCount"] > 0
        ):  # Checking to see if assessment exists for selected RegScale Id and RegScale Module.
            return existing_assessment_data["assessments"]["items"]
        return []

    @classmethod
    def use_query(cls) -> bool:
        """
        Overrides the base method.

        :return: bool
        :rtype: bool
        """
        return True

    @classmethod
    def get_extra_fields(cls) -> list:
        """
        Overrides the base method.

        :return: list of extra field names
        :rtype: list
        """
        return ["leadAssessor", "facility", "org"]

    @staticmethod
    def fetch_all_assessments_by_parent_for_export(
        app: Application,
        parent_id: int,
        parent_module: str,
        org_and_facil: Optional[bool] = False,
    ) -> dict:
        """
        Function to retrieve all assessments from RegScale by parent

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :param Optional[bool] org_and_facil: If True, return org and facility names, defaults to False
        :return: GraphQL response from RegScale
        :rtype: dict
        """
        api = Api()
        body = f"""
            query {{
              assessments (skip: 0, take: 50, where: {{parentId: {{eq: {parent_id}}} parentModule: {{eq: "{parent_module}"}}}}) {{
                items {{
                  id
                  title
                  leadAssessorId
                  facilityId
                  orgId
                  assessmentType
                  plannedStart
                  plannedFinish
                  status
                  actualFinish
                  assessmentResult
                  parentId
                  parentModule
                }}
                totalCount
                pageInfo {{
                  hasNextPage
                }}
              }}
            }}
        """
        assessments = api.graph(query=body)
        if parent_module not in [
            "securityplans",
            "incidents",
            "policies",
            "components",
            "requirements",
            "supplychain",
        ]:
            return assessments

        replacements = {
            "securityplans": "securityPlanId",
            "incidents": "incidentId",
            "policies": "policyId",
            "components": "componentId",
            "requirements": "requirementId",
            "supplychain": "supplyChainId",
        }
        if replacement_key := replacements.get(parent_module):
            body = body.replace(
                f'parentId: {{eq: {parent_id}}} parentModule: {{eq: "{parent_module}"}}',
                f"{replacement_key}: {{eq: {parent_id}}}",
            )
        return {**assessments, **api.graph(query=body)}

    @classmethod
    def is_required_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: field name to check
        :return: bool indicating if the field is required
        :rtype: bool
        """
        return field_name in ["plannedStart", "plannedFinish"]
