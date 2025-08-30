"""StakeHolders pydantic BaseModel."""

import logging
import warnings
from typing import Optional
from urllib.parse import urljoin

from pydantic import field_validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class StakeHolder(RegScaleModel):
    """StakeHolders model"""

    _module_slug = "stakeholders"

    id: int = 0
    parentId: int  # Required
    parentModule: str  # Required
    name: Optional[str] = ""
    shortname: Optional[str] = ""
    title: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    otherID: Optional[str] = ""
    notes: Optional[str] = ""

    @classmethod
    @field_validator("email", "shortname", "notes", mode="before", check_fields=True)
    def convert_email_none_to_empty_str(cls, value: Optional[str]) -> str:
        """
        Convert a none value for email, shortname adn notes to an empty string.

        :param Optional[str] value: The value for the field
        :return: The email value or an empty string
        :rtype: str
        """
        return value if value is not None else ""

    def post(self, app: Application) -> Optional[dict]:
        """
        Post a StakeHolders to RegScale

        This method is deprecated, use 'create' method instead

        :param Application app: The application instance
        :return: The response from the API or None
        :rtype: Optional[dict]
        """
        warnings.warn(
            "The 'post' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )
        api = Api()
        url = urljoin(app.config.get("domain", ""), "/api/stakeholders")
        data = self.dict()
        response = api.post(url, json=data)
        return response.json() if response.ok else None
