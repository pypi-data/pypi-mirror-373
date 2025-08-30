#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Custom Fields in the application"""

import logging
from typing import Any, List, Optional, Dict

from pydantic import ConfigDict, Field

from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.module import Module

logger = logging.getLogger(__name__)


class FormFieldValue(RegScaleModel):
    _module_slug = "formFieldValue"
    formFieldName: Optional[str] = None
    formFieldId: Optional[int] = None
    data: Optional[str] = Field(default=None, alias="fieldValue")

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the CustomFieldData model.
            record id is the recordId like cases id or change id
            formId is the tab_id from the module calls
        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            post_save_form_fields="/api/{model_slug}/saveFormFields/{recordId}/{moduleName}",
            get_field_value="/api/{model_slug}/getFieldValues/{recordId}/{moduleName}/{formId}",
        )

    @staticmethod
    def filter_dict_keys(data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
        """
        Return a new dictionary containing only the keys from allowed_fields.

        :param data: The original dictionary.
        :param allowed_fields: A list of keys to keep in the dictionary.
        :return: A new dictionary with only the allowed keys.
        """
        return {key: value for key, value in data.items() if key in allowed_fields}

    @classmethod
    def save_custom_data(cls, record_id: int, module_name: str, data: List[Any]) -> bool:
        """
        Save custom data for a record
        :param record_id: record id
        :param module_name: module name
        :param data: data to save
        :return: list of custom fields
        """
        fields = ["formFieldId", "data"]

        # Suppose data is a list of Pydantic model instances.
        # First, convert each instance to a dict.
        data_dicts = [d.dict() for d in data]

        # Now, filter each dictionary so that only the keys in `fields` remain.
        filtered_data = [cls.filter_dict_keys(item, fields) for item in data_dicts]

        result = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("post_save_form_fields").format(
                model_slug=cls.get_module_slug(), recordId=record_id, moduleName=module_name
            ),
            data=filtered_data,
        )
        if result and result.ok:
            return True
        else:
            cls.log_response_error(response=result)
            return False

    @classmethod
    def get_field_values(cls, record_id: int, module_name: str, form_id: int) -> List["FormFieldValue"]:
        """
        Get custom data for a record
        :param record_id: record id
        :param module_name: module name
        :param form_id: form tab id
        :return: list of custom fields
        """
        result = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_field_value").format(
                model_slug=cls.get_module_slug(), recordId=record_id, moduleName=module_name, formId=form_id
            )
        )
        if result and result.ok:
            return [cls(**o) for o in result.json()]
        else:
            cls.log_response_error(response=result)
            return []

    @staticmethod
    def check_custom_fields(fields_list: list, module_name: str, tab_name: str) -> dict:
        """
        Check if the custom fields exist and
            create if not

        :param list fields_list: list list of custom fields
        :param str module_name: name of the module in RegScale
        :param str tab_name: name of the tab in the module
        :return: map of custom fields names to ids
        :return_type: dict
        """
        # Check the custom fields exist in RegScale
        custom_form_fields = Module.get_form_fields_by_tab_id(module_name=module_name, tab_name=tab_name)
        if custom_form_fields:
            custom_form_field_id_dict = {cf.regScaleName: cf.id for cf in custom_form_fields}
        else:
            custom_form_field_id_dict = {}
        missing_custom_fields = []
        for field in fields_list:
            if field not in custom_form_field_id_dict.keys():
                missing_custom_fields.append(field)

        if len(missing_custom_fields) > 0:
            logger.error(
                f"The following custom fields are missing:\n \
                    {missing_custom_fields}\n \
                        Load these custom fields in RegScale \
                        and run this command again"
            )

        return custom_form_field_id_dict

    @staticmethod
    def save_custom_fields(form_field_values: list):
        """
        Populate Custom Fields form a list of dict of
        record_id: int, record_module: str, form_field_id: int,
        and field_value: Any

        :param list form_field_values: list of custom form
        fields, values, and the record to which to post
        :return: None
        """
        logger.debug("Creating custom form field values...")
        # FormFieldValue class will throw errors if encountered
        for form_field_value in form_field_values:
            data = [
                FormFieldValue(
                    formFieldId=form_field_value["form_field_id"], fieldValue=form_field_value["field_value"]
                ),
            ]
            if data:
                FormFieldValue.save_custom_data(
                    record_id=form_field_value.get["record_id"],
                    module_name=form_field_value.get("record_module", "securityplans"),
                    data=data,
                )
