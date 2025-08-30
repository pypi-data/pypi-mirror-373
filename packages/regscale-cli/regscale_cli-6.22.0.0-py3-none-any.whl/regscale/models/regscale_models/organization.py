"""Organization model for RegScale."""

from typing import Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class Organization(RegScaleModel):
    """Data Model for Organizations"""

    _module_slug = "organizations"

    id: int = 0
    name: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = "Active"

    @staticmethod
    def _get_additional_endpoints() -> dict:
        """
        Get additional endpoints for the Facility model.

        :return: A dictionary of additional endpoints
        :rtype: dict
        """
        return ConfigDict(
            get_list="/api/{model_slug}/getList",
        )
