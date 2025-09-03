import logging
from typing import Optional, List, Dict

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.search import Search
from regscale.models.regscale_models import Asset
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.regscale_model import T
from regscale.models.regscale_models.mixins.parent_cache import PlanCacheMixin

logger = logging.getLogger(__name__)


class AssetMapping(RegScaleModel, PlanCacheMixin["AssetMapping"]):
    """
    AssetMapping model class.
    """

    _module_slug = "assetmapping"
    _unique_fields = [
        ["componentId", "assetId"],
    ]
    _parent_id_field = "componentId"

    # New class attributes
    _graph_query_name = "assetMappings"
    _graph_plan_id_path = "component.securityPlansId"

    id: Optional[int] = 0
    uuid: Optional[str] = None
    assetId: int
    componentId: int
    createdById: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = True
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1

    @staticmethod
    def get_assets(component_id: int) -> List[T]:
        """
        Get assets for a given component ID.

        :param int component_id: The ID of the component
        :return: A list of assets
        :rtype: List[T]
        """
        asset_mappings = AssetMapping.find_mappings(component_id=component_id)
        assets = []
        for asset_mapping in asset_mappings:
            assets.append(Asset.get_object(object_id=asset_mapping.assetId))
        return assets

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the AssetMapping model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getMappingsAsComponents/{intParentID}",
            filter_asset_mappings="/api/{model_slug}/filterAssetMappings/{intAsset}/{intComp}/{strSearch}/{intPage}/{intPageSize}",
            find_mappings="/api/{model_slug}/findMappings/{intId}",
            get_mappings_as_components="/api/{model_slug}/getMappingsAsComponents/{intId}",
            get_mappings_as_assets="/api/{model_slug}/getMappingsAsAssets/{intId}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
        )

    @classmethod
    def cast_list_object(
        cls,
        item: Dict,
        parent_id: Optional[int] = None,
        parent_module: Optional[str] = None,
    ) -> "AssetMapping":
        """
        Cast list of items to class instances.

        :param Dict item: item to cast
        :param Optional[int] parent_id: Parent ID, defaults to None
        :param Optional[str] parent_module: Parent module, defaults to None
        :return: Class instance created from the item
        :rtype: "AssetMapping"
        """
        item["assetId"] = parent_id or item.get("assetId")
        return cls(**item)

    @classmethod
    def get_all_by_parent(
        cls,
        parent_id: int,
        parent_module: Optional[str] = None,
        search: Optional[Search] = None,
    ) -> List[T]:
        """
        Retrieves all asset mappings for a given parent ID and ONLY Components.

        :param int parent_id: The ID of the parent
        :param Optional[str] parent_module: The module of the parent
        :param Optional[Search] search: The search object, defaults to None
        :return: A list of asset mappings
        :rtype: List[T]
        :returns: A list of asset mappings for the given parent ID
        """
        return cls.find_mappings(parent_id)

    @classmethod
    def find_mappings(cls, component_id: int) -> List[T]:
        """
        Retrieves all component mappings for a given component ID.

        :param int component_id: The ID of the component
        :return: A list of component mappings
        :rtype: List[T]
        """
        cache_key = f"{component_id}:{cls.__name__}"

        # Get the lock for this cache_key
        lock = cls._get_lock(cache_key)

        with lock:
            # Check the cache
            cached_mappings = cls._parent_cache.get(cache_key)
            if cached_mappings is not None:
                return cached_mappings

            # Not cached, make the API call
            response = cls._get_api_handler().get(
                endpoint=cls.get_endpoint("find_mappings").format(model_slug=cls.get_module_slug(), intId=component_id)
            )
            mappings = cls._handle_list_response(response)

            # Cache the mappings
            cls.cache_list_objects(cache_key=cache_key, objects=mappings)

        return mappings

    @classmethod
    def get_mappings_as_components(cls, asset_id: int) -> Optional[List[T]]:
        """
        Retrieves all component mappings for a given asset ID.

        :param int asset_id: The ID of the asset
        :return: A list of component mappings or None
        :rtype: Optional[List[T]]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_mappings_as_components").format(
                model_slug=cls.get_module_slug(), intId=asset_id
            )
        )
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return [cls(**item) for item in response.json()]
        return None

    def get_mappings_as_assets(
        self, component_id: int, sort_by: str, direction: str, page: int, page_size: int
    ) -> Optional[List["AssetMapping"]]:
        """
        Retrieves all asset mappings for a given component ID.

        :param int component_id: The ID of the component
        :param str sort_by: The field to sort by
        :param str direction: The direction of sorting ('asc' or 'desc')
        :param int page: The page number for pagination
        :param int page_size: The number of items per page
        :return: A list of asset mappings or None
        :rtype: Optional[List[AssetMapping]]
        """
        response = self._get_api_handler().get(
            endpoint=self.get_endpoint("get_mappings_as_assets").format(
                model_slug=self._module_slug,
                intId=component_id,
                strSortBy=sort_by,
                strDirection=direction,
                intPage=page,
                intPageSize=page_size,
            )
        )
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return [self.__class__(**item) for item in response.json()]
        return None
