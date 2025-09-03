"""
This module contains the Business Impact Assessment model for RegScale.
"""

from typing import List

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class BusinessImpactAssessment(RegScaleModel):
    """RegScale Business Impact Assessment

    :return: RegScale Business Impact Assessment
    """

    _module_slug = "business-impact-assessments"
    _module_string = "business-impact-assessments"
    # Should we include baseline, ruleId, check, and results in unique fields?
    _unique_fields = [
        [
            "riskId",
            "category",
        ],
    ]
    _parent_id_field = "riskId"
    # Required
    id: int = 0
    isPublic: bool = True
    uuid: str = ""
    category: str = ""
    probability: str = ""
    consequence: str = ""
    notes: str = ""
    riskType: str = ""
    riskScore: int = 0
    riskId: int = 0

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Catalogues model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_risk="/api/{model_slug}/getAllByRisk/{intID}",
            get_all_by_risk_and_type="/api/{model_slug}/getAllByRiskAndType/{intID}/{strType}",
        )

    @classmethod
    def get_all_by_risk(cls, risk_id: int) -> List["BusinessImpactAssessment"]:
        """
        Get all Business Impact Assessments by risk ID
        """
        endpoint = cls.get_endpoint("get_all_by_risk").format(model_slug=cls.get_module_slug(), intID=risk_id)
        res = cls._handle_list_response(cls._get_api_handler().get(endpoint))
        return res

    @classmethod
    def get_all_by_risk_and_type(cls, risk_id: int, risk_type: str) -> List["BusinessImpactAssessment"]:
        """
        Get all Business Impact Assessments by risk ID and type
        """
        endpoint = cls.get_endpoint("get_all_by_risk_and_type").format(
            model_slug=cls.get_module_slug(), intID=risk_id, strType=risk_type
        )
        res = cls._handle_list_response(cls._get_api_handler().get(endpoint))
        return res
