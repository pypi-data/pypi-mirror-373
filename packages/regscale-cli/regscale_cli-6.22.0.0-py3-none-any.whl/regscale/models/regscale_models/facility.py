"""Facility model for RegScale."""

from typing import Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class Facility(RegScaleModel):
    """Data Model for Facilities"""

    _module_slug = "facilities"

    id: int = 0
    name: str = ""
    description: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zipCode: str = ""
    status: str = ""
    latitude: float = 0
    longitude: float = 0
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: bool = True
    dateLastUpdated: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> dict:
        """
        Get additional endpoints for the Facility model.

        :return: A dictionary of additional endpoints
        :rtype: dict
        """
        return ConfigDict(
            get_list="/api/{model_slug}/get_list",
        )
