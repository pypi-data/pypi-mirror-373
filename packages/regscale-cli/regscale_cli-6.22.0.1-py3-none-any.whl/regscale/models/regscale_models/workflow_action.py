"""
This module contains the WorkflowAction model.
"""

from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel
from pydantic import ConfigDict


class WorkflowAction(RegScaleModel):
    _module_slug = "workflowActions"

    id: Optional[int] = None
    value: Optional[str] = None
    recordId: Optional[int] = None
    recordModule: Optional[str] = None
    days: Optional[int] = None
    recordTitle: Optional[str] = None
    workflowTemplateId: Optional[int] = None
    workflowInstanceId: Optional[int] = None
    isPublic = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the WorkflowAction model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_actions="/api/{model_slug}/getActions/{strModule}",
        )
