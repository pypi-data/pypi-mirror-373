#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Teams in the application"""

from typing import Optional, Union

from pydantic import ConfigDict

from regscale.core.app.api import Api
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Team(RegScaleModel):
    _module_slug = "teams"

    id: Optional[int] = None
    member: Optional[str] = None
    memberId: Optional[str] = None
    memberType: Optional[str] = None
    bExecutive: Optional[bool] = False
    bOversight: Optional[bool] = False
    bCommunications: Optional[bool] = False
    bEngineer: Optional[bool] = False
    bAssessor: Optional[bool] = False
    bQuality: Optional[bool] = False
    bSafety: Optional[bool] = False
    bSecurity: Optional[bool] = False
    bAnalyst: Optional[bool] = False
    bScheduler: Optional[bool] = False
    bAdministrative: Optional[bool] = False
    bProjectManager: Optional[bool] = False
    bFinance: Optional[bool] = False
    bHumanResources: Optional[bool] = False
    bOperations: Optional[bool] = False
    bISSO: Optional[bool] = False
    bISSM: Optional[bool] = False
    bAO: Optional[bool] = False
    bCISO: Optional[bool] = False
    bSCA: Optional[bool] = False
    bDevOps: Optional[bool] = False
    bProgrammer: Optional[bool] = False
    bSystemOwner: Optional[bool] = False
    bRiskAnalyst: Optional[bool] = False
    bInternalAudit: Optional[bool] = False
    bExternalAudit: Optional[bool] = False
    bInformationOwner: Optional[bool] = False
    bAODR: Optional[bool] = False
    bContingencyCoordinator: Optional[bool] = False
    bContingencyDirector: Optional[bool] = False
    bResponsible: Optional[bool] = False
    bAccountable: Optional[bool] = False
    bConsulted: Optional[bool] = False
    bInformed: Optional[bool] = False
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
