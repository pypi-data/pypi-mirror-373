"""
This module contains the PlanCacheMixin class, which provides caching functionality for objects associated with security plans.

The PlanCacheMixin is a generic class that can be used with any model that has a security plan ID. It offers methods to populate a cache of objects by plan ID and retrieve all objects for a given plan ID.

Classes that inherit from PlanCacheMixin should define two class variables:
- _graph_query_name: A string representing the name of the GraphQL query for the objects.
- _graph_plan_id_path: A dot notation string representing the path to the security plan ID in the GraphQL response.

Example usage:
    class AssetMapping(PlanCacheMixin["AssetMapping"]):
        _graph_query_name = "assetMappings"
        _graph_plan_id_path = "component.securityPlanId"

This mixin is designed to work with the RegScale API and assumes the existence of certain methods like cache_object.
"""

import logging
from typing import Dict, List, TypeVar, Generic, cast, Type, ClassVar

logger = logging.getLogger("regscale")


T = TypeVar("T", bound="PlanCacheMixin")


class PlanCacheMixin(Generic[T]):
    """
    Mixin for caching objects by plan ID.

    This mixin is designed to be used with classes that have a security plan ID.
    It provides a method to populate a cache of objects by plan ID and a method to get all objects for a given plan ID.

    Example:
    class AssetMapping(PlanCacheMixin["AssetMapping"]):
        _graph_query_name = "assetMappings"
        _graph_plan_id_path = "component.securityPlanId"
    """

    _graph_query_name: ClassVar[str]  # Example: "assetMappings"
    _graph_plan_id_path: ClassVar[str]  # Example: "component.securityPlanId"

    @classmethod
    def populate_cache_by_plan(cls: Type[T], plan_id: int) -> None:
        """
        Populate the parent cache using the get_plan_objects method.

        :param int plan_id: Security Plan ID
        :rtype: None
        """
        objects = cls.get_plan_objects(plan_id)
        for obj in objects:
            cls.cache_object(obj)
        logger.debug("Cached %s %s objects.", len(objects), cls.__name__)

    @classmethod
    def get_plan_objects(cls: Type[T], plan_id: int) -> List[T]:
        """
        Get all objects for a given plan ID.

        :param int plan_id: Security Plan ID
        :return: Objects for a given plan ID
        :rtype: List[T]
        """
        plan_id_field = cls._graph_plan_id_path

        # Parse the dot notation to build the where statement
        where_parts = plan_id_field.split(".")
        where_statement = ": {".join(where_parts) + f": {{eq: {plan_id}}}" + "}" * (len(where_parts) - 1)

        search_query = f"""query {{
            {cls._graph_query_name}(skip: 0, take: 50, where: {{{where_statement}}}) {{
                items {{
                    {cls.build_graphql_fields()}
                }}
                totalCount
                pageInfo {{
                    hasNextPage
                }}
            }}
        }}"""
        response = cls._get_api_handler().graph(query=search_query)
        objects = cast(List[T], cls._handle_graph_response(response))
        return objects

    @classmethod
    def build_graphql_fields(cls) -> str:
        """
        Build GraphQL fields for the query.

        :return: GraphQL fields
        :rtype: str
        """
        raise NotImplementedError("Subclasses must implement build_graphql_fields")

    @classmethod
    def cache_object(cls, obj: T) -> None:
        """
        Cache an object.

        :param T obj: Object to cache
        :rtype: None
        """
        raise NotImplementedError("Subclasses must implement cache_object")

    @classmethod
    def _handle_graph_response(cls, response: Dict) -> List[T]:
        """
        Handle GraphQL response.

        :param Dict response: GraphQL response
        :return: List of objects
        :rtype: List[T]
        """
        raise NotImplementedError("Subclasses must implement _handle_graph_response")

    @property
    def _api_handler(self):
        """
        Get API handler.

        :return: API handler
        """
        raise NotImplementedError("Subclasses must implement _api_handler")
