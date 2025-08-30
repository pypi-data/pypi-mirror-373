"""Provide a SystemRoleExternalAssignments model."""

import warnings
from typing import Optional
from urllib.parse import urljoin

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel


class SystemRoleExternalAssignment(RegScaleModel):
    """SystemRoleExternalAssignments model"""

    _module_slug = "systemRoleExternalAssignments"

    id: int = 0
    uuid: str = ""
    stakeholderId: int = 0
    roleId: int = 0

    def post(self, app: Application) -> Optional["SystemRoleExternalAssignment"]:
        """
        Post a SystemRoleExternalAssignments to RegScale

        This method is deprecated, use 'create' method instead

        :param Application app: The application instance
        :return: The response from the API or None
        :rtype: Optional[SystemRoleExternalAssignment]
        """
        warnings.warn(
            "The 'post' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )
        api = Api()
        url = urljoin(app.config.get("domain", ""), "/api/systemRoleExternalAssignments")
        data = self.dict()
        response = api.post(url, json=data)
        return SystemRoleExternalAssignment(**response.json()) if response.ok else None
