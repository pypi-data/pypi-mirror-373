#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Security Control"""

# standard python imports
from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel


# from regscale.core.app.api import Api
# from regscale.core.app.application import Application


class Control(RegScaleModel):
    """RegScale Control class"""

    _module_slug = "controls"

    id: int = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    controlId: Optional[str] = None
    sortId: Optional[str] = None
    controlType: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    references: Optional[str] = None
    relatedControls: Optional[str] = None
    subControls: Optional[str] = None
    enhancements: Optional[str] = None
    family: Optional[str] = None
    weight: Optional[int] = None
    catalogueID: Optional[int] = None
    archived: bool = False
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    tenantsId: Optional[int] = None
