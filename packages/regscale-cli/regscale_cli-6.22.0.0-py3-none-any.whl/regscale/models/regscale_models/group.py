"""
This module contains the Group model class that represents a group in the RegScale application.
"""

import logging
from typing import Optional, List, Tuple, cast

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.utils.decorators import deprecated
from regscale.models.regscale_models.regscale_model import RegScaleModel, T
from regscale.models.regscale_models.user import User
from regscale.models.regscale_models.user_group import UserGroup

logger = logging.getLogger("regscale")


class Group(RegScaleModel):
    _module_slug = "groups"

    id: Optional[int] = None
    name: Optional[str] = None
    userGroups: Optional[List[UserGroup]] = None
    activated: Optional[bool] = True
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: Optional[bool] = True
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Group model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_groups="/api/{model_slug}",
            change_group_status="/api/{model_slug}/changeGroupStatus/{id}/{strActivated}",
            find_groups_by_user="/api/{model_slug}/findGroupsByUser/{strUser}",
            filter_groups="/api/{model_slug}/filterGroups/{strName}/{strActivated}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            find_users_by_group="/api/{model_slug}/findUsersByGroup/{intGroupId}",
        )

    @classmethod
    @deprecated("Use UserGroup.get_users_by_group instead")
    def get_users_in_group(cls, name: str) -> Tuple[List[User], int]:
        """
        Get a list of users in a group.

        :param str name: The name of the group
        :return: A list of users
        :rtype: Tuple[List[User], int]
        """
        group_list_resp = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_groups").format(model_slug=cls._module_slug)
        )
        group_id = 0
        if group_list_resp and group_list_resp.ok:
            group_list = group_list_resp.json()
            for group in group_list:
                if group.get("name") == name:
                    group_id = group.get("id")
                    break

        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("find_users_by_group").format(model_slug=cls._module_slug, intGroupId=group_id)
        )
        if response and response.ok:
            users = [User(**user) for user in response.json()]
            for user in users:
                # add delegates to users list
                users.extend(user.get_delegates(user.id))
            return users, group_id
        else:
            logger.error(f"Failed to get users in group {name}")
            return [], group_id

    @classmethod
    def get_group_by_name(cls, name: str) -> Optional["Group"]:
        """
        Get a group by name
        :param name: The name of the group
        :return: The group
        :rtype: Optional[Group]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_groups").format(model_slug=cls._module_slug)
        )
        if response and response.ok:
            group_list = response.json()
            for group in group_list:
                if group.get("name") == name:
                    return cls(**group)
        else:
            cls.log_response_error(response=response)
        return None

    @classmethod
    def get_group_list(cls) -> List["Group"]:
        """
        Get a list of groups
        :return: A list of groups
        :rtype: List[Group]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_groups").format(model_slug=cls._module_slug)
        )
        return cast(List[T], cls._handle_list_response(response))

    @classmethod
    def find_groups_by_user(cls, user: str) -> List["Group"]:
        """
        Find groups by user
        :param user: The user ID
        :return: A list of groups
        :rtype: List[Group]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("find_groups_by_user").format(model_slug=cls._module_slug, strUser=user)
        )
        return cast(List[T], cls._handle_list_response(response))

    @classmethod
    def filter_groups(
        cls, name: str, activated: str, sort_by: str, direction: str, page: int, page_size: int
    ) -> List["Group"]:
        """
        Filter groups
        :param name: The name of the group
        :param activated: The activation status
        :param sort_by: The field to sort by
        :param direction: The sort direction
        :param page: The page number
        :param page_size: The page size
        :return: A list of groups
        :rtype: List[Group]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("filter_groups").format(
                model_slug=cls._module_slug,
                strName=name,
                strActivated=activated,
                strSortBy=sort_by,
                strDirection=direction,
                intPage=page,
                intPageSize=page_size,
            )
        )
        return cast(List[T], cls._handle_list_response(response))

    @classmethod
    def find_users_by_group(cls, group_id: int) -> List[User]:
        """
        Find users by group
        :param group_id: The group ID
        :return: A list of users
        :rtype: List[User]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("find_users_by_group").format(model_slug=cls._module_slug, intGroupId=group_id)
        )
        if response and response.ok:
            return [User(**o) for o in response.json()]
        else:
            cls.log_response_error(response=response)
        return []
