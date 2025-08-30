"""This module contains the Compliance Settings model class."""

from typing import List, Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class ComplianceSettings(RegScaleModel):
    """
    Compliance Settings model class
    """

    _module_slug = "settings"
    _module_slug_id_url = "/api/compliance/{model_slug}/{id}"
    _unique_fields = [
        ["title"],
    ]

    id: int
    title: str
    hasParts: bool = True
    wayfinderOptionId: Optional[int] = None
    profileIds: Optional[List] = None
    complianceSettingsFieldGroups: Optional[List] = None

    @classmethod
    def get_by_current_tenant(cls) -> List["ComplianceSettings"]:
        """
        Get a list of compliance settings by current tenant.

        :return: A list of compliance settings
        :rtype: List[ComplianceSettings]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_current_tenant").format(model_slug=cls._module_slug)
        )
        compliance_settings = []
        if response and response.ok:
            for setting in response.json():
                compliance_settings.append(ComplianceSettings(**setting))
        return compliance_settings

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ComplianceSettings model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_by_current_tenant="/api/compliance/{model_slug}",  # type: ignore
            get_by_compliance_id="/api/compliance/{model_slug}/{id}/",  # type: ignore
        )

    @classmethod
    def _get_endpoints(cls) -> ConfigDict:
        """
        Get the endpoints for the API.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        endpoints = ConfigDict(  # type: ignore
            get=cls._module_slug_id_url,  # type: ignore
            insert="/api/compliance/{model_slug}/",  # type: ignore
            update=cls._module_slug_id_url,  # type: ignore
            delete=cls._module_slug_id_url,  # type: ignore
        )
        endpoints.update(cls._get_additional_endpoints())
        return endpoints

    @classmethod
    def get_labels(cls, setting_id: int, setting_field: str) -> List[str]:
        """
        Get the labels for the ComplianceSettings model.

        :param int setting_id: The ID of the compliance setting
        :param str setting_field: The field of the compliance setting
        :return: A list of labels
        :rtype: List[str]
        """
        compliance_setting = None
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_compliance_id").format(model_slug=cls._module_slug, id=setting_id)
        )
        labels = []
        if response and response.ok:
            compliance_setting = cls(**response.json())
        else:
            return labels
        if not compliance_setting:
            return labels
        if compliance_setting.complianceSettingsFieldGroups:
            for group in compliance_setting.complianceSettingsFieldGroups:
                if group["formFieldId"] == setting_field:
                    for item in group["complianceSettingsList"]:
                        labels.append(item["statusName"])

        return labels

    def get_field_labels(self, setting_field: str) -> List[str]:
        """
        Get the labels for the specified field from this compliance setting.

        :param str setting_field: The field of the compliance setting
        :return: A list of labels
        :rtype: List[str]
        """
        return self.__class__.get_labels(self.id, setting_field)
