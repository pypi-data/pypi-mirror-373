#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Interconnect in the application"""

from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel


class InterConnection(RegScaleModel):
    """RegScale Interconnects model"""

    _module_slug = "interconnections"

    id: int = 0
    authorizationType: str
    categorization: str
    connectionType: str
    name: str
    organization: str
    status: str
    aoId: str
    interconnectOwnerId: str
    parentId: int = 0
    parentModule: Optional[str] = None
    isPublic: bool = True
    agreementDate: Optional[str] = None
    expirationDate: Optional[str] = None
    description: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    tenantsId: Optional[int] = None
    uuid: Optional[str] = None
    dataDirection: Optional[str] = None
    externalEmail: Optional[str] = None
    externalFQDN: Optional[str] = None
    externalIpAddress: Optional[str] = None
    externalPOC: Optional[str] = None
    externalPhone: Optional[str] = None
    sourceFQDN: Optional[str] = None
    sourceIpAddress: Optional[str] = None
