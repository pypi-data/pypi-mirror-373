"""
UserGroup model for the RegScale API.
"""

from typing import Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class UserGroup(RegScaleModel):
    _module_slug = "userGroups"

    id: Optional[int] = None
    groupsId: int
    userId: str
    isPublic: Optional[bool] = True
    tenantsId: Optional[int] = 1
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the UserGroup model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            filter_user_groups="/api/{model_slug}/filterUserGroups/{intGroupId}/{intPage}/{intPageSize}",
            # Get the list of users in the specified group (GET)
            get_users_by_group="/api/userGroups/getUsersByGroup/{intGroupId}",
            # Get the list of groups for a given user (GET)
            get_groups_by_user="/api/userGroups/getGroupsByUser/{strUserId}",
        )

    @classmethod
    def get_users_by_group(cls, group_id: int):
        """
        Get the list of users in the specified group.

        :param group_id: The group ID
        :return: A list of users
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_users_by_group").format(intGroupId=group_id)
        )
        if response and response.ok:
            return response.json()
        return []
