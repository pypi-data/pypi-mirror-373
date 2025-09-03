"""Container Scan Abstract"""

import ast
import json
import logging
import re
import shutil
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import datetime
from os import PathLike
from typing import TYPE_CHECKING, Any, Callable, Generator, Iterator, List, Optional, Sequence, TextIO, Tuple, Union

if TYPE_CHECKING:
    from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding

from pathlib import Path

import click
import xmltodict
from openpyxl.reader.excel import load_workbook

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    check_file_path,
    create_progress_object,
    creation_date,
    error_and_exit,
    get_current_datetime,
)
from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.integrations.scanner_integration import ScannerIntegration
from regscale.models import IssueStatus, Metadata, regscale_models
from regscale.models.app_models.mapping import Mapping
from regscale.models.regscale_models import Asset, File, IssueSeverity, Vulnerability

logger = logging.getLogger(__name__)

DT_FORMAT = "%Y-%m-%d"


class FlatFileIntegration(ScannerIntegration):
    """
    Flat File Integration
    """

    title = "Flat File Integration"
    # Required fields from ScannerIntegration
    asset_identifier_field = "name"
    type = ScannerIntegration.type.CONTROL_TEST

    def __init__(
        self,
        plan_id: int,
        asset_identifier_field: str = "name",
        finding_severity_map: Optional[dict] = None,
        **kwargs: Any,
    ):
        self.asset_identifier_field = asset_identifier_field
        if finding_severity_map:
            self.finding_severity_map = finding_severity_map
        else:
            self.finding_severity_map = {
                "Critical": regscale_models.IssueSeverity.Critical,
                "High": regscale_models.IssueSeverity.High,
                "Medium": regscale_models.IssueSeverity.Moderate,
                "Moderate": regscale_models.IssueSeverity.Moderate,
                "Low": regscale_models.IssueSeverity.Low,
            }
        super().__init__(plan_id=plan_id, **kwargs)
        self.is_component = kwargs.get("is_component", False)

    def set_asset_identifier_field(self, asset_identifier_field: str) -> None:
        """
        Set the asset identifier field

        :param str asset_identifier_field: The asset identifier field to set
        """
        self.asset_identifier_field = asset_identifier_field

    def fetch_assets(self, *args: Tuple, **kwargs: dict) -> Iterator["IntegrationAsset"]:
        """
        Fetches assets from FlatFileImporter

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationAsset]
        """
        integration_assets = kwargs.get("integration_assets")
        for asset in integration_assets:
            yield asset

    def fetch_findings(self, *args: Tuple, **kwargs: dict) -> Iterator["IntegrationFinding"]:
        """
        Fetches findings from the integration

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationFinding]

        """
        logger.debug(f"Asset identifier field: {self.asset_identifier_field}")
        integration_findings = kwargs.get("integration_findings")
        for vuln in integration_findings:
            yield vuln


