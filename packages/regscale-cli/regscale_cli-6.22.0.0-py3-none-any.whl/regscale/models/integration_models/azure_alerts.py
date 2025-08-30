#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a Microsoft Defender for Cloud alerts"""

# standard python imports
from dataclasses import dataclass
from typing import Any, Optional
from typing import List


@dataclass
class Location:
    countryCode: Optional[str] = None
    countryName: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    asn: Optional[int] = None
    carrier: Optional[str] = None
    organization: Optional[str] = None
    organizationType: Optional[str] = None
    cloudProvider: Optional[str] = None
    systemService: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Location":
        _countryCode = str(obj.get("countryCode"))
        _countryName = str(obj.get("countryName"))
        _state = str(obj.get("state"))
        _city = str(obj.get("city"))
        _longitude = float(obj.get("longitude"))
        _latitude = float(obj.get("latitude"))
        _asn = int(obj.get("asn"))
        _carrier = str(obj.get("carrier"))
        _organization = str(obj.get("organization"))
        _organizationType = str(obj.get("organizationType"))
        _cloudProvider = str(obj.get("cloudProvider"))
        _systemService = str(obj.get("systemService"))
        return Location(
            _countryCode,
            _countryName,
            _state,
            _city,
            _longitude,
            _latitude,
            _asn,
            _carrier,
            _organization,
            _organizationType,
            _cloudProvider,
            _systemService,
        )


@dataclass
class SourceAddress:
    ref: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "SourceAddress":
        _ref = str(obj.get("$ref"))
        return SourceAddress(_ref)


@dataclass
class Host:
    ref: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Host":
        _ref = str(obj.get("$ref"))
        return Host(_ref)


@dataclass
class Entity:
    id: Optional[str] = None
    resourceId: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    hostName: Optional[str] = None
    sourceAddress: Optional[SourceAddress] = None
    name: Optional[str] = None
    host: Optional[Host] = None

    @staticmethod
    def from_dict(obj: Any) -> "Entity":
        _id = str(obj.get("$id"))
        _resourceId = str(obj.get("resourceId"))
        _type = str(obj.get("type"))
        _address = str(obj.get("address"))
        _location = Location.from_dict(obj.get("location"))
        _hostName = str(obj.get("hostName"))
        _sourceAddress = SourceAddress.from_dict(obj.get("sourceAddress"))
        _name = str(obj.get("name"))
        _host = Host.from_dict(obj.get("host"))
        return Entity(
            _id,
            _resourceId,
            _type,
            _address,
            _location,
            _hostName,
            _sourceAddress,
            _name,
            _host,
        )


@dataclass
class ExtendedProperties:
    alertId: Optional[str] = None
    compromisedEntity: Optional[str] = None
    clientIpAddress: Optional[str] = None
    clientPrincipalName: Optional[str] = None
    clientApplication: Optional[str] = None
    investigationSteps: Optional[str] = None
    potentialCauses: Optional[str] = None
    resourceType: Optional[str] = None
    killChainIntent: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "ExtendedProperties":
        _alertId = str(obj.get("alert Id"))
        _compromisedEntity = str(obj.get("compromised entity"))
        _clientIpAddress = str(obj.get("client IP address"))
        _clientPrincipalName = str(obj.get("client principal name"))
        _clientApplication = str(obj.get("client application"))
        _investigationSteps = str(obj.get("investigation steps"))
        _potentialCauses = str(obj.get("potential causes"))
        _resourceType = str(obj.get("resourceType"))
        _killChainIntent = str(obj.get("killChainIntent"))
        return ExtendedProperties(
            _alertId,
            _compromisedEntity,
            _clientIpAddress,
            _clientPrincipalName,
            _clientApplication,
            _investigationSteps,
            _potentialCauses,
            _resourceType,
            _killChainIntent,
        )


@dataclass
class ResourceIdentifier:
    id: Optional[str] = None
    azureResourceId: Optional[str] = None
    type: Optional[str] = None
    azureResourceTenantId: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "ResourceIdentifier":
        _id = str(obj.get("$id"))
        _azureResourceId = str(obj.get("azureResourceId"))
        _type = str(obj.get("type"))
        _azureResourceTenantId = str(obj.get("azureResourceTenantId"))
        return ResourceIdentifier(_id, _azureResourceId, _type, _azureResourceTenantId)


@dataclass
class Properties:
    status: Optional[str] = None
    timeGeneratedUtc: Optional[str] = None
    processingEndTimeUtc: Optional[str] = None
    version: Optional[str] = None
    vendorName: Optional[str] = None
    productName: Optional[str] = None
    productComponentName: Optional[str] = None
    alertType: Optional[str] = None
    startTimeUtc: Optional[str] = None
    endTimeUtc: Optional[str] = None
    severity: Optional[str] = None
    isIncident: Optional[str] = None
    systemAlertId: Optional[str] = None
    correlationKey: Optional[str] = None
    intent: Optional[str] = None
    resourceIdentifiers: Optional[List[ResourceIdentifier]] = None
    compromisedEntity: Optional[str] = None
    alertDisplayName: Optional[str] = None
    description: Optional[str] = None
    remediationSteps: Optional[List[str]] = None
    extendedProperties: Optional[ExtendedProperties] = None
    entities: Optional[List[Entity]] = None
    alertUri: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Properties":
        _status = str(obj.get("status"))
        _timeGeneratedUtc = str(obj.get("timeGeneratedUtc"))
        _processingEndTimeUtc = str(obj.get("processingEndTimeUtc"))
        _version = str(obj.get("version"))
        _vendorName = str(obj.get("vendorName"))
        _productName = str(obj.get("productName"))
        _productComponentName = str(obj.get("productComponentName"))
        _alertType = str(obj.get("alertType"))
        _startTimeUtc = str(obj.get("startTimeUtc"))
        _endTimeUtc = str(obj.get("endTimeUtc"))
        _severity = str(obj.get("severity"))
        _isIncident = bool(obj.get("isIncident"))
        _systemAlertId = str(obj.get("systemAlertId"))
        _correlationKey = str(obj.get("correlationKey"))
        _intent = str(obj.get("intent"))
        _resourceIdentifiers = [ResourceIdentifier.from_dict(y) for y in obj.get("resourceIdentifiers")]
        _compromisedEntity = str(obj.get("compromisedEntity"))
        _alertDisplayName = str(obj.get("alertDisplayName"))
        _description = str(obj.get("description"))
        _remediationSteps = [obj.get("remediationSteps")]
        _extended_properties = ExtendedProperties.from_dict(obj.get("extendedProperties"))
        _entities = [Entity.from_dict(y) for y in obj.get("entities")]
        _alertUri = str(obj.get("alertUri"))
        return Properties(
            _status,
            _timeGeneratedUtc,
            _processingEndTimeUtc,
            _version,
            _vendorName,
            _productName,
            _productComponentName,
            _alertType,
            _startTimeUtc,
            _endTimeUtc,
            _severity,
            _isIncident,
            _systemAlertId,
            _correlationKey,
            _intent,
            _resourceIdentifiers,
            _compromisedEntity,
            _alertDisplayName,
            _description,
            _remediationSteps,
            _extended_properties,
            _entities,
            _alertUri,
        )


@dataclass
class Alert:
    id: str
    name: str
    type: str
    properties: Properties

    @staticmethod
    def from_dict(obj: Any) -> "Alert":
        _id = str(obj.get("id"))
        _name = str(obj.get("name"))
        _type = str(obj.get("type"))
        _properties = Properties.from_dict(obj.get("properties"))
        return Alert(_id, _name, _type, _properties)
