#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a Microsoft Defender recommendations or alerts"""

# standard python imports
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


@dataclass
class DefenderData(BaseModel):
    """DefenderData Model"""

    _model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str  # Required
    data: dict  # Required
    system: str  # Required
    object: str  # Required
    analyzed: Optional[str] = Field(default=False)  # type: ignore
    created: Optional[str] = Field(default=False)  # type: ignore
    integration_field: Optional[str] = None
    init_key: Optional[str] = None

    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.integration_field = self.get_integration_field(self.system, self.object)
        self.init_key = self.get_init_key()

    @field_validator("system")
    def validate_system(cls, v: str) -> str:
        """
        Validates the riskAdjustment field.

        :param str v: The value to validate
        :raise ValueError: If the value is not valid

        :return: The validated values
        :rtype: str

        """
        allowed_values = ["365", "cloud"]
        if v not in allowed_values:
            raise ValueError(f"system must be one of {allowed_values}")
        return v

    @field_validator("object")
    def validate_object(cls, v: str) -> str:
        """
        Validates the riskAdjustment field.

        :param str v: The value to validate
        :raise ValueError: If the value is not valid

        :return: The validated values
        :rtype: str

        """
        allowed_values = ["alerts", "recommendations"]
        if v not in allowed_values:
            raise ValueError(f"object must be one of {allowed_values}")
        return v

    @staticmethod
    def get_integration_field(system: str, object: str) -> str:
        """
        Get the integration field for the provided system and object

        :return: The integration field for the provided system and object
        :rtype: str
        """
        issue_integration_field = {
            "365_alerts": "defenderAlertId",
            "365_recommendations": "defenderId",
            "cloud_alerts": "defenderCloudId",
            "cloud_recommendations": "manualDetectionId",
        }
        return issue_integration_field.get(f"{system}_{object}", "pluginId")

    def get_init_key(self) -> str:
        """
        Get the init.yaml key for the system and object

        :return: The init.yaml key for the system and object
        :rtype: str
        """
        init_mapping = {
            "365": "defender365",
            "cloud": "defenderCloud",
        }
        return init_mapping.get(self.system, "defender")
