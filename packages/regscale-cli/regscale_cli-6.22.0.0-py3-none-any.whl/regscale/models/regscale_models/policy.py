"""This module contains the Policy models."""

from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class PolicyParameter(RegScaleModel):
    """Policy Parameter Model"""

    _module_slug = "policyparameter"
    _unique_fields = [
        ["policyId", "name"],
    ]
    id: int = 0
    policyId: int
    name: str = ""
    value: str = ""
    default: str = ""


class Policy(RegScaleModel):
    """Policy Model"""

    _module_slug = "policies"
    _unique_fields = [
        ["integrationFindingId", "vulnerabilityId", "status"],
        ["otherIdentifier", "parentModule", "parentId", "status"],
    ]

    id: int = 0
    policyNumber: str = ""
    policyOwnerId: str = ""
    policyType: str = ""
    dateApproved: str = ""
    expirationDate: str = ""
    status: str = ""
    title: str = ""
    description: str = ""
    practiceLevel: str = ""
    processLevel: str = ""
    facilityId: Optional[int] = None
    orgId: int = 0
    parentModule: str = ""
    parentId: int = 0
    isPublic: bool = True
    policyTemplate: str = ""
    policyTemplateId: str = ""
    policyParameters: List[PolicyParameter] = []

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ProfileMapping model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """

        return ConfigDict(  # type: ignore
            get_list="/api/{model_slug}/getList",
        )

    @classmethod
    def get_list(cls) -> List[dict]:
        """
        Get a list of policies.

        :return: A list of policies
        :rtype: List[dict]
        """
        endpoint = cls.get_endpoint("get_list")
        res = cls._get_api_handler().get(endpoint=endpoint)
        return res.json()

    def convert_datetime_to_date_str(self, dt: Optional[datetime]) -> str:
        """
        Convert a datetime object to a date string in the format 'MMM DD, YYYY'.

        :param dt: The datetime object to convert
        :type dt: Optional[datetime]
        :return: The date string in format 'MMM DD, YYYY'
        :rtype: str
        """
        if dt is None:
            return ""
        return dt.strftime("%b %d, %Y")
