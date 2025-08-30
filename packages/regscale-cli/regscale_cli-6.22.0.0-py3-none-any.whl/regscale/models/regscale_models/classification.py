#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Classification Records in the application"""

from typing import Optional, Union

from pydantic import ConfigDict
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ClassifiedRecord(RegScaleModel):
    _module_slug = "classifiedRecords"

    id: Optional[int] = None
    parentRecordId: Optional[int] = 0
    parentModule: Optional[str] = None
    classificationTypeId: Optional[int] = 0
    adjustedConfidentiality: Optional[str] = None
    confidentialityJustification: Optional[str] = None
    adjustedAvailability: Optional[str] = None
    availabilityJustification: Optional[str] = None
    adjustedIntegrity: Optional[str] = None
    integrityJustification: Optional[str] = None
