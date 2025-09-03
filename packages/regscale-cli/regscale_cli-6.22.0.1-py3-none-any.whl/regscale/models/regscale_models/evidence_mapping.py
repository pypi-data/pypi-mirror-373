#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for evidence mapping model in RegScale platform"""

from typing import Optional
from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class EvidenceMapping(RegScaleModel):
    """Evidence mapping Model"""

    _module_slug = "evidenceMapping"
    _module_string = "evidenceMapping"

    id: int = 0
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    isPublic: Optional[bool] = True
    evidenceID: Optional[int] = 0
    mappedID: Optional[int] = 0
    mappingType: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Evidence model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByEvidence/{intParentID}",
            get_summary_by_evidence="/api/{model_slug}/getSummaryByEvidence/{intID}",
            batch_create="/api/{model_slug}/batchCreate",
        )
