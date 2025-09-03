#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Cryptography in the application"""

from typing import Optional

from pydantic import ConfigDict, Field
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Cryptography(RegScaleModel):
    _module_slug = "cryptography"

    id: Optional[int] = None
    cryptographyType: str
    sourceArea: Optional[str] = None
    sourceVendorName: Optional[str] = None
    sourceModule: Optional[str] = None
    fipsNumber: Optional[str] = None
    bSourceEmbedded: Optional[bool] = False
    bSourceThirdParty: Optional[bool] = False
    bSourceOS: Optional[bool] = False
    bSourceFIPS: Optional[bool] = False
    bSourceOther: Optional[bool] = False
    sourceExplanationOther: Optional[str] = None
    destinationArea: Optional[str] = None
    destinationVendorName: Optional[str] = None
    destinationModule: Optional[str] = None
    bDestinationEmbedded: Optional[bool] = False
    bDestinationThirdParty: Optional[bool] = False
    bDestinationOS: Optional[bool] = False
    bDestinationFIPS: Optional[bool] = False
    bDestinationOther: Optional[bool] = False
    destinationExplanationOther: Optional[str] = None
    bUsageTLS11: Optional[bool] = False
    bUsageTLS12: Optional[bool] = False
    bUsageTLS13: Optional[bool] = False
    bUsageOther: Optional[bool] = False
    usageExplanationOther: Optional[str] = None
    usage: str
    bRestFullDisk: Optional[bool] = False
    bRestFile: Optional[bool] = False
    bRestRecord: Optional[bool] = False
    bRestNone: Optional[bool] = False
    encryptionExplanationOther: Optional[str] = None
    encryptionType: Optional[str] = None
    notes: Optional[str] = None
    referenceUrl: Optional[str] = None
    isPublic: Optional[bool] = False
    parentId: Optional[int] = 0
    parentModule: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: int = 1
