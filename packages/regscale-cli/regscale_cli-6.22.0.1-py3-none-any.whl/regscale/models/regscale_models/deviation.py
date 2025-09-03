import concurrent.futures
import logging
from typing import List, Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class Deviation(RegScaleModel):
    """
    Deviation model class
    """

    _module_slug = "deviations"
    _unique_fields = [
        ["parentIssueId", "deviationType", "rationale", "requestedImpactRating", "vulnerabilityId"],
    ]
    _parent_id_field = "parentIssueId"

    parentIssueId: int  # Required
    requestedImpactRating: str  # Required
    deviationType: str  # Required
    rationale: str  # Required

    id: int = 0
    otherIdentifier: Optional[str] = None
    isPublic: bool = True
    uuid: Optional[str] = None
    dateSubmitted: Optional[str] = None
    evidenceDescription: Optional[str] = None
    operationalImpacts: Optional[str] = None
    riskJustification: Optional[str] = None
    tmpExploitCodeMaturity: Optional[str] = None
    tmpRemediationLevel: Optional[str] = None
    tmpReportConfidence: Optional[str] = None
    envConfidentiality: Optional[str] = None
    envIntegrity: Optional[str] = None
    envAvailability: Optional[str] = None
    envAttackVector: Optional[str] = None
    envAttackComplexity: Optional[str] = None
    envPrivilegesRequired: Optional[str] = None
    envUserInteraction: Optional[str] = None
    envScope: Optional[str] = None
    envModConfidentiality: Optional[str] = None
    envModIntegrity: Optional[str] = None
    envModAvailability: Optional[str] = None
    vulnerabilityId: Optional[str] = None
    baseScore: Optional[float] = None
    temporalScore: Optional[float] = None
    environmentalScore: Optional[float] = None
    envAttackVectorExplanation: Optional[str] = None
    envAttackComplexityExplanation: Optional[str] = None
    envPrivilegesRequiredExplanation: Optional[str] = None
    envUserInteractionExplanation: Optional[str] = None
    envConfidentialityExplanation: Optional[str] = None
    envIntegrityExplanation: Optional[str] = None
    envAvailabilityExplanation: Optional[str] = None
    tmpExploitCodeMaturityExplanation: Optional[str] = None
    tmpRemediationLevelExplanation: Optional[str] = None
    tmpReportConfidenceExplanation: Optional[str] = None
    baseSeverity: Optional[str] = None
    temporalSeverity: Optional[str] = None
    environmentalSeverity: Optional[str] = None
    finalVectorString: Optional[str] = None
    overallRiskReductionExplanation: Optional[str] = None
    additionalInformation: Optional[str] = None
    drNumber: Optional[str] = None
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    @classmethod
    def mapping(cls) -> dict:
        """
        Get the mapping for the Deviation model.

        :return: A dictionary of mappings
        :rtype: dict
        """
        return {
            "FP": "False Positive (FP)",
            "FP_RA": "False Positive (FP)",
            "OR": "Operational Requirements (OR)",
            "OR_RA": "RA & OR",
            "OR RA": "RA & OR",
            "RA": "Risk Adjustment (RA)",
        }

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Deviations model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_by_issue="/api/{model_slug}/getbyIssue/{intParentID}/{includeDrNumber}",
            get_all_by_security_plan="/api/{model_slug}/getAllBySecurityPlan/{sspId}/{includeDrNumber}",
            export_deviation_by_ssp="/api/{model_slug}/getAllByPart/{intParentID}/{strModule}/{strType}/{strPart}",
        )

    @classmethod
    def get_by_issue(cls, issue_id: int, include_dr_number: bool = True) -> Optional["Deviation"]:
        """
        Get a deviation by issue id

        :param int issue_id: Ths issue to search for
        :param bool include_dr_number: Include DR number in the response
        :return: A list of deviations
        :rtype: Optional["Deviation"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_issue").format(intParentID=issue_id, includeDrNumber=include_dr_number)
        )
        if response and response.status_code == 200:
            return cls(**response.json())
        return None

    @classmethod
    def get_by_security_plan(cls, ssp_id: int, include_dr_number: bool = True) -> List["Deviation"]:
        """
        Get a list of deviations by ssp id

        :param int ssp_id: Ths ssp to search for
        :return: A list of deviations
        :rtype: Optional["Deviation"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_security_plan").format(
                sspId=ssp_id, includeDrNumber=include_dr_number
            )
        )
        if response and response.status_code == 200:
            return [cls(**res) for res in response.json()]
        return []

    @classmethod
    def get_dr_ids(cls, issue_id: int) -> Optional["Property"]:
        """
        Get a list of control implementations by plan ID.

        :param int issue_id: Issue Id
        :return: A single Property object with the DR number if it exists or None
        :rtype: Optional[Property]
        """
        from regscale.models import Property

        properties = [
            prop
            for prop in Property.get_all_by_parent(parent_id=issue_id, parent_module="issues")
            if prop.key == "dr_number"
        ]
        if properties:
            return properties.pop()
        return None

    @classmethod
    def get_existing_deviations_by_ssp(
        cls, ssp_id: int, issue_ids: List[int], poam_map: dict = None
    ) -> List["Deviation"]:
        """
        Get existing deviations by SSP

        :param int ssp_id: Security Plan ID
        :param List[int] issue_ids: List of issue IDs
        :param dict poam_map: POAM map, optional
        :return: list of deviations
        :rtype: List["Deviation"]
        """
        # poam_map description:
        # The main dict key of `id_other_identifier_map` are the `otherIdentifier` of each issue.
        # The values of `id_other_identifier_map` are dictionaries themselves, with the following structure:
        # The values are dictionaries with the following keys
        # - `id`: The ID of the issue in RegScale
        # - `dr_number`: The DR number of the issue

        # CAUTION: This needs to be moved to platform specific code (see REG-9998)
        logger.info("Looking up existing RegScale deviations for SSP# %i.. ", ssp_id)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            properties = (
                [prop for prop in list(executor.map(cls.get_dr_ids, issue_ids)) if prop] if not poam_map else []
            )
            deviations = [dev for dev in list(executor.map(cls.get_by_issue, issue_ids)) if dev]

        for deviation in deviations:
            if not poam_map:
                prop = [prop for prop in properties if prop.parentId == deviation.parentIssueId]
                if prop:
                    deviation.extra_data = {"dr_number": prop.pop().value}
                else:
                    deviation.extra_data = {"dr_number": None}
            else:
                match = [val for val in poam_map.values() if val.get("id") == deviation.parentIssueId]
                if match:
                    deviation.extra_data = {"dr_number": match.pop().get("dr_number")}

        return deviations
