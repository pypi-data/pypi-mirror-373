from typing import List

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class FunctionalRole(RegScaleModel):
    """
    Functional Role Model
    """

    _module_slug = "functionalroles"

    id: int = 0
    role: str

    @classmethod
    def get_list(cls) -> List["FunctionalRole"]:
        """
        Get list of Functional Roles

        :return: list of Functional Roles
        :rtype: List["FunctionalRole"]
        """
        return cls._handle_list_response(cls._get_api_handler().get(cls.get_endpoint("get_list")))

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the FunctionalRole

        :return: Additional endpoints for the FunctionalRole
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_list="/api/{model_slug}/getList",
        )
