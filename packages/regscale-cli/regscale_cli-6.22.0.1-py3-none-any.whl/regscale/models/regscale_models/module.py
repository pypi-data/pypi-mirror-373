import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class Choice(BaseModel):
    id: Optional[int] = None
    isActive: Optional[bool] = None
    value: Optional[str] = None
    label: Optional[str] = None
    regScaleLabel: Optional[str] = None
    sequence: Optional[int] = None


class FormField(BaseModel):
    id: Optional[int] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[datetime] = None
    dateLastUpdated: Optional[datetime] = None
    isPublic: Optional[bool] = None
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    displayName: Optional[str] = None
    regScaleId: Optional[str] = None
    regScaleName: Optional[str] = None
    isActive: Optional[bool] = None
    isRequired: Optional[bool] = None
    isCustom: Optional[bool] = None
    fieldType: Optional[str] = None
    selectType: Optional[str] = None
    pattern: Optional[str] = None
    sequence: Optional[int] = None
    helpText: Optional[str] = None
    choices: Optional[List[Choice]] = None


class FormTab(BaseModel):
    id: Optional[int] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[datetime] = None
    dateLastUpdated: Optional[datetime] = None
    isPublic: Optional[bool] = None
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    displayName: Optional[str] = None
    regScaleName: Optional[str] = None
    regScaleId: Optional[str] = None
    regScaleLink: Optional[str] = None
    isActive: Optional[bool] = None
    isDefault: Optional[bool] = None
    isCustom: Optional[bool] = None
    sequence: Optional[int] = None
    helpText: Optional[str] = None
    formFields: Optional[List[FormField]] = None


class Status(BaseModel):
    regScaleTitle: Optional[str] = None
    displayTitle: Optional[str] = None
    iconName: Optional[str] = None
    color: Optional[str] = None


class Report(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None


class HelpTextDetail(BaseModel):
    summary: Optional[str] = None
    bulletList: Optional[List[str]] = None


class HelpText(BaseModel):
    whyUseIt: Optional[HelpTextDetail] = None
    whatIsIt: Optional[HelpTextDetail] = None


class ChildModule(BaseModel):
    moduleName: Optional[str] = None
    moduleInformalName: Optional[str] = None
    helpText: Optional[HelpText] = None


class Module(RegScaleModel):
    _module_slug = "modules"
    id: Optional[int] = None
    displayName: Optional[str] = None
    displayPluralizedName: Optional[str] = None
    regScaleName: Optional[str] = None
    regScalePluralizedName: Optional[str] = None
    regScaleId: Optional[int] = None
    regScaleInformalName: Optional[str] = None
    route: Optional[str] = None
    newFormRoute: Optional[str] = None
    documentation: Optional[str] = None
    workbench: Optional[bool] = None
    atlasModule: Optional[str] = None
    formTabs: Optional[List[FormTab]] = None
    status: Optional[List[Status]] = None
    reports: Optional[List[Report]] = None
    children: Optional[List[ChildModule]] = None
    helpText: Optional[HelpText] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Module model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_modules="/api/{model_slug}",
            get_module_by_id="/api/{model_slug}/{id}",
        )

    @classmethod
    def get_modules(cls) -> List["Module"]:
        """
        Get all modules.

        :return: A list of modules
        :rtype: List["Module"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_modules").format(model_slug=cls.get_module_slug())
        )
        if response and response.ok:
            return [cls(**o) for o in response.json()]
        else:
            cls.log_response_error(response=response)
            return []

    @classmethod
    def get_module_by_id(cls, id: int) -> Optional["Module"]:
        """
        Get a module by ID. provides more data that get_modules

        :param int id: The ID of the module to get
        :return: The module
        :rtype: Optional["Module"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_module_by_id").format(model_slug=cls._module_slug, id=id)
        )
        if response and response.ok:
            return cls(**response.json())
        else:
            cls.log_response_error(response=response)
            return None

    @classmethod
    def get_module_by_name(cls, regscale_name: str) -> Optional["Module"]:
        """
        Get a module by name.

        :param str regscale_name: The name of the module to get
        :return: The module
        :rtype: Optional["Module"]
        """
        for module in cls.get_modules():
            if module.regScaleInformalName == regscale_name:
                return module
        return None

    @classmethod
    def get_tab_by_name(cls, regscale_module_name: str, regscale_tab_name: str) -> Optional[FormTab]:
        """
        Get a tab by name.

        :param str regscale_module_name: The name of the module
        :param str regscale_tab_name: The regscale_name of the tab to get
        :return: The tab
        :rtype: Optional[FormTab]
        """
        module = cls.get_module_by_name(regscale_name=regscale_module_name)
        if module:
            module_metadata = cls.get_module_by_id(id=module.id)
            if not module_metadata:
                return None
            for form_tab in module_metadata.formTabs:
                if form_tab.regScaleName == regscale_tab_name:
                    return form_tab
        return None

    @classmethod
    def get_new_custom_form_tab_id(cls, module_name="cases", tab_name: str = "Migrated Custom Fields") -> Optional[int]:
        """
        Get the id of the new custom form tab. this is needed to update the custom field data

        :param str module_name: The name of the module
        :param str tab_name: The name of the tab
        :return: The id of the new custom form tab
        :rtype: Optional[int]
        """
        form_tab = cls.get_tab_by_name(regscale_module_name=module_name, regscale_tab_name=tab_name)
        if form_tab:
            return form_tab.id
        return None

    @classmethod
    def get_form_fields_by_tab_id(
        cls, module_name: str = "cases", tab_name: str = "Migrated Custom Fields"
    ) -> Optional[List[FormField]]:
        """
        Get the form fields by tab id.
        :param str module_name: The name of the module
        :param str tab_name: The name of the tab
        :return: A list of form fields
        :rtype: Optional[List[FormField]]
        """
        form_tab = cls.get_tab_by_name(regscale_module_name=module_name, regscale_tab_name=tab_name)
        if form_tab:
            return form_tab.formFields
        return None
