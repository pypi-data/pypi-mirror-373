#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclasses for a Tenable integration"""

import re

# standard python imports
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from pydantic import BaseModel

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import format_data_to_html
from regscale.integrations.scanner_integration import IntegrationAsset
from regscale.models.regscale_models.asset import Asset


class Family(BaseModel):
    """Family Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    type: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Family":
        """Dict to Family

        :param Any obj: Family object to convert
        :return: Family object
        :rtype: Family
        """
        return cls(**obj)


class Repository(BaseModel):
    """Repository Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    description: str
    dataFormat: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Repository":
        """Dict to Repository

        :param Any obj: Repository object as a dictionary
        :return: Repository object
        :rtype: Repository
        """
        return cls(**obj)


class Severity(BaseModel):
    """Severity Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    description: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Severity":
        """Dict to Severity

        :param Any obj: Severity object as a dictionary
        :return: Severity object
        :rtype: Severity
        """
        return cls(**obj)


class TenableIOAsset(BaseModel):
    """Tenable Asset Model from Tenable IO API

    :param BaseModel: Pydantic BaseModel
    """

    id: str
    has_agent: bool = False
    last_seen: str
    last_scan_target: Optional[str] = None
    sources: Optional[List[dict]] = []
    acr_score: Optional[int] = None
    acr_drivers: Optional[List[dict]] = None
    exposure_score: Optional[int] = None
    scan_frequency: Optional[List[dict]] = None
    ipv4s: Optional[List[str]] = None
    ipv6s: Optional[List[str]] = None
    fqdns: Optional[List[str]] = None
    installed_software: Optional[List[str]] = None
    mac_addresses: Optional[List[str]] = None
    netbios_names: Optional[List[str]] = None
    operating_systems: Optional[List[str]] = None
    hostnames: Optional[List[str]] = None
    agent_names: Optional[List[str]] = None
    aws_ec2_name: Optional[List[str]] = None
    security_protection_level: Optional[int] = None
    security_protections: Optional[Union[List[str], List[dict]]] = None
    exposure_confidence_value: Optional[Union[str, int]] = None
    terminated_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None

    @staticmethod
    def get_asset_name(asset: "TenableIOAsset") -> str:
        """Returns the name of an asset

        :param TenableIOAsset asset: Tenable IO Asset Object
        :return: Asset Name
        :rtype: str
        """
        if asset.netbios_names:
            return asset.netbios_names.pop()
        if asset.hostnames:
            return asset.hostnames.pop()
        if asset.ipv4s:
            return asset.ipv4s.pop()
        if asset.last_scan_target:
            return asset.last_scan_target
        return asset.id

    @staticmethod
    def get_asset_ip(asset: "TenableIOAsset") -> Optional[str]:
        """Returns the IP address of an asset

        :param TenableIOAsset asset: Tenable IO Asset Object
        :return: Asset IP
        :rtype: Optional[str]
        """
        if asset.ipv4s:
            return asset.ipv4s.pop()
        if asset.last_scan_target:
            return asset.last_scan_target
        return None

    @staticmethod
    def get_os_type(os_list: List[str]) -> Optional[str]:
        """Returns the operating system type of an asset.

        :param List[str] os_list: A list of operating systems associated with the asset.
        :return: The operating system type of the asset, or None if os_list is empty.
        :rtype: Optional[str]
        """
        if os_list:
            for os_name in os_list:
                if "windows" in os_name.lower():
                    return "Windows Server"
                if "linux" in os_name.lower():
                    return "Linux"
                if "android" in os_name.lower():
                    return "Android"
            return "Other"
        return None

    @staticmethod
    def create_asset_from_tenable(asset: "TenableIOAsset", ssp_id: int, app: Application) -> Asset:
        """Creates an Asset object from a TenableIOAsset object.

        :param TenableIOAsset asset: The TenableIOAsset object to create an Asset from.
        :param int ssp_id: The ID of the SSP associated with the Asset.
        :param Application app: The Application object to use for database operations.
        :return: The created Asset object.
        :rtype: Asset
        """
        keys = ["last_seen", "last_scan_target", "acr_score", "exposure_score"]
        meta = {key: asset.dict()[key] for key in keys}

        return Asset(
            otherTrackingNumber=asset.id,
            tenableId=asset.id,
            name=TenableIOAsset.get_asset_name(asset),
            ipAddress=TenableIOAsset.get_asset_ip(asset),
            awsIdentifier=asset.aws_ec2_name if asset.aws_ec2_name else None,
            macAddress=asset.mac_addresses.pop() if asset.mac_addresses else None,
            fqdn=asset.fqdns.pop() if asset.fqdns else None,
            status="Active (On Network)" if asset.terminated_at is None else "Decommissioned",
            assetCategory="Hardware",
            assetOwnerId=app.config["userId"],
            assetType="Other",
            operatingSystem=TenableIOAsset.get_os_type(asset.operating_systems),
            operatingSystemVersion=(asset.operating_systems.pop() if asset.operating_systems else None),
            scanningTool=asset.sources.pop()["name"] if asset.sources else None,
            notes=format_data_to_html(meta),
            parentId=ssp_id,
            parentModule="securityplans",
            createdById=app.config["userId"],
        )

    @staticmethod
    def update_existing_asset(asset: Asset, existing_assets: List[Asset]) -> Optional[Asset]:
        """Updates an existing Asset object if it exists and if it has changed,
            otherwise returns None

        :param Asset asset: The Asset object to update.
        :param List[Asset] existing_assets: A list of existing Asset objects to compare against.
        :return: The updated Asset object if it has changed, otherwise None.
        :rtype: Optional[Asset]
        """
        for existing in existing_assets:
            if existing.tenableId == asset.otherTrackingNumber:
                asset.id = existing.id
                if asset != existing:
                    return asset
                return None
        return asset

    @staticmethod
    def prepare_assets_for_sync(
        assets: List["TenableIOAsset"], ssp_id: int, existing_assets: List[Asset]
    ) -> Tuple[List[Asset], List[Asset]]:
        """Prepares Tenable assets for synchronization

        :param List[TenableIOAsset] assets: A list of TenableIOAsset objects to prepare for synchronization.
        :param int ssp_id: The ID of the SSP associated with the assets.
        :param List[Asset] existing_assets: A list of existing Asset objects to compare against.
        :return: A tuple containing two lists of Asset objects: new assets and updated assets.
        :rtype: Tuple[List[Asset], List[Asset]]
        """
        app = Application()
        insert_assets = []
        update_assets = []

        for asset in assets:
            reg = TenableIOAsset.create_asset_from_tenable(asset, ssp_id, app)
            updated_asset = TenableIOAsset.update_existing_asset(reg, existing_assets)
            if reg.tenableId not in {ten.tenableId for ten in existing_assets}:
                insert_assets.append(reg)
            if updated_asset and reg.tenableId in {ten.tenableId for ten in existing_assets}:
                update_assets.append(updated_asset)

        return insert_assets, update_assets

    @staticmethod
    def sync_assets_to_regscale(insert_assets: List[Asset], update_assets: List[Asset]) -> None:
        """Synchronizes assets to RegScale.

        :param List[Asset] insert_assets: A list of Asset objects to insert.
        :param List[Asset] update_assets: A list of Asset objects to update.
        :rtype: None
        """
        if insert_assets:
            Asset.batch_create(insert_assets)

        if update_assets:
            Asset.batch_update(update_assets)

    @staticmethod
    def sync_to_regscale(assets: List["TenableIOAsset"], ssp_id: int, existing_assets: List[Asset]) -> None:
        """Synchronizes Tenable assets to RegScale

        :param List[TenableIOAsset] assets: A list of TenableIOAsset objects to synchronize.
        :param int ssp_id: The ID of the SSP associated with the assets.
        :param List[Asset] existing_assets: A list of existing Asset objects to compare against.
        :rtype: None
        """
        # Exports API will determine if the asset is off network, if so, it will be decommissioned in regscale
        insert_assets, update_assets = TenableIOAsset.prepare_assets_for_sync(assets, ssp_id, existing_assets)
        TenableIOAsset.sync_assets_to_regscale(insert_assets, update_assets)


class TenableBasicAsset(BaseModel):
    """Basic Asset Class for Tenable

    :param BaseModel: Pydantic Base Class
    """

    device_type: Optional[str] = None
    hostname: Optional[str] = None
    uuid: Optional[str] = None
    ipv4: Optional[str] = None
    mac_address: Optional[str] = None
    netbios_name: Optional[str] = None
    fqdn: Optional[str] = None
    last_unauthenticated_results: Optional[datetime] = None
    operating_system: Optional[List[str]] = None
    network_id: Optional[str] = None
    tracked: Optional[bool] = None


class TenableAsset(BaseModel):
    """TenableAsset Model

    :param BaseModel: Base Model
    """

    pluginID: str
    severity: Severity
    hasBeenMitigated: str
    acceptRisk: str
    recastRisk: str
    ip: str
    uuid: str
    port: str
    protocol: str
    pluginName: str
    firstSeen: str
    lastSeen: str
    exploitAvailable: str
    exploitEase: str
    exploitFrameworks: str
    synopsis: str
    description: str
    solution: str
    seeAlso: str
    riskFactor: str
    stigSeverity: str
    vprScore: str
    vprContext: str
    baseScore: str
    temporalScore: str
    cvssVector: str
    cvssV3BaseScore: str
    cvssV3TemporalScore: str
    cvssV3Vector: str
    cpe: str
    vulnPubDate: str
    patchPubDate: str
    pluginPubDate: str
    pluginModDate: str
    checkType: str
    version: str
    cve: str
    bid: str
    xref: str
    pluginText: str
    dnsName: str
    macAddress: str
    netbiosName: str
    operatingSystem: str
    ips: str
    recastRiskRuleComment: str
    acceptRiskRuleComment: str
    hostUniqueness: str
    acrScore: str
    keyDrivers: str
    uniqueness: str
    family: Family
    repository: Repository
    pluginInfo: str
    count: int = 0
    dns: str = ""

    @classmethod
    def from_dict(cls, obj: Any) -> "TenableAsset":
        """Dict to TenableAsset

        :param Any obj: TenableAsset object as a dictionary
        :return: TenableAsset object
        :rtype: TenableAsset
        """
        obj["severity"] = Severity.from_dict(obj.get("severity"))
        obj["family"] = Family.from_dict(obj.get("family"))
        obj["repository"] = Repository.from_dict(obj.get("repository"))
        return cls(**obj)

    @staticmethod
    def determine_os(os_string: str) -> str:
        """
        Determine RegScale friendly OS name

        :param str os_string: String of the asset's OS
        :return: RegScale acceptable OS
        :rtype: str
        """
        linux_words = ["linux", "ubuntu", "hat", "centos", "rocky", "alma", "alpine"]
        if re.compile("|".join(linux_words), re.IGNORECASE).search(os_string):
            return "Linux"
        elif (os_string.lower()).startswith("windows"):
            return "Windows Server" if "server" in os_string else "Windows Desktop"
        else:
            return "Other"

    # 'uniqueness': 'repositoryID,ip,dnsName'
    def __hash__(self) -> hash:
        """
        Enable object to be hashable
        :return: Hashed TenableAsset
        :rtype: hash
        """
        return hash(str(self))

    def __eq__(self, other: "TenableAsset") -> bool:
        """
        Update items in TenableAsset class
        :param TenableAsset other: TenableAsset to compare
        :return: Updated TenableAsset
        :rtype: bool
        """
        return (
            self.dnsName == other.dnsName
            and self.macAddress == other.macAddress
            and self.ip == other.ip
            and self.repository.name == other.respository.name
        )


class Reference(BaseModel):
    """Reference Model

    :param BaseModel: Base Model
    """

    framework: str
    control: str


class AssetCheck(BaseModel):
    """AssetCheck Model

    :param BaseModel: Base Model
    """

    asset_uuid: str
    first_seen: str
    last_seen: str
    audit_file: str
    check_id: str
    check_name: str
    check_info: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    status: str
    reference: Optional[List[Reference]] = []
    see_also: str
    solution: Optional[str] = None
    plugin_id: Optional[int] = None
    state: str
    description: str


class ExportStatus(Enum):
    """ExportStatus Enum

    :param Enum: Enum base class
    """

    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"
    READY = "READY"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class Plugin(BaseModel):
    """Plugin Class for Tenable

    :param BaseModel: Pydantic Base Class
    """

    checks_for_default_account: Optional[bool] = None
    checks_for_malware: Optional[bool] = None
    cvss3_base_score: Optional[float] = None
    cvss3_temporal_score: Optional[float] = None
    cvss_base_score: Optional[float] = None
    cvss_temporal_score: Optional[float] = None
    description: Optional[str] = None
    exploit_available: Optional[bool] = None
    exploit_framework_canvas: Optional[bool] = None
    exploit_framework_core: Optional[bool] = None
    exploit_framework_d2_elliot: Optional[bool] = None
    exploit_framework_exploithub: Optional[bool] = None
    exploit_framework_metasploit: Optional[bool] = None
    exploited_by_malware: Optional[bool] = None
    exploited_by_nessus: Optional[bool] = None
    family: Optional[str] = None
    family_id: Optional[int] = None
    has_patch: Optional[bool] = None
    id: Optional[int] = None
    in_the_news: Optional[bool] = None
    name: Optional[str] = None
    modification_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    risk_factor: Optional[str] = None
    see_also: Optional[List[str]] = None
    solution: Optional[str] = None
    synopsis: Optional[str] = None
    type: Optional[str] = None
    unsupported_by_vendor: Optional[bool] = None
    version: Optional[str] = None


class TenablePort(BaseModel):
    """Tenable Port and Protocol

    :param BaseModel: Pydantic Base Class
    """

    port: Optional[int]
    protocol: Optional[str]


class TenableScan(BaseModel):
    """Tenable Basic Scan class

    :param BaseModel: Pydantic Base Class
    """

    completed_at: Optional[datetime] = None
    schedule_uuid: Optional[str] = None
    started_at: Optional[datetime] = None
    uuid: Optional[str] = None
