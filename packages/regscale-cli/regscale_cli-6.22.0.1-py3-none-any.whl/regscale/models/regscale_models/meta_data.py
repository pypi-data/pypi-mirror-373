"""Metadata model for RegScale"""

from typing import List, Optional

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from .regscale_model import RegScaleModel


class Metadata(RegScaleModel):
    """RegScale Metadata class"""

    _module_slug = "metadata"

    id: Optional[int] = None
    isPublic: bool = True  # Required as boolean
    active: bool = True  # Required as boolean
    readOnly: bool = False  # Required as boolean
    field: Optional[str] = None
    value: Optional[str] = None
    type: Optional[str] = None
    module: Optional[str] = None
    tenantsId: int = 1
    lastUpdatedById: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: str = Field(default_factory=get_current_datetime)  # Required as string
    dateLastUpdated: str = Field(default_factory=get_current_datetime)  # Required as string
    dateLastUpdated: str = Field(default_factory=get_current_datetime)  # Required as string
    mappedValue: Optional[str] = None
    externalKey: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Metadata model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_grouped="/api/{model_slug}/getAllGrouped",
            filter_metadata="/api/{model_slug}/filterMetadata/{strModule}/{strField}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            get_metadata_by_module_field="/api/{model_slug}/getMetadata/{strModule}/{strField}",
            get_metadata_by_module="/api/{model_slug}/getMetadata/{strModule}",
            get_seeding_options="/api/{model_slug}/getSeedingOptions",
            reseed="/api/{model_slug}/reseed/{strModule}",
            toggle_metadata="/api/{model_slug}/toggleMetadata/{intId}/{bToggle}",
        )

    @classmethod
    def get_metadata_by_module_field(cls, module: str, field: str) -> List["Metadata"]:
        """
        Retrieves metadata by module and field.

        :param str module: The module
        :param str field: The field
        :return: A list of metadata or None
        :rtype: List[Metadata]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_metadata_by_module_field").format(strModule=module, strField=field)
        )
        return cls._handle_list_response(response)