class FlatFileImporter(ABC):
    """
    Abstract class for container scan integration

    :param dict **kwargs: Keyword arguments
    """

    name: str
    mapping: "Mapping"

    def __init__(self, **kwargs):
        if finding_severity_map := kwargs.pop("finding_severity_map", None):
            self.finding_severity_map = finding_severity_map
        else:
            self.finding_severity_map = {
                "Critical": regscale_models.IssueSeverity.Critical,
                "High": regscale_models.IssueSeverity.High,
                "Medium": regscale_models.IssueSeverity.Moderate,
                "Moderate": regscale_models.IssueSeverity.Moderate,
                "Low": regscale_models.IssueSeverity.Low,
            }

        kwargs = self.update_kwargs(kwargs)

        # empty generator
        self.integration_assets: Generator["IntegrationAsset", None, None] = (x for x in [])
        self.integration_findings: Generator["IntegrationAsset", None, None] = (x for x in [])
        self.field_names = [
            "logger",
            "headers",
            "file_type",
            "app",
            "file_path",
            "name",
            "parent_id",
            "parent_module",
            "scan_date",
            "asset_func",
            "vuln_func",
            "issue_func",
            "extra_headers_allowed",
            "mapping",
            "ignore_validation",
            "header_line_number",
            "is_component",
            "object_id",
            "plan_id",
            "disable_mapping",
            "mappings_path",
            "upload_file",
            "file_name",
        ]
        self.asset_identifier_field = kwargs.pop("asset_identifier_field", "name")
        asset_count = kwargs.pop("asset_count") if "asset_count" in kwargs else 0
        vuln_count = kwargs.pop("vuln_count") if "vuln_count" in kwargs else 0
        _attributes = namedtuple(
            "Attributes",
            self.field_names,
            defaults=[None] * len(self.field_names),
        )
        self.attributes = _attributes(**kwargs)

        self.file_type = kwargs.get("file_type", ".csv")
        self.extra_headers_allowed = kwargs.get("extra_headers_allowed", False)
        self.scan_date = safe_datetime_str(kwargs.get("scan_date"))
        self.attributes.logger.info("Processing %s...", self.attributes.file_path)
        self.formatted_headers = None
        self.config = self.attributes.app.config
        self.header, self.file_data = self.file_to_list_of_dicts()
        self.data = {
            "assets": [],
            "issues": [],
            "scans": [],
            "vulns": [],
        }
        self.create_epoch = str(int(creation_date(self.attributes.file_path)))
        flat_int = FlatFileIntegration(
            plan_id=self.attributes.plan_id or self.attributes.object_id or self.attributes.parent_id,
            is_component=self.attributes.is_component,
            asset_identifier_field=self.asset_identifier_field,
            finding_severity_map=self.finding_severity_map,
        )
        flat_int.asset_identifier_field = self.asset_identifier_field
        logger.debug(f"Asset Identifier Field: {flat_int.asset_identifier_field}")
        flat_int.title = self.attributes.name
        self.create_assets(kwargs["asset_func"])  # type: ignore # Pass in the function to create an asset
        self.create_vulns(kwargs["vuln_func"])  # type: ignore # Pass in the function to create a vuln
        if asset_count:
            flat_int.num_assets_to_process = asset_count
        elif isinstance(self.data["assets"], list) and not asset_count:
            flat_int.num_assets_to_process = len(self.data["assets"])
        if vuln_count:
            flat_int.num_findings_to_process = vuln_count
        elif isinstance(self.data["vulns"], list) and not vuln_count:
            flat_int.num_findings_to_process = len(self.data["vulns"])
        flat_int.sync_assets(
            plan_id=self.attributes.plan_id,
            is_component=self.attributes.is_component,
            integration_assets=self.integration_assets,
            title=self.attributes.name,
            asset_count=flat_int.num_assets_to_process,
        )
        flat_int.sync_findings(
            plan_id=self.attributes.plan_id,
            is_component=self.attributes.is_component,
            integration_findings=self.integration_findings,
            title=self.attributes.name,
            finding_count=flat_int.num_findings_to_process,
            enable_finding_date_update=True,
            scan_date=self.scan_date,
        )
        self.clean_up()

    def update_kwargs(self, kwargs: dict) -> dict:
        """
        Update the kwargs with the default values

        :param dict kwargs: The kwargs to update
        :return: The updated kwargs
        :rtype: dicta
        """
        # Set the parent_id, parent_module, and plan_id if they are not provided
        if "parent_id" not in kwargs and "object_id" in kwargs:
            kwargs["parent_id"] = kwargs["object_id"]
            kwargs["plan_id"] = kwargs["object_id"]
        if kwargs.get("is_component", False):
            kwargs["parent_module"] = regscale_models.Component.get_module_string()
        else:
            kwargs["parent_module"] = regscale_models.SecurityPlan.get_module_string()

        # if plan id is still not set, set it to the object id
        if "plan_id" not in kwargs or not kwargs["plan_id"]:
            kwargs["plan_id"] = kwargs["object_id"]

        if "app" not in kwargs:
            kwargs["app"] = Application()
        return kwargs

    def parse_finding(self, vuln: Union[Vulnerability, "IntegrationFinding"]) -> Optional["IntegrationFinding"]:
        """
        Parses a vulnerability object into an IntegrationFinding object

        :param Union[Vulnerability, IntegrationFinding] vuln: A vulnerability object
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        from regscale.integrations.scanner_integration import IntegrationFinding

        if isinstance(vuln, IntegrationFinding):
            # We will store this in the properties subsystem of issue.
            vuln.extra_data["source_file_path"] = self.attributes.file_path
            return vuln

        try:
            asset_id = vuln.dns or vuln.ipAddress
            if not asset_id:
                return None
            severity = self.finding_severity_map.get(vuln.severity.capitalize(), regscale_models.IssueSeverity.Low)
            status = self.map_status_to_issue_status(vuln.status)
            cve: Optional[str] = getattr(vuln, "cve", "")
            extract_vuln: Any = self.extract_ghsa_strings(getattr(vuln, "plugInName", ""))
            plugin_name = getattr(vuln, "plugInName", getattr(vuln, "title", ""))
            plugin_id = str(vuln.plugInId) if vuln.plugInId else ""
            non_cve_identifier = self.determine_non_cve_identifier(cve)
            if not self.assert_valid_cve(cve):
                if isinstance(extract_vuln, list):
                    cve = ", ".join(extract_vuln)
                if isinstance(extract_vuln, str):
                    # Coalfire requires vulnerabilities to be stuffed into this field, regardless if they start
                    # with CVE or not.
                    cve = extract_vuln
            if not self.assert_valid_cve(cve):
                if not non_cve_identifier:
                    plugin_name = cve
                cve = ""
            remediation_description = ""
            if remediation := vuln.extra_data.get("solution"):
                if isinstance(remediation, list):
                    remediation_description = ", ".join(remediation)
                elif isinstance(remediation, dict):
                    remediation_description = "\n".join([f"{k}: {v}" for k, v in remediation.items()])
                else:
                    remediation_description = remediation
            return IntegrationFinding(
                control_labels=[],  # Add an empty list for control_labels
                category=f"{self.name} Vulnerability",  # Add a default category
                title=vuln.title,
                description=vuln.description,
                severity=severity,
                status=status,
                asset_identifier=asset_id,
                external_id=non_cve_identifier or plugin_id,
                rule_id=plugin_id,
                first_seen=vuln.firstSeen,
                last_seen=vuln.lastSeen,
                remediation=remediation_description,
                cvss_score=vuln.vprScore,
                cve=cve,
                cvss_v3_base_score=vuln.cvsSv3BaseScore,
                source_rule_id=plugin_id,
                vulnerability_type="Vulnerability Scan",
                baseline=f"{self.name} Host",
                results=vuln.title,
                plugin_id=plugin_id or non_cve_identifier or plugin_name,
                plugin_name=plugin_name,
                date_created=vuln.firstSeen,
                date_last_updated=vuln.lastSeen,
                due_date="",  # Override the default factory, we want ScannerIntegration to handle this
            )
        except (KeyError, TypeError, ValueError) as e:
            self.attributes.logger.error("Error parsing Wiz finding: %s", str(e), exc_info=True)
            return None

    def parse_asset(self, asset: Union[Asset, "IntegrationAsset"]) -> "IntegrationAsset":
        """
        Converts Asset -> IntegrationAsset

        :param Union[Asset, IntegrationAsset] asset: The asset to parse
        :return: The parsed IntegrationAsset
        :rtype: IntegrationAsset
        """
        from regscale.integrations.scanner_integration import IntegrationAsset

        if isinstance(asset, IntegrationAsset):
            return asset

        return IntegrationAsset(
            name=asset.name,
            external_id=asset.otherTrackingNumber,
            other_tracking_number=asset.otherTrackingNumber,
            identifier=(
                getattr(asset, self.asset_identifier_field)
                if hasattr(asset, self.asset_identifier_field)
                else asset.name
            ),
            asset_type=asset.assetType,
            asset_owner_id=asset.assetOwnerId,
            parent_id=self.attributes.parent_id,
            parent_module=self.attributes.parent_module,
            asset_category=asset.assetCategory,
            date_last_updated=asset.dateLastUpdated,
            status=asset.status,
            ip_address=asset.ipAddress if asset.ipAddress else "Unknown",
            software_vendor=asset.softwareVendor,
            software_version=asset.softwareVersion,
            software_name=asset.softwareName,
            location=asset.location,
            notes=asset.notes,
            model=asset.model,
            serial_number=asset.serialNumber,
            is_public_facing=False,
            azure_identifier=asset.azureIdentifier,
            mac_address=asset.macAddress,
            fqdn=asset.fqdn,
            disk_storage=0,
            cpu=0,
            ram=0,
            operating_system=asset.operatingSystem,
            os_version=asset.osVersion,
            end_of_life_date=asset.endOfLifeDate,
            vlan_id=asset.vlanId,
            uri=asset.uri,
            aws_identifier=asset.awsIdentifier,
            google_identifier=asset.googleIdentifier,
            other_cloud_identifier=asset.otherCloudIdentifier,
            patch_level=asset.patchLevel,
            cpe=asset.cpe,
            component_names=[],
            source_data=None,
            url=None,
            ports_and_protocols=[],
            software_inventory=asset.extra_data.get("software_inventory", []),
        )

    @staticmethod
    def create_asset_type(asset_type: str) -> str:
        """
        Create asset type if it does not exist and reformat the string to Title Case

        :param str asset_type: The asset to parse
        :return: Asset type in title case
        :rtype: str
        """
        #
        asset_type = asset_type.title().replace("_", " ")
        meta_data_list = Metadata.get_metadata_by_module_field(module="assets", field="Asset Type")
        if not any(meta_data.value == asset_type for meta_data in meta_data_list):
            Metadata(
                field="Asset Type",
                module="assets",
                value=asset_type,
            ).create()
        return asset_type

    def file_to_list_of_dicts(self) -> tuple[Optional[Sequence[str]], list[Any]]:
        """
        Converts a csv file to a list of dictionaries

        :raises AssertionError: If the headers in the csv/xlsx file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple[Optional[Sequence[str]], list[Any]]
        """
        header = []
        data = []
        start_line_number = 0 if not self.attributes.header_line_number else self.attributes.header_line_number
        # added encoding errors="replace" param to replace encoding characters it can on error, ignoring or not including could throw errors or result in missing data
        with open(self.attributes.file_path, encoding="utf-8-sig", errors="replace") as file:
            # Skip lines until the start line is reached
            for _ in range(start_line_number):
                next(file)
            if file.name.endswith((".csv", ".xlsx")):
                # Use the validater data for CSV and XLSX files to ensure proper mapping validation
                data = self.validater.data.to_dict("records")
                header = list(self.validater.parsed_headers)
            elif file.name.endswith(".json"):
                try:
                    # Filter possible null values
                    file_data = json.load(file)
                    if isinstance(file_data, dict):
                        data = file_data
                    if isinstance(file_data, list):
                        data = [dat for dat in file_data if dat]
                except json.JSONDecodeError:
                    raise AssertionError("Invalid JSON file")
            elif file.name.endswith(".xml"):
                data = self.convert_xml_to_dict(file)
            else:
                raise AssertionError("Unsupported file type")
        return header, data

    def handle_extra_headers(self, header: list) -> None:
        """
        Handle extra headers in the csv file

        :param list header: The headers from the csv file
        :raises AssertionError: If the headers in the csv file do not contain the required headers
        """
        extra_headers = [column for column in header if column not in self.attributes.headers]
        required_headers = [column for column in header if column in self.attributes.headers]

        if not all(item in self.attributes.headers for item in required_headers):
            raise AssertionError(
                "The headers in the csv file do not contain the required headers "
                + f"headers, is this a valid {self.attributes.name} {self.file_type} file?"
            )

        if extra_headers:
            self.attributes.logger.warning(
                "The following extra columns were found and will be ignored: %s",
                ", ".join(extra_headers),
            )

    def convert_xlsx_to_dict(self, file: TextIO, start_line_number: int = 0) -> tuple:
        """
        Converts a xlsx file to a list of dictionaries

        :param TextIO file: The xlsx file to convert
        :param int start_line_number: The line number to start reading from
        :return: Tuple of data and header from xlsx file
        :rtype: tuple
        """
        logger.debug("flatfileimporter: Converting xlsx to dict")
        # Load the workbook
        workbook = load_workbook(filename=file.name)

        # Select the first sheet
        sheet = workbook.active

        # Get the data from the sheet
        data = list(sheet.values)

        # Get the header from the first row
        header = list(data[start_line_number])

        # Get the rest of the data
        data = data[start_line_number + 1 :]

        # Convert the data to a dictionary
        data_dict = [dict(zip(header, row)) for row in data]

        # Loop through the data and convert any string lists to lists
        for dat in data_dict:
            for key, val in dat.items():
                if isinstance(val, str) and val.startswith("["):
                    try:
                        dat[key] = ast.literal_eval(dat[key])
                    except SyntaxError as rex:
                        # Object is probably not a list, so just leave it as a string
                        self.attributes.app.logger.debug("SyntaxError: %s", rex)
        logger.debug("flatfileimporter: Done converting xlsx to dict.")
        return data_dict, header

    def count_vuln_by_severity(self, severity: str, asset_id: int) -> int:
        """
        Count the number of vulnerabilities by the provided severity

        :param str severity: The severity to count
        :param int asset_id: The asset id to match the vulnerability's parentId
        :return: The number of vulnerabilities
        :rtype: int
        """
        return len([vuln for vuln in self.data["vulns"] if vuln.parentId == asset_id and vuln.severity == severity])

    def create_assets(self, func: Callable) -> None:
        """
        Create assets in RegScale from csv file

        :param Callable func: Function to create asset
        :return: None
        :rtype: None
        """
        self.process_assets(func=func)

    def process_assets(self, func: Callable) -> None:
        """
        Process the assets in the data
        """
        from regscale.integrations.scanner_integration import IntegrationAsset

        # The passed function creates asset objects. Convert to IntegrationAsset here
        if isinstance(self.file_data, list):
            for dat in self.file_data:
                self.process_asset_data(dat, func)
        elif isinstance(self.file_data, dict):
            self.data["assets"] = func(self.file_data)
        if isinstance(self.data["assets"], Iterator):
            self.integration_assets = self.data["assets"]
            return None
        elif isinstance(self.data["assets"], IntegrationAsset):
            self.data["assets"] = [self.data["assets"]]
        self.integration_assets = (self.parse_asset(asset) for asset in self.data["assets"])

    def process_asset_data(self, dat: Any, func: Callable) -> None:
        """
        Process the asset data

        :param Any dat: The data to process
        :param Callable func: The function to process the data
        :rtype: None
        """
        from regscale.integrations.scanner_integration import IntegrationAsset

        res = func(dat)
        if not res:
            return
        if isinstance(res, Asset) and res not in self.data["assets"]:
            self.data["assets"].append(res)
        elif isinstance(res, IntegrationAsset):
            self.data["assets"].append(res)
        elif isinstance(res, list):
            for asset in res:
                if asset not in self.data["assets"]:
                    self.data["assets"].append(asset)

    def create_vulns(self, func: Callable) -> None:
        """
        Create vulns in RegScale from csv file

        :param Callable func: Function to create vuln
        :rtype: None
        """
        from regscale.integrations.scanner_integration import IntegrationFinding

        with create_progress_object() as vuln_progress:
            vuln_task = vuln_progress.add_task("Processing vulnerabilities...", total=len(self.file_data))
            try:
                res = func(self.file_data)
                if isinstance(res, list):
                    self.integration_findings = res
                    self.data["vulns"] = res
                    vuln_progress.update(vuln_task, completed=len(self.file_data))
                    return
            except Exception as e:
                self.attributes.logger.debug(
                    "Cannot process vulns as a whole, now iterating all data to parse vulns: %s", str(e)
                )
            for ix, dat in enumerate(self.file_data):
                vuln = func(dat, index=ix)
                if not vuln:
                    vuln_progress.advance(vuln_task, advance=1)
                    continue

                if isinstance(vuln, IntegrationFinding):
                    self.data["vulns"].append(vuln)
                if isinstance(vuln, list):
                    for v in vuln:
                        self.data["vulns"].append(v)
                if isinstance(vuln, Iterator):
                    self.integration_findings = vuln
                    self.data["vulns"] = vuln
                    vuln_progress.update(vuln_task, completed=len(self.file_data))
                    return None
                vuln_progress.advance(vuln_task, advance=1)
        self.integration_findings = (self.parse_finding(vuln) for vuln in self.data["vulns"])

    def clean_up(self, file_path=None) -> None:
        """
        Move the Nexpose file to the processed folder

        :rtype: None
        """
        if not file_path:
            file_path = self.attributes.file_path
        file_path = Path(file_path)
        processed_dir = file_path.parent / "processed"
        file_name = (f"{file_path.stem}_" + f"{get_current_datetime('%Y%m%d-%I%M%S%p')}").replace(" ", "_")
        new_name = (file_path.parent / file_name).with_suffix(file_path.suffix)
        new_file_path = file_path.rename(new_name)
        if self.attributes.parent_id:
            check_file_path(str(processed_dir.absolute()))
            try:
                self.attributes.logger.info(
                    "Renaming %s to %s...",
                    file_path.name,
                    new_file_path.name,
                )
                shutil.move(new_file_path, processed_dir)
                self.attributes.logger.info("File moved to %s", processed_dir)
            except shutil.Error:
                self.attributes.logger.debug(
                    "File %s already exists in %s",
                    new_file_path.name,
                    processed_dir,
                )
        if self.attributes.upload_file and self.attributes.parent_id and self.attributes.parent_module:
            api = Api()
            self.attributes.logger.info(
                "Uploading %s to RegScale %s #%i...",
                new_file_path,
                self.attributes.parent_module,
                self.attributes.parent_id,
            )
            if File.upload_file_to_regscale(
                file_name=str(processed_dir / new_file_path.name),
                parent_id=self.attributes.parent_id,
                parent_module=self.attributes.parent_module,
                api=api,
            ):
                self.attributes.logger.info("File uploaded to RegScale succesfully.")
            else:
                self.attributes.logger.error("File upload to RegScale failed.")

    @abstractmethod
    def create_asset(self):
        """Create an asset"""

    @abstractmethod
    def create_vuln(self):
        """Create a Vulnerability"""

    @staticmethod
    def import_files(
        import_type: Callable,
        import_name: str,
        file_types: Union[str, list[str]],
        folder_path: PathLike[str],
        object_id: int,
        scan_date: datetime,
        mappings_path: Union[PathLike[str], Path],
        disable_mapping: bool,
        s3_bucket: str,
        s3_prefix: str,
        aws_profile: str,
        upload_file: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """
        Import files from the given file path

        :param Callable import_type: Function to import files
        :param str import_name: The name of the import type
        :param Union[str, list[str]] file_types: The file types to glob and import, e.g. ".csv" or [".csv", ".xlsx"]
        :param PathLike[str] folder_path: The folder path to import from
        :param int object_id: The RegScale SSP ID
        :param datetime scan_date: The date of the scan
        :param Union[PathLike[str], Path] mappings_path: The path to the mappings file
        :param bool disable_mapping: Whether to disable custom mappings
        :param str s3_bucket: The S3 bucket to download the files from
        :param str s3_prefix: The S3 prefix to download the files from
        :param str aws_profile: The AWS profile to use for S3 access
        :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
        """
        from regscale.core.app.application import Application
        from regscale.core.app.utils.file_utils import download_from_s3
        from regscale.exceptions import ValidationException
        from regscale.validation.record import validate_regscale_object

        if s3_bucket:
            download_from_s3(s3_bucket, s3_prefix, folder_path, aws_profile)
        app = Application()

        # Validate the parent_id is a valid RegScale object
        is_component = kwargs.get("is_component", False)
        if is_component and not validate_regscale_object(object_id, "components"):
            app.logger.warning("Component #%i is not a valid RegScale Component.", object_id)
            return
        elif not is_component and not validate_regscale_object(object_id, "securityplans"):
            app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", object_id)
            return

        if not scan_date or not FlatFileImporter.check_date_format(scan_date):
            scan_date = datetime.now()
        if isinstance(file_types, str):
            file_types = [file_types]
        files = []
        for file_type in file_types:
            files.extend(
                list(Path(folder_path).glob(f"*{file_type if file_type.startswith('.') else '.' + file_type}"))
            )
        if len(files) == 0:
            app.logger.warning(f"No {import_name} ({'/'.join(file_types)}) files found in the specified folder.")
            return
        for file in files:
            try:
                import_type(
                    name=import_name,
                    file_path=str(file),
                    object_id=object_id,
                    scan_date=scan_date,
                    mappings_path=mappings_path,
                    disable_mapping=disable_mapping,
                    upload_file=upload_file,
                    file_type=file.suffix,
                    **kwargs,
                )
            except ValidationException as e:
                app.logger.error(f"Validation error: {e}")
                continue

    @classmethod
    def common_scanner_options(
        cls, message: str, prompt: str, import_name: str, support_component: bool = False
    ) -> Callable[[Callable], click.option]:
        """
        Common options for container scanner integrations

        :param str message: The message to display to the user
        :param str prompt: The prompt to display to the user
        :param str import_name: The name of the import function
        :param bool support_component: Whether to support importing data to a component
        :return: The decorated function
        :rtype: Callable[[Callable], click.option]
        """
        import os

        from regscale.models.app_models.click import NotRequiredIf

        mapping_dir = os.path.join("./", "mappings", import_name)

        def decorator(this_func) -> Callable[[Callable], click.option]:
            """
            Decorator for common options
            """

            this_func = click.option(
                "--s3-bucket",
                help="S3 bucket to download scan files from",
                type=str,
                cls=NotRequiredIf,
                not_required_if=["folder_path"],
            )(this_func)
            this_func = click.option(
                "--s3-prefix",
                help="Prefix (folder path) within the S3 bucket",
                type=str,
                default="",
                cls=NotRequiredIf,
                not_required_if=["folder_path"],
            )(this_func)
            this_func = click.option(
                "--aws-profile",
                help="AWS profile to use for S3 access",
                type=str,
                default="regscale",
                cls=NotRequiredIf,
                not_required_if=["folder_path"],
            )(this_func)
            this_func = click.option(
                "--folder_path",
                "-f",
                help=message,
                prompt=prompt,
                type=click.Path(exists=True, dir_okay=True, resolve_path=True),
                cls=NotRequiredIf,
                not_required_if=["s3_bucket", "s3_prefix"],
            )(this_func)
            if support_component:
                # This will be the normal behavior for the imports in the future, but for now we will support it for Trivy, Grype, and OpenText
                this_func = click.option(
                    "-id",
                    "-p",
                    "--regscale_ssp_id",
                    "--plan_id",
                    type=click.INT,
                    help="The ID number from RegScale of the System Security Plan.",
                    cls=NotRequiredIf,
                    not_required_if=["component_id"],
                )(this_func)
                this_func = click.option(
                    "-c",
                    "--component_id",
                    type=click.INT,
                    help="The ID number from RegScale of the Component.",
                    cls=NotRequiredIf,
                    not_required_if=["regscale_ssp_id"],
                )(this_func)
            else:
                this_func = click.option(
                    "--regscale_ssp_id",
                    "-id",
                    type=click.INT,
                    help="The ID number from RegScale of the System Security Plan.",
                    prompt="Enter RegScale System Security Plan ID",
                    required=True,
                )(this_func)
            this_func = click.option(
                "--scan_date",
                "-sd",
                type=click.DateTime(formats=[DT_FORMAT]),
                help="The scan date of the file.",
                required=False,
            )(this_func)
            this_func = click.option(
                "--mappings_path",
                "-m",
                type=click.Path(dir_okay=True, resolve_path=True),
                help=f"The CLI will use the custom header from the provided mappings directory or file, example is {mapping_dir}",
                default=mapping_dir,
                required=False,
            )(this_func)
            this_func = click.option(
                "--disable_mapping",
                "-dm",
                help="Whether to disable the default mapping",
                is_flag=True,
            )(this_func)
            this_func = click.option(
                "--upload_file",
                "--upload",
                help="Whether to upload the file to RegScale after processing. Default is True.",
                default=True,
                required=False,
            )(this_func)
            return this_func

        return decorator

    @classmethod
    def show_mapping(cls, group: click.Group, import_name: str, file_type: Optional[str] = None) -> click.Command:
        """
        Show the mapping for the given import_name

        :param click.Group group: The click group to register the command with
        :param str import_name: The name of the import function
        :param Optional[str] file_type: The file type of the import, defaults to None
        :return: The decorated function.
        :rtype: Callable[[Callable], click.option]
        """
        import os

        # Define default path based on import_name and file_type
        default = os.path.join("./", "mappings", import_name, f"{file_type}_mapping.json") if file_type else None

        @click.command(help=f"Show the mapping file used during {import_name} imports.")
        @click.option(
            "--file_path",
            "-f",
            help="File path to the mapping file to display",
            type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
            required=True,
            default=default if default else None,
        )
        # Define the desired function behavior
        def wrapped_func(file_path: str) -> None:
            """
            Show the mapping file used during imports
            """
            from rich.console import Console

            console = Console()
            with open(file_path, "r", encoding="utf-8") as file:
                mapping = json.load(file)
            dat = json.dumps(mapping, indent=4)
            console.print(f"{file_path} mapping:")
            console.print(dat)

        # Register the decorated function with the given click group
        group.add_command(wrapped_func, name="show_mapping")

    @staticmethod
    def check_date_format(the_date: Any) -> bool:
        """
        Check if the date is in the correct format

        :param Any the_date: The date to check
        :return: True if the date is in the correct format
        :rtype: bool

        """
        try:
            if isinstance(the_date, str):
                the_date = datetime.strptime(the_date, DT_FORMAT)
            # make sure the date is not in the future
            if the_date >= datetime.now():
                error_and_exit("The scan date cannot be in the future.")
            res = True
        except ValueError:
            error_and_exit("Incorrect data format, should be YYYY-MM-DD")
        return res

    @staticmethod
    def convert_xml_to_dict(file: TextIO) -> dict:
        """
        Convert an XML file to a Python dictionary.

        :param TextIO file: The file object representing the XML file.
        :return: A dictionary representation of the XML content.
        :rtype: dict
        """

        xml_content = file.read()
        dict_content = xmltodict.parse(xml_content)
        return dict_content

    @staticmethod
    def determine_severity(s: str) -> str:
        """
        Determine the CVSS severity of the vulnerability

        :param str s: The severity
        :return: The severity
        :rtype: str
        """
        mapping = {
            "critical": IssueSeverity.Critical,
            "high": IssueSeverity.High,
            "medium": IssueSeverity.Moderate,
            "moderate": IssueSeverity.Moderate,
            "low": IssueSeverity.Low,
            "informational": IssueSeverity.NotAssigned,
            "none": IssueSeverity.NotAssigned,
            "info": IssueSeverity.NotAssigned,
            "unknown": IssueSeverity.NotAssigned,
        }
        severity = "info"
        if s:
            severity = s.lower()
        return mapping.get(severity, IssueSeverity.NotAssigned)

    @staticmethod
    def map_status_to_issue_status(status: str) -> IssueStatus:
        """
        Maps the vuln status to issue status
        :param str status: Status of the vulnerability
        :returns: Issue status
        :rtype: IssueStatus
        """
        issue_status = IssueStatus.Open
        if status.lower() in ["resolved", "rejected", "closed", "completed"]:
            issue_status = IssueStatus.Closed
        return issue_status

    @staticmethod
    def extract_ghsa_strings(text: str) -> Union[List[str], str]:
        """
        Extract GHSA strings from a given text.

        :param str text: The input text containing GHSA strings
        :return: A list of GHSA strings or the input text if no GHSA strings are found
        :rtype: Union[List[str], str]
        """
        ghsa_pattern = r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}"
        res = re.findall(ghsa_pattern, text)
        if res:
            return res
        return text

    @staticmethod
    def assert_valid_cve(cve: str) -> bool:
        """
        Assert that the CVE identifier is valid

        :param str cve: The CVE identifier
        :return: True if the CVE identifier is valid
        :rtype: bool
        """
        pattern = r"^CVE-\d{4}-\d{4,}$"
        return bool(re.match(pattern, cve))

    @staticmethod
    def determine_non_cve_identifier(vuln_id: str) -> str:
        """
        Determine the non-CVE identifier based on the CVE string

        :param str vuln_id: The Vulnerability Identifier string
        :return: The non-CVE identifier
        :rtype: str
        """
        match_regex = "^(?:(?:ALSA|ALSA2|ALAS|ALAS2|ELSA)-(?:19|20)\\d{2}-\\d{4,5}|GHSA-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4})$"
        return vuln_id if re.match(match_regex, vuln_id) else ""
