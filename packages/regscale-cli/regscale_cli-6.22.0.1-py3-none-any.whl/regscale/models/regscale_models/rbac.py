from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel
from pydantic import Field, ConfigDict
import logging

logger = logging.getLogger(__name__)


class RBAC(RegScaleModel):
    _module_slug = "rbac"
    id: Optional[int] = Field(alias="rbacId")
    moduleId: Optional[int] = None
    parentId: Optional[int] = None
    groupId: Optional[int] = None
    permissionType: Optional[int] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the RBAC model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/{moduleId}/{parentId}",
            add="/api/{model_slug}/add/{moduleId}/{parentId}/{groupId}/{permissionType}",
            public="/api/{model_slug}/public/{moduleId}/{parentId}/{public}",
            none_standard_delete="/api/{model_slug}/{moduleId}/{parentId}/{rbacId}",
            reset="/api/{model_slug}/reset/{moduleId}/{parentId}",
        )

    @classmethod
    def delete(cls, module_id: int, parent_id: int, rbac_id: int) -> bool:
        """
        Delete a RBAC entry.

        :param int module_id: The ID of the module
        :param int parent_id: The ID of the parent
        :param int rbac_id: The ID of the RBAC entry
        :return: True if the RBAC entry was deleted, False otherwise
        :rtype: bool
        """
        response = cls._get_api_handler().delete(
            endpoint=cls.get_endpoint("none_standard_delete").format(
                model_slug=cls._module_slug,
                moduleId=module_id,
                parentId=parent_id,
                rbacId=rbac_id,
            )
        )
        if response and response.ok:
            return True
        else:
            cls.log_response_error(response=response)

    @classmethod
    def get_all_by_parent(cls, module_id: int, parent_id: int) -> list:
        """
        Get all RBAC entries by parent. Override from regscaleModel due to different endpoint params on api call.

        :param int module_id: The ID of the module
        :param int parent_id: The ID of the parent
        :return: A list of RBAC entries
        :rtype: list
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(
                model_slug=cls._module_slug,
                moduleId=module_id,
                parentId=parent_id,
            )
        )
        if response and response.ok:
            logger.info(f"Response: {response.json()}")
            return [cls(**o) for o in response.json()]
        else:
            cls.log_response_error(response=response)
            return []

    @classmethod
    def add(cls, module_id: int, parent_id: int, group_id: int, permission_type: int) -> bool:
        """
        Add a new RBAC entry.

        :param int module_id: The ID of the module
        :param int parent_id: The ID of the parent
        :param int group_id: The ID of the group
        :param int permission_type: The permission type
        :return: True if the RBAC entry was added, False otherwise
        :rtype: bool
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("add").format(
                model_slug=cls._module_slug,
                moduleId=module_id,
                parentId=parent_id,
                groupId=group_id,
                permissionType=permission_type,
            )
        )
        if response and response.ok:
            return True
        else:
            cls.log_response_error(response=response)
            return False

    @classmethod
    def public(cls, module_id: int, parent_id: int, is_public: int = 0) -> bool:
        """
        Add a new RBAC entry.

        :param int module_id: The ID of the module
        :param int parent_id: The ID of the parent
        :param int is_public: The public flag 0 is public and 1 is private
        :return: True if the RBAC entry was added, False otherwise
        :rtype: bool
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("public").format(
                model_slug=cls._module_slug,
                moduleId=module_id,
                parentId=parent_id,
                public=is_public,
            )
        )
        if response and response.ok:
            return True
        else:
            cls.log_response_error(response=response)
            return False

    @classmethod
    def reset(cls, module_id: int, parent_id: int) -> bool:
        """
        Proliferates the RBAC entry to all its children

        :param int module_id: The ID of the module
        :param int parent_id: The ID of the parent
        :return: True if the RBAC entry was added, False otherwise
        :rtype: bool
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("reset").format(
                model_slug=cls._module_slug, moduleId=module_id, parentId=parent_id
            )
        )
        if response and response.ok:
            return True
        else:
            cls.log_response_error(response=response)
            return False
