#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for a RegScale Ports and Protocols"""
from enum import Enum
from typing import Optional, Union

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class Protocol(str, Enum):
    """Enumeration for Protocols"""

    TCP = "TCP"
    UDP = "UDP"
    TCP_UDP = "TCP/UDP"
    OTHER = "Other"


class PortsProtocol(RegScaleModel):
    """Ports And Protocols"""

    _module_slug = "portsprotocols"
    _unique_fields = [
        [
            "parentId",
            "parentModule",
            "startPort",
            "endPort",
            "protocol",
            "service",
        ],
    ]

    startPort: Optional[int] = 0
    endPort: Optional[int] = 0
    parentId: Optional[int] = 0
    parentModule: Optional[str] = ""
    protocol: Optional[Union[str, Protocol]] = Protocol.OTHER
    service: Optional[str] = "N/A"
    purpose: Optional[str] = "N/A"
    usedBy: Optional[str] = "N/A"
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the PortsProtocols model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            find="/api/{model_slug}/find/{id}",
        )

    def __eq__(self, other: object) -> bool:
        """
        Compare two PortsProtocols objects

        :param object other: PortsProtocols object
        :return: True if PortsProtocols are equal
        :rtype: bool
        """
        if isinstance(other, PortsProtocol):
            return self.dict() == other.dict()
        return False

    def __hash__(self) -> hash:
        """
        Return hash of PortsProtocols

        :return: hash of PortsProtocols
        :rtype: hash
        """
        return hash(
            (
                self.parentId,
                self.parentModule,
                self.startPort,
                self.endPort,
                self.protocol,
                self.service,
                self.purpose,
                self.usedBy,
            )
        )
