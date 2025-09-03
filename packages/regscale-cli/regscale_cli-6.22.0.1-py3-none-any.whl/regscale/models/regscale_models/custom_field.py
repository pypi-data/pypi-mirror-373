#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Custom Fields in the application"""

import logging
from typing import Any, List, Optional

from pydantic import ConfigDict

from regscale.core.app.utils.app_utils import update_keys_to_lowercase_first_letter
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class CustomField(RegScaleModel):
    _module_slug = "customFields"

    id: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = None
    moduleId: Optional[int] = None
    fieldName: Optional[str] = None
    fieldDataType: Optional[str] = None
    active: Optional[bool] = None
    fieldRequired: Optional[bool] = None
    disabled: Optional[bool] = None
    order: Optional[int] = None
    tenantId: int = 1
    dateLastUpdated: Optional[str] = None
    data: Optional[List[Any]] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the CustomField model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            insert="/api/{model_slug}/1",
            get_module_with_tenant="/api/{model_slug}/module/{tenantId}/{moduleId}",
            get_module="/api/{model_slug}/module/{moduleId}",
            get_module_required="/api/{model_slug}/moduleRequired/{moduleId}",
            get_custom_field="/api/{model_slug}/{customFieldId}",
            filter_custom_fields="/api/{model_slug}/{tenantId}/{moduleId}/{strSort}/{strDirection}/{intPage}/{intPageSize}",
            update_batch_post="/api/{model_slug}/update/{tenantId}",
            create_custom_field_post="/api/{model_slug}/{tenantId}",
            update_custom_field_put="/api/{model_slug}/{tenantId}",
            update_sort_order_post="/api/{model_slug}/sortOrder/{moduleId}",
            enable_custom_field_put="/api/{model_slug}/enable/{tenantId}/{customFieldId}/{enabled}",
            require_custom_field_put="/api/{model_slug}/require/{tenantId}/{customFieldId}/{required}",
            get_by_parent="/api/{model_slug}/module/{strModule}",
        )

    @classmethod
    def get_list_by_module_id(cls, module_id: int) -> List["CustomField"]:
        """
        Get a list of custom fields by module ID

        :param int module_id: The ID of the module
        :return: A list of custom fields
        :rtype: List[CustomField]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_module").format(model_slug=cls._module_slug, moduleId=module_id)
        )
        custom_fields = []
        if response and response.ok:
            for custom_field in response.json():
                custom_fields.append(CustomField(**custom_field))
        return custom_fields

    @classmethod
    def get_custom_fields_by_module_id(cls, parent_module_id: int) -> List["CustomField"]:
        """
        Get a list of custom fields by module ID

        :param int parent_module_id: The ID of the module
        :return: List of CustomField objects
        :rtype: List[CustomField]
        """
        custom_fields = CustomField.get_list_by_module_id(module_id=cls.get_module_id())
        for field in custom_fields:
            data_field_list = CustomFieldsData.get_list_by_parent_id_and_module_id(
                parent_id=parent_module_id, module_id=field.moduleId
            )
            for data in data_field_list:
                if data.fieldId == field.id:
                    field.data = data
            if field.data:
                field.data = update_keys_to_lowercase_first_letter(field.data)
        return custom_fields


class CustomFieldsData(RegScaleModel):
    _module_slug = "customFieldsData"
    id: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = None
    moduleId: Optional[int] = None
    parentId: Optional[int] = None
    field: Optional[CustomField] = None
    fieldId: Optional[int] = None
    fieldName: Optional[str] = None
    fieldValue: Optional[str] = None
    fieldDataType: Optional[str] = None
    fieldRequired: Optional[bool] = None
    disabled: Optional[bool] = None
    tenantsId: Optional[int] = None
    dateLastUpdated: Optional[str] = None

    @classmethod
    def get_by_module_id(cls, parent_id: int, module_id: int) -> Optional[List["CustomFieldsData"]]:
        """
        Get a list of custom fields by module ID.

        :param int parent_id: The ID of the module parent id field
        :param int module_id: The ID of the module
        :return: A list of custom fields, None if no custom fields are found
        :rtype: Optional[List[CustomFieldsData]]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_custom_fields_data_get").format(
                model_slug=cls._module_slug, parentId=parent_id, moduleId=module_id
            )
        )
        if response and response.ok:
            return [CustomFieldsData(**data) for data in response.json()]
        return None

    @classmethod
    def get_by_id(cls, cid: int, module_id: int) -> Optional["CustomFieldsData"]:
        """
        Get a list of custom fields by module ID.

        :param int cid: The ID of the custom field
        :param int module_id: The ID of the module
        :return: A list of custom fields, None if no custom fields are found
        :rtype: Optional[CustomFieldsData]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_custom_fields_data").format(
                model_slug=cls._module_slug, id=cid, moduleId=module_id
            )
        )
        if response and response.ok:
            # print(response.json())
            return CustomFieldsData(**response.json())
        return None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the CustomFieldData model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_custom_fields_data="/api/{model_slug}/{id}/{moduleId}",
            update_batch_post="/api/{model_slug}/update",
            create_custom_field_data_post="/api/{model_slug}",
            get_custom_fields_data_get="/api/{model_slug}/createCustomFieldsData/{parentId}/{moduleId}",
            get_by_parent="/api/{model_slug}/{intParentID}/{strModule}",
        )

    @classmethod
    def get_list_by_parent_id_and_module_id(cls, parent_id: int, module_id: int) -> List["CustomFieldsData"]:
        """
        Get a list of custom fields by module ID.

        :param int parent_id: The ID of the parent
        :param int module_id: The ID of the module
        :return: A list of custom field datas
        :rtype: List["CustomFieldsData"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_custom_fields_data_get").format(
                model_slug=cls._module_slug, parentID=parent_id, moduleID=module_id
            )
        )
        custom_fields = []
        if response and response.ok:
            for custom_field_data in response.json():
                custom_fields.append(CustomFieldsData(**custom_field_data))
        return custom_fields

    @classmethod
    def batch_update(cls, custom_data_fields: List["CustomFieldsData"]) -> bool:
        """
        Batch update custom fields data.

        :param List[CustomFieldsData] custom_data_fields: The list of custom fields data
        :return: Whether the batch update was successful
        :rtype: bool
        """
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("update_batch_post").format(model_slug=cls._module_slug),
            data=[custom_data_field.dict() for custom_data_field in custom_data_fields],
        )
        if response and response.ok:
            return True
        else:
            logger.error("Failed to batch update custom fields data")
            return False


class CustomFieldsSelectItem(RegScaleModel):
    _module_slug = "customFieldsSelectItems"

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the CustomFieldSelectItem model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            create_items_post="/api/{model_slug}/items/{tenantId}",
            update_items_put="/api/{model_slug}/items/{tenantId}",
            get_items="/api/{model_slug}/items/{parentId}",
            get_items_for_request="/api/{model_slug}/items/{parentId}/{moduleId}/{requestId}",
            enable_item_put="/api/{model_slug}/enable/{tenantId}/{customFieldSelectItemId}/{enabled}",
        )

    id: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = None
    moduleId: Optional[int] = None
    parentId: Optional[int] = None
    fieldKey: Optional[str] = None
    fieldValue: Optional[str] = None
    tenantsId: Optional[int] = None
    dateLastUpdated: Optional[str] = None
    disabled: Optional[bool] = None
    itemOrder: Optional[int] = None
