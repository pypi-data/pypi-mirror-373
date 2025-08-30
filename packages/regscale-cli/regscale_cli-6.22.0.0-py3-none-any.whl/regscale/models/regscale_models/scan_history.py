#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Scan in the application"""
import logging
import pickle
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from pydantic import ConfigDict, Field
from requests import JSONDecodeError, RequestException, Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    convert_datetime_to_regscale_string,
    create_progress_object,
    get_current_datetime,
)
from regscale.core.utils.date import normalize_date
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class ScanHistory(RegScaleModel):
    """Model for ScanHistory in the application"""

    _module_slug = "scanhistory"
    _unique_fields = [
        ["scanningTool", "parentId", "parentModule"],
    ]

    id: int = 0
    scanningTool: str
    dateCreated: str = Field(default_factory=get_current_datetime)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    tenantsId: int = 1
    uuid: Optional[str] = None
    sicuraId: Optional[str] = None
    tenableId: Optional[str] = None
    scanDate: Optional[str] = None
    scannedIPs: Optional[int] = None
    checks: Optional[int] = None
    vInfo: Optional[int] = None
    vLow: int = 0
    vMedium: int = 0
    vHigh: int = 0
    vCritical: int = 0
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ScanHistory model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """

        return ConfigDict(  # type: ignore
            get_by_parent_recursive="/api/{model_slug}/getAllByParentRecursive/{intParentID}/{strModule}/{filterDate}",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            get_count="/api/{model_slug}/getCount",
            get_scan_dates_by_parent="/api/{model_slug}/getScanDatesByParent/{intID}/{strModule}",
            filter_scans="/api/{model_slug}/filterScans/{intID}/{strModule}/{intPage}/{intPageSize}",
            insert="/api/{model_slug}",
            update="/api/{model_slug}",
            batch_create="/api/{model_slug}/batchCreate",
            get="/api/{model_slug}/find/{id}",
            find_by_guid="/api/{model_slug}/findByGUID/{strGUID}",
        )

    @classmethod
    def get_by_parent_recursive(cls, parent_id: int, parent_module: str, filter_date: str = "") -> List["ScanHistory"]:
        """
        Get a list of control implementations by plan ID.

        :param int parent_id: Parent ID
        :param str parent_module: Parent Module
        :param str filter_date: Filter Date
        :return: A list of ScanHistory objects
        :rtype: List[ScanHistory]
        :raises RequestException: If the API request fails
        """
        endpoint = cls.get_endpoint("get_by_parent_recursive").format(
            model_slug=cls._module_slug, intParentID=parent_id, strModule=parent_module, filterDate=filter_date
        )
        logger.debug(f"Endpoint: {endpoint}")
        response = cls._get_api_handler().get(endpoint=endpoint)
        logger.debug(f"Response: {response.status_code}")
        if response and response.ok:
            return [cls(**ci) for ci in response.json()]
        else:
            raise RequestException(f"API request failed with status code {response.status_code}")

    def __hash__(self) -> int:
        """
        Hash items in Scan class

        :return: Hashed Scan
        :rtype: int
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        return hash(
            (
                self.tenableId,
                self.parentId,
                self.parentModule,
                normalize_date(self.scanDate, fmt),
            )
        )

    def __eq__(self, other: Union["ScanHistory", dict]) -> bool:
        """
        Compare two Scan objects for equality.

        :param other: Other Scan object or dictionary to compare
        :type other: Union["ScanHistory", dict]
        :return: True if equal, False otherwise
        :rtype: bool
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        if isinstance(other, ScanHistory):
            return (
                self.tenableId == other.tenableId
                and self.parentId == other.parentId
                and self.parentModule == other.parentModule
                and normalize_date(self.scanDate, fmt) == normalize_date(other.scanDate, fmt)
            )

        return (
            self.tenableId == other["tenableId"]
            and self.parentId == other["parentId"]
            and self.parentModule == other["parentModule"]
            and normalize_date(self.scanDate, fmt) == normalize_date(other["scanDate"], fmt)
        )

    @staticmethod
    def post_scan(app: Application, api: Api, scan: "ScanHistory") -> "ScanHistory":
        """
        Post a Scan to RegScale.

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param ScanHistory scan: Scan Object
        :return: RegScale Scan
        :rtype: ScanHistory
        """
        res = api.post(url=app.config["domain"] + "/api/scanhistory", json=scan.dict())
        if res.status_code != 200:
            api.logger.error(res)
        return ScanHistory(**res.json())

    @staticmethod
    def group_vulns_by_severity(associated_vulns: List[dict]) -> Dict[str, List[dict]]:
        """
        Groups vulnerabilities by severity

        :param List[dict] associated_vulns: A list of associated vulnerabilities
        :return: Dictionary of vulnerabilities grouped by severity
        :rtype: Dict[str, List[dict]]
        """
        return {
            vuln["severity"]: [v for v in associated_vulns if v["severity"] == vuln["severity"]]
            for vuln in associated_vulns
        }

    @staticmethod
    def get_existing_scan_history(app: Application, reg_asset: dict) -> List[dict]:
        """
        Gets existing scan history for a RegScale asset

        :param Application app: Application Instance
        :param dict reg_asset: RegScale Asset
        :return: List of existing scan history
        :rtype: List[dict]
        """
        api = Api()
        res = api.get(url=app.config["domain"] + f"/api/scanhistory/getAllByParent/{reg_asset.id}/assets")
        if not res.raise_for_status():
            return res.json()

    @staticmethod
    def create_scan_from_tenable(
        associated_vulns: List[dict], reg_asset: dict, config: dict, tenant_id: int
    ) -> "ScanHistory":
        """
        Creates a Scan object from a Tenable scan

        :param List[dict] associated_vulns: List of associated vulnerabilities
        :param dict reg_asset: RegScale Asset
        :param dict config: Application Config
        :param int tenant_id: Tenant ID
        :return: Scan object
        :rtype: ScanHistory
        """
        grouped_vulns = ScanHistory.group_vulns_by_severity(associated_vulns)
        return ScanHistory(
            id=0,
            uuid=associated_vulns[0]["scan"]["uuid"],
            scanningTool="NESSUS",
            tenableId=associated_vulns[0]["scan"]["uuid"],
            scanDate=convert_datetime_to_regscale_string(associated_vulns[0]["scan"]["started_at"]),
            scannedIPs=1,
            checks=len(associated_vulns),
            vInfo=len(grouped_vulns["info"]) if "info" in grouped_vulns else 0,
            vLow=len(grouped_vulns["low"]) if "low" in grouped_vulns else 0,
            vMedium=len(grouped_vulns["medium"]) if "medium" in grouped_vulns else 0,
            vHigh=len(grouped_vulns["high"]) if "high" in grouped_vulns else 0,
            vCritical=(len(grouped_vulns["critical"]) if "critical" in grouped_vulns else 0),
            parentId=reg_asset.id,
            parentModule="assets",
            createdById=config["userId"],
            lastUpdatedById=config["userId"],
            dateCreated=convert_datetime_to_regscale_string(datetime.now()),
            tenantsId=tenant_id,
        )

    @staticmethod
    def prepare_scan_history_for_sync(
        app: Application,
        nessus_list: List[dict],
        existing_assets: List[dict],
    ) -> List["ScanHistory"]:
        """
        Prepares scan history data for synchronization.

        :param Application app: The Application object to use for database operations.
        :param List[dict] nessus_list: A list of Nessus scan history data.
        :param List[dict] existing_assets: A list of existing Asset objects to compare against.
        :return: List of scan history objects
        :rtype: List["ScanHistory"]
        """
        new_scan_history = []
        assets = {asset["asset"]["uuid"] for asset in nessus_list}
        asset_count = 0
        api = Api()
        config = app.config
        tenant_id = api.get(url=api.config["domain"] + "/api/tenants/config").json()["id"]

        def process_asset(asset: str) -> None:
            """
            Process an asset from the Nessus scan history data.

            :param str asset: Asset UUID
            :rtype: None
            """
            nonlocal asset_count
            asset_count += 1
            if asset_count % 100 == 0:
                app.logger.debug(f"Processing asset {asset_count} of {len(assets)}")
            associated_vulns = [ness for ness in nessus_list if ness["asset"]["uuid"] == asset]
            reg_assets = [reg for reg in existing_assets if reg["tenableId"] == asset]
            if reg_assets:
                reg_asset = reg_assets[0] if reg_assets else None
                existing_scans = ScanHistory.get_existing_scan_history(app, reg_asset)
                scan = ScanHistory.create_scan_from_tenable(associated_vulns, reg_asset, config, tenant_id)
                if scan not in existing_scans:
                    new_scan_history.append(scan)

        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(process_asset, assets)

        return new_scan_history

    @staticmethod
    def sync_scan_history_to_regscale(
        app: Application,
        new_scan_history: List["ScanHistory"],
    ) -> Tuple[List[Response], List["ScanHistory"]]:
        """
        Synchronizes scan history to RegScale

        :param Application app: Application Instance
        :param List[ScanHistory] new_scan_history: List of new scan history items
        :return: Tuple of Response and Scan
        :rtype: Tuple[List[Response], List[ScanHistory]]
        """
        tup_res = []
        if new_scan_history:
            app.logger.info(f"Inserting {len(new_scan_history)} new scan history item(s)")
            tup_res = ScanHistory.bulk_insert(app, new_scan_history)
            app.logger.info("Done!")
        return tup_res

    @staticmethod
    def convert_from_tenable(
        str_path: str,
        existing_assets: List[dict],
    ) -> List["ScanHistory"]:
        """
        Converts a TenableScan object to a RegScale Scan object

        :param str str_path: A path to a temporary directory to store the Nessus scan history data.
        :param List[dict] existing_assets: Existing RegScale Assets
        :return: List of RegScale Scans
        :rtype: List[ScanHistory]
        """
        app = Application()
        existing_scan_history_list = []
        file_list = list(Path(str_path).glob("*"))
        with create_progress_object() as progress:
            processing_pages = progress.add_task(
                f"[#ef5d23]Processing {len(file_list)} pages from Tenable...",
                total=len(file_list),
            )
            for index, file in enumerate(file_list):
                app.logger.debug(f"Processing page {index + 1} of {len(file_list)}")
                with open(file, "rb") as vuln_file_wrapper:
                    new_scan_data = []
                    # import dict from json file
                    nessus_list = [vuln.dict() for vuln in pickle.load(vuln_file_wrapper)]
                    new_scan_data.extend(ScanHistory.prepare_scan_history_for_sync(app, nessus_list, existing_assets))
                existing_scan_history_list.extend(ScanHistory.sync_scan_history_to_regscale(app, new_scan_data))
                progress.update(processing_pages, advance=1)

        return existing_scan_history_list

    @staticmethod
    def bulk_insert(
        app: Application, scans: List["ScanHistory"], max_workers: Optional[int] = 10
    ) -> List[Tuple[Response, "ScanHistory"]]:
        """Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[ScanHistory] scans: List of Scans
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :return: List of Tuples containing Response and Scan
        :rtype: List[Tuple[Response, ScanHistory]]
        """
        api = Api()
        res = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    ScanHistory.insert_scan,
                    app,
                    api,
                    scan,
                )
                for scan in scans
            ]
        for future in as_completed(futures):
            res.append(future.result()[1])
        return res

    @staticmethod
    def bulk_update(
        app: Application, scans: List["ScanHistory"], max_workers: Optional[int] = 10
    ) -> List["ScanHistory"]:
        """
        Bulk update assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[ScanHistory] scans: List of Scans
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :return: List of Scan
        :rtype: List[ScanHistory]
        """
        api = Api()
        res = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    ScanHistory.update_scan,
                    app,
                    api,
                    scan,
                )
                for scan in scans
            ]
        for future in as_completed(futures):
            res.append(future.result()[1])
        return res

    @staticmethod
    def update_scan(app: Application, api: Api, regscale_scan: "ScanHistory") -> Tuple[Response, "ScanHistory"]:
        """
        Api wrapper to update a scan

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param ScanHistory regscale_scan: Regscale Scan
        :return: RegScale Scan and Response
        :rtype: Tuple[Response, ScanHistory]
        """
        scan_res = api.put(
            url=app.config["domain"] + "/api/scanHistory",  # no ID needed on this endpoint
            json=regscale_scan.model_dump(),
        )
        regscale_scan.id = scan_res.json()["id"]
        return scan_res, regscale_scan

    @staticmethod
    def insert_scan(app: Application, api: Api, regscale_scan: "ScanHistory") -> Tuple[Response, "ScanHistory"]:
        """
        Api wrapper to insert a scan

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param ScanHistory regscale_scan: Regscale Scan
        :return: RegScale Scan and Response
        :rtype: Tuple[Response, ScanHistory]
        """
        scan_res = api.post(
            url=app.config["domain"] + "/api/scanHistory",
            json=regscale_scan.model_dump(),
        )
        if not scan_res.ok:
            api.logger.error(f"Unable to insert scan: {scan_res.status_code}: {scan_res.reason}. {scan_res.text}")
        else:
            try:
                regscale_scan.id = scan_res.json()["id"]
            except (KeyError, JSONDecodeError) as ex:
                api.logger.error(f"Unable to insert scan: {ex}")
        return scan_res, regscale_scan


class Scan(ScanHistory):
    """
    DEPRECATED: Scan class is deprecated. Use ScanHistory instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Scan class is deprecated. Use ScanHistory instead.",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
