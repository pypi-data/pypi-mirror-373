from typing import List, Type, TypeVar

import pytest
from unittest.mock import patch
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models import regscale_models

T = TypeVar("T", bound=RegScaleModel)


@pytest.fixture
def mock_regscale_models(mock_api_handler):
    """
    Fixture to patch various methods for RegScaleModel and its subclasses to use model cache and avoid API calls.

    :param mock_api_handler: Mocked API handler
    :yield: None
    """

    def mock_get_all_by_parent(cls: Type[T], parent_id: int, *args, **kwargs) -> List[T]:
        """
        Mock method to get all objects by parent ID.

        :param Type[T] cls: The class of the objects to retrieve
        :param int parent_id: The ID of the parent object
        :return: List of objects matching the parent ID and other criteria
        """
        parent_module = kwargs.get("parent_module")

        return [
            obj
            for obj in cls._object_cache.values()
            if isinstance(obj, cls)
            and parent_id == getattr(obj, cls._parent_id_field)
            and (not parent_module or obj.parentModule == parent_module)
        ]

    def mock_issue_find_by_other_identifier(other_identifier: str) -> List[regscale_models.Issue]:
        """
        Mock method to find issues by other identifier.

        :param str other_identifier: The other identifier to search for
        :return: List of Issue objects matching the other identifier
        """
        return [
            issue
            for issue in regscale_models.Issue._object_cache.values()
            if isinstance(issue, regscale_models.Issue) and issue.otherIdentifier == other_identifier
        ]

    def mock_vulnerability_mapping_find_by_issue(
        issue_id: int, status: str = "all"
    ) -> List[regscale_models.VulnerabilityMapping]:
        """
        Mock method to find vulnerability mappings by issue ID and status.

        :param int issue_id: The ID of the issue to search for
        :param str status: The status of the vulnerability mapping (default: "all")
        :return: List of VulnerabilityMapping objects matching the criteria
        """
        return [
            mapping
            for mapping in regscale_models.VulnerabilityMapping._object_cache.values()
            if isinstance(mapping, regscale_models.VulnerabilityMapping)
            and (status == "all" or mapping.status.lower() == status.lower())
        ]

    def mock_get_object(cls: Type[T], object_id: int) -> T:
        """
        Mock method to get an object by its ID.

        :param Type[T] cls: The class of the object to retrieve
        :param int object_id: The ID of the object to retrieve
        :return: The object if found, None otherwise
        """
        # Try to get the object from the cache first
        cached_object = next((obj for obj in cls._object_cache.values() if obj.id == object_id), None)
        if cached_object:
            return cached_object

        # If not in cache, simulate an API call (you might want to raise an exception here instead)
        return None

    with patch.object(RegScaleModel, "get_all_by_parent", classmethod(mock_get_all_by_parent)), patch.object(
        regscale_models.Issue, "find_by_other_identifier", mock_issue_find_by_other_identifier
    ), patch.object(
        regscale_models.VulnerabilityMapping, "find_by_issue", mock_vulnerability_mapping_find_by_issue
    ), patch.object(
        RegScaleModel, "get_object", classmethod(mock_get_object)
    ):
        yield
