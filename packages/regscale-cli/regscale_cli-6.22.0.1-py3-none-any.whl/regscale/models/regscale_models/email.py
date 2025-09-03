#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for emails to send emails in RegScale platform"""

from typing import Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Email(RegScaleModel):
    """Class for email capabilities via RegScale platform"""

    _module_slug = "email"
    _exclude_graphql_fields = ["tenantsId"]

    to: str
    subject: str
    id: Optional[int] = 0
    fromEmail: str = Field(description="Cannot use from since it is a reserved word in Python", alias="from")
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: Optional[bool] = True
    cc: Optional[str] = ""
    body: Optional[str] = ""
    dateSent: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1
    emailSenderId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Issues model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_domain="/api/{model_slug}/getDomain",
            get_admin_email="/api/{model_slug}/getAdminEmail",
            filter_my_email="/api/{model_slug}/filterMyEmail/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            filter_email="/api/{model_slug}/filterEmail/{strUser}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            find_my_email="/api/{model_slug}/findMyEmail/{intID}",
        )

    def send(self) -> bool:
        """
        Send the email

        :return: Whether the email was sent successfully
        :rtype: bool
        """
        logger = create_logger()
        endpoint = self.get_endpoint("insert")
        response = self._get_api_handler().post(endpoint=endpoint, data=self.dict())
        if response and response.ok:
            return True
        import json

        logger.error(
            f"Failed to create {self.__class__.__name__}\n Endpoint: {endpoint}\n Payload: "
            f"{json.dumps(self.dict(), indent=2)}",
            exc_info=True,
        )
        if response and not response.ok:
            logger.error(f"Response Error: Code #{response.status_code}: {response.reason}\n{response.text}")
            return False
        if response is None:
            error_msg = "Response was None"
            logger.error(error_msg)
            return False
        error_msg = f"Response Code: {response.status_code}:{response.reason} - {response.text}"
        logger.error(error_msg)
        return False

    def create(self, _=False) -> bool:
        """
        Create the email

        :return: Email object
        :rtype: Email
        """
        return self.send()

    def delete(self) -> bool:
        """
        Delete is not supported for emails, returns False

        :return: False because it is not supported
        :rtype: bool
        """
        return False
