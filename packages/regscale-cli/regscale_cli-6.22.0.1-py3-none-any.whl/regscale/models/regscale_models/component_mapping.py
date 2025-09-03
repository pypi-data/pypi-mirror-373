"""This module contains the ComponentMapping model."""

import logging
from typing import Optional, Dict

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.mixins.parent_cache import PlanCacheMixin

logger = logging.getLogger(__name__)


class ComponentMapping(RegScaleModel, PlanCacheMixin["ComponentMapping"]):
    _module_slug = "componentmapping"
    _parent_id_field = "securityPlanId"
    _unique_fields = [
        ["componentId", "securityPlanId"],
    ]

    # New class attributes
    _graph_query_name = "componentMappings"
    _graph_plan_id_path = "securityPlanId"

    id: int = 0
    uuid: Optional[str] = None
    securityPlanId: int
    componentId: int
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    tenantsId: int = 1
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ComponentMapping model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(get_all_by_parent="/api/{model_slug}/getMappingsAsComponents/{intParentID}")

    @classmethod
    def cast_list_object(
        cls,
        item: Dict,
        parent_id: Optional[int] = None,
        parent_module: Optional[str] = None,
    ) -> "ComponentMapping":
        """
        Cast list of items to class instances.

        :param Dict item: item to cast
        :param Optional[int] parent_id: Parent ID, defaults to None
        :param Optional[str] parent_module: Parent module, defaults to None
        :return: Class instance created from the item
        :rtype: "ComponentMapping"
        """
        item["securityPlanId"] = parent_id
        item["id"] = item["mappingId"]
        return cls(**item)
