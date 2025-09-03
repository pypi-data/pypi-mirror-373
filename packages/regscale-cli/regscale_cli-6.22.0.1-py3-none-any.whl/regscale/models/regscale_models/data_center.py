"""DataCenter model for RegScale."""

import warnings
from urllib.parse import urljoin

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel


class DataCenter(RegScaleModel):
    """DataCenter pydantic BaseModel."""

    _module_slug = "datacenters"

    id: int = 0
    uuid: str = ""
    facilityId: int
    parentId: int
    parentModule: str
    isPublic: bool = True
    facility: str = ""

    def post(self, app: Application) -> dict:
        """
        Post a DataCenter to RegScale

        :param Application app: The application instance
        :return: The response from the API
        :rtype: dict
        """
        warnings.warn(
            "The 'post' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )
        api = Api()
        url = urljoin(app.config.get("domain", ""), "/api/datacenters")
        data = self.dict()
        response = api.post(url, json=data)
        return response.json()
