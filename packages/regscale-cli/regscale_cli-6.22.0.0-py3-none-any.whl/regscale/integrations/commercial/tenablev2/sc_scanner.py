"""
Module for Tenable SC vulnerability scanning integration.
"""

import logging
import queue
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor, wait
from threading import current_thread, get_ident, get_native_id
from typing import Any, Iterator, List, Optional, Tuple

from pathlib import Path
from tenable.sc.analysis import AnalysisResultsIterator

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import epoch_to_datetime
from regscale.core.app.utils.pickle_file_handler import PickleFileHandler
from regscale.integrations.commercial.tenablev2.authenticate import gen_tsc
from regscale.integrations.commercial.tenablev2.utils import get_filtered_severities
from regscale.integrations.integration_override import IntegrationOverride
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
    issue_due_date,
)
from regscale.models import regscale_models
from regscale.models.integration_models.tenable_models.models import TenableAsset
from regscale.utils.threading import ThreadSafeCounter

logger = logging.getLogger("regscale")


class SCIntegration(ScannerIntegration):
    """
    Tenable SC Integration class that is responsible for fetching assets and findings from Tenable
    """

    ASSETS_FILE = "./artifacts/tenable_sc_assets.jsonl"
    FINDINGS_FILE = "./artifacts/tenable_sc_findings.jsonl"

    finding_severity_map = {
        "Info": regscale_models.IssueSeverity.NotAssigned,
        "Low": regscale_models.IssueSeverity.Low,
        "Medium": regscale_models.IssueSeverity.Moderate,
        "High": regscale_models.IssueSeverity.High,
        "Critical": regscale_models.IssueSeverity.Critical,
    }
    # Required fields from ScannerIntegration
    title = "Tenable SC"
    asset_identifier_field = "tenableId"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the SCIntegration class

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.scan_date = kwargs.get("scan_date")
        self.plan_id = kwargs.get("plan_id")
        self.is_component = kwargs.get("is_component", False) is True
        self.client = None
        self.closed_count = 0
        self.batch_size = kwargs.get("batch_size", 1000)
        if self.is_component:
            from regscale.validation.record import validate_regscale_object

            if validate_regscale_object(
                parent_id=self.plan_id, parent_module=regscale_models.Component.get_module_string()
            ):
                component = regscale_models.Component.get_object(self.plan_id)
                self.component_title = component.title
        else:
            self.component_title = None

    def authenticate(self) -> None:
        """Authenticate to Tenable SC."""
        self.client = gen_tsc()

    def fetch_assets(self, *args: Any, **kwargs: Any) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from SCIntegration

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationAsset]
        """
        integration_assets = kwargs.get("integration_assets", [])
        yield from integration_assets

    def fetch_findings(self, *args: Tuple, **kwargs: dict) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the SCIntegration

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationFinding]

        """
        integration_findings = kwargs.get("integration_findings", [])
        yield from integration_findings

    def parse_findings(self, vuln: TenableAsset, integration_mapping: Any) -> List[IntegrationFinding]:
        """
        Parses a TenableAsset into an IntegrationFinding object

        :param TenableAsset vuln: The Tenable SC finding
        :param Any integration_mapping: The IntegrationMapping object
        :return: A list of IntegrationFinding objects
        :rtype: List[IntegrationFinding]
        """
        findings = []
        try:
            severity = self.finding_severity_map.get(vuln.severity.name, regscale_models.IssueSeverity.Low)
            cve_set = set(vuln.cve.split(",")) if vuln.cve else set()
            if severity in get_filtered_severities():
                if cve_set:
                    for cve in cve_set:
                        findings.append(
                            self._create_finding(vuln=vuln, cve=cve, integration_mapping=integration_mapping)
                        )
                else:
                    findings.append(self._create_finding(vuln=vuln, cve="", integration_mapping=integration_mapping))
        except (KeyError, TypeError, ValueError) as e:
            logger.error("Error parsing Tenable SC finding: %s", str(e), exc_info=True)

        return findings

    def _create_finding(
        self, vuln: TenableAsset, cve: str, integration_mapping: IntegrationOverride
    ) -> IntegrationFinding:
        """
        Helper method to create an IntegrationFinding object

        :param TenableAsset vuln: The Tenable SC finding
        :param str cve: The CVE identifier
        :param IntegrationOverride integration_mapping: The IntegrationMapping object
        :return: An IntegrationFinding object
        :rtype: IntegrationFinding
        """

        def getter(field_name: str) -> Optional[str]:
            """
            Helper method to get the field value from the integration mapping

            :param str field_name: The field name to get the value for
            :return: The field value
            :rtype: Optional[str]
            """
            if val := integration_mapping.load("tenable_sc", field_name):
                return getattr(vuln, val, None)
            return None

        validated_match = integration_mapping.field_map_validation(obj=vuln, model_type="asset")
        asset_identifier = validated_match or vuln.dnsName or vuln.dns or vuln.ip
        cvss_scores = self.get_cvss_scores(vuln)
        severity = self.finding_severity_map.get(vuln.severity.name, regscale_models.IssueSeverity.Low)

        installed_versions_str = ""
        fixed_versions_str = ""
        package_path_str = ""

        if "Installed package" in vuln.pluginText:
            installed_versions = re.findall(r"Installed package\s*:\s*(\S+)", vuln.pluginText)
            installed_versions_str = ", ".join(installed_versions)
        if "Fixed package" in vuln.pluginText:
            fixed_versions = re.findall(r"Fixed package\s*:\s*(\S+)", vuln.pluginText)
            fixed_versions_str = ", ".join(fixed_versions)
        if "Path" in vuln.pluginText:
            package_path = re.findall(r"Path\s*:\s*(\S+)", vuln.pluginText)
            package_path_str = ", ".join(package_path)
        if "Installed version" in vuln.pluginText:
            installed_versions = re.findall(r"Installed version\s*:\s*(.+)", vuln.pluginText)
            installed_versions_str = ", ".join(installed_versions)
        if "Fixed version" in vuln.pluginText:
            fixed_versions = re.findall(r"Fixed version\s*:\s*(.+)", vuln.pluginText)
            fixed_versions_str = ", ".join(fixed_versions)

        first_seen = epoch_to_datetime(vuln.firstSeen) if vuln.firstSeen else self.scan_date
        return IntegrationFinding(
            control_labels=[],  # Add an empty list for control_labels
            category="Tenable SC Vulnerability",  # Add a default category
            dns=vuln.dnsName,
            title=getter("title") or f"{cve}: {vuln.synopsis}" if cve else (vuln.synopsis or vuln.pluginName),
            description=getter("description") or (vuln.description or vuln.pluginInfo),
            severity=severity,
            status=regscale_models.IssueStatus.Open,  # Findings of > Low are considered as FAIL
            asset_identifier=asset_identifier,
            external_id=vuln.pluginID,  # Weakness Source Identifier
            first_seen=first_seen,
            last_seen=epoch_to_datetime(vuln.lastSeen),
            date_created=first_seen,
            date_last_updated=epoch_to_datetime(vuln.lastSeen),
            recommendation_for_mitigation=vuln.solution,
            cve=cve,
            cvss_v3_score=cvss_scores.get("cvss_v3_base_score", 0.0),
            cvss_score=cvss_scores.get("cvss_v3_base_score", 0.0),
            cvss_v3_vector=vuln.cvssV3Vector,
            cvss_v2_score=cvss_scores.get("cvss_v2_base_score", 0.0),
            cvss_v2_vector=vuln.cvssVector,
            vpr_score=float(vuln.vprScore) if vuln.vprScore else None,
            comments=vuln.cvssV3Vector,
            plugin_id=vuln.pluginID,
            plugin_name=vuln.pluginName,
            rule_id=vuln.pluginID,
            rule_version=vuln.pluginName,
            basis_for_adjustment="Tenable SC import",
            vulnerability_type="Tenable SC Vulnerability",
            vulnerable_asset=vuln.dnsName,
            build_version="",
            affected_os=vuln.operatingSystem,
            affected_packages=vuln.pluginName,
            package_path=package_path_str,
            installed_versions=installed_versions_str,
            fixed_versions=fixed_versions_str,
            fix_status="",
            scan_date=self.scan_date,
            due_date=issue_due_date(
                severity=severity, created_date=first_seen, title="tenable", config=self.app.config
            ),
        )

    def get_cvss_scores(self, vuln: TenableAsset) -> dict:
        """
        Returns the CVSS score for the finding

        :param TenableAsset vuln: The Tenable SC finding
        :return: The CVSS score
        :rtype: float
        """
        res = {}
        try:
            res["cvss_v3_base_score"] = float(vuln.cvssV3BaseScore) if vuln.cvssV3BaseScore else 0.0
            res["cvss_v2_base_score"] = float(vuln.baseScore) if vuln.baseScore else 0.0
        except (ValueError, TypeError):
            res["cvss_v3_base_score"] = 0.0
            res["cvss_v2_base_score"] = 0.0

        return res

    def to_integration_asset(self, asset: TenableAsset, **kwargs: dict) -> IntegrationAsset:
        """Converts a TenableAsset object to an IntegrationAsset object

        :param TenableAsset asset: The Tenable SC asset
        :param dict **kwargs: Additional keyword arguments
        :return: An IntegrationAsset object
        :rtype: IntegrationAsset
        """
        app = kwargs.get("app")
        config = app.config
        override = kwargs.get("override")

        validated_match = override.field_map_validation(obj=asset, model_type="asset")
        asset_identifier = validated_match or asset.dnsName or asset.dns or asset.ip
        name = asset.dnsName or asset.ip

        return IntegrationAsset(
            name=name,
            identifier=asset_identifier,
            ip_address=asset.ip,
            mac_address=asset.macAddress,
            asset_owner_id=config["userId"],
            status="Active (On Network)" if asset.family.type else "Off-Network",
            asset_type="Other",
            asset_category="Hardware",
            parent_id=self.plan_id,
            parent_module=(
                regscale_models.Component.get_module_string()
                if self.is_component
                else regscale_models.SecurityPlan.get_module_string()
            ),
            component_names=[self.component_title],
        )

    def is_empty(self, file_path: Path) -> bool:
        """
        Check if the file is empty.

        :param Path file_path: The path to the file
        :return: True if the file is empty, False otherwise
        :rtype: bool
        """
        try:
            return file_path.stat().st_size == 0
        except FileNotFoundError:
            return True

    def fetch_vulns_by_query_id(self, query_id: int) -> None:
        """
        Fetch vulnerabilities from Tenable SC by query ID and sync to RegScale

        :param int query_id: Tenable SC query ID to retrieve via API
        """
        # Ensure authentication
        self._ensure_authenticated()

        # Log query information
        logger.info(f"Fetching vulnerabilities from Tenable SC using query ID: {query_id}")
        logger.info(f"Using batch size of {self.batch_size} for processing")

        # Get vulnerability iterator from Tenable SC
        vulns = self.client.analysis.vulns(query_id=query_id)

        # Process in temporary directory to avoid disk space issues
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Saving Tenable SC data to disk: {temp_dir}")

            # Process data and get counts
            assets_count, findings_count = self._process_and_save_data(vulns, temp_dir)

            # Sync to RegScale
            self._sync_processed_data_to_regscale(temp_dir, assets_count, findings_count)

    def _ensure_authenticated(self) -> None:
        """
        Ensure client is authenticated to Tenable SC.

        :raises ValueError: If authentication fails
        """
        if not self.client:
            self.authenticate()

        if not self.client:
            raise ValueError("Failed to authenticate to Tenable SC")

    def _process_and_save_data(self, vulns: AnalysisResultsIterator, temp_dir: str) -> Tuple[int, int]:
        """
        Process vulnerability data and save to temporary directory.

        :param AnalysisResultsIterator vulns: Vulnerability iterator
        :param str temp_dir: Temporary directory path
        :return: Tuple of (assets_count, findings_count)
        :rtype: Tuple[int, int]
        """
        return self.consume_iterator_to_file(iterator=vulns, dir_path=Path(temp_dir))

    def _sync_processed_data_to_regscale(self, temp_dir: str, assets_count: int, findings_count: int) -> None:
        """
        Sync processed data to RegScale.

        :param str temp_dir: Temporary directory path
        :param int assets_count: Number of assets processed
        :param int findings_count: Number of findings processed
        :raises IndexError: If data processing fails
        """
        try:
            # Get iterables from disk
            iterables = self.tenable_dir_to_tuple_generator(Path(temp_dir))

            # Sync assets
            self.sync_assets(
                plan_id=self.plan_id,
                integration_assets=(asset for sublist in iterables[0] for asset in sublist),
                asset_count=assets_count,
                is_component=self.is_component,
            )

            # Sync findings
            self.sync_findings(
                plan_id=self.plan_id,
                integration_findings=(finding for sublist in iterables[1] for finding in sublist),
                finding_count=findings_count,
                is_component=self.is_component,
            )

            logger.info(f"Successfully synced {assets_count} assets and {findings_count} findings")
        except IndexError as ex:
            logger.error(f"Error processing Tenable SC data: {str(ex)}")
            raise

    def consume_iterator_to_file(self, iterator: AnalysisResultsIterator, dir_path: Path) -> Tuple[int, int]:
        """
        Consume an iterator and write the results to a file

        :param AnalysisResultsIterator iterator: Tenable SC iterator
        :param Path dir_path: The directory to save the pickled files
        :return: The total count of assets and findings processed
        :rtype: Tuple[int, int]
        """
        app = Application()
        logger.info("Consuming Tenable SC iterator...")
        override = IntegrationOverride(app)

        # Initialize counters and thread tracking
        counters = self._initialize_thread_safe_counters()
        process_queue = queue.Queue()
        futures_list = []

        # Process data in batches using threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures_list = self._process_iterator_in_batches(
                iterator=iterator,
                executor=executor,
                process_queue=process_queue,
                counters=counters,
                app=app,
                dir_path=dir_path,
                override=override,
            )

        # Collect results from all threads
        asset_count, finding_count = self._collect_thread_results(futures_list)

        if counters["total"].value == 0:
            logger.warning("No Tenable SC data found.")

        return asset_count, finding_count

    def _initialize_thread_safe_counters(self) -> dict:
        """
        Initialize thread-safe counters for processing.

        :return: Dictionary of counter objects
        :rtype: dict
        """
        return {"total": ThreadSafeCounter(), "page": ThreadSafeCounter(), "record": ThreadSafeCounter()}

    def _process_iterator_in_batches(
        self,
        iterator: AnalysisResultsIterator,
        executor: ThreadPoolExecutor,
        process_queue: queue.Queue,
        counters: dict,
        app: Application,
        dir_path: Path,
        override: IntegrationOverride,
    ) -> List:
        """
        Process an iterator in batches, submitting each batch to the executor.

        :param AnalysisResultsIterator iterator: The data iterator
        :param ThreadPoolExecutor executor: Thread pool executor
        :param queue.Queue process_queue: Queue for items to process
        :param dict counters: Thread-safe counters
        :param Application app: Application instance
        :param Path dir_path: Directory to save files
        :param IntegrationOverride override: Integration override
        :return: List of futures
        :rtype: List
        """
        futures = []

        for item in iterator:
            # Add item to queue and update counters
            counters["total"].increment()
            process_queue.put(item)
            counters["record"].increment()

            # When we've accumulated a full page of data, process it
            if counters["record"].value == len(iterator.page):
                counters["page"].increment()

                # Extract items from queue
                items = self._extract_items_from_queue(process_queue, len(iterator.page))

                # Submit batch for processing
                futures.append(
                    executor.submit(
                        self.process_sc_chunk,
                        app=app,
                        vulns=items,
                        page=counters["page"].value,
                        dir_path=dir_path,
                        override=override,
                    )
                )

                # Reset record counter for next batch
                counters["record"].set(0)

        return futures

    def _extract_items_from_queue(self, queue_obj: queue.Queue, max_items: int) -> List[Any]:
        """
        Extract up to max_items from a queue.

        :param queue.Queue queue_obj: Queue to extract from
        :param int max_items: Maximum number of items to extract
        :return: List of extracted items
        :rtype: List[Any]
        """
        items = []

        for _ in range(max_items):
            if not queue_obj.empty():
                items.append(queue_obj.get())
            else:
                break

        return items

    def _collect_thread_results(self, futures: List) -> Tuple[int, int]:
        """
        Collect results from completed futures.

        :param List futures: List of futures to collect from
        :return: Counts of assets and findings
        :rtype: Tuple[int, int]
        """
        # Wait for all threads to complete
        wait(futures)

        # Collect results
        asset_count = 0
        finding_count = 0

        for future in futures:
            findings, assets = future.result()
            finding_count += findings
            asset_count += assets

        return asset_count, finding_count

    def process_sc_chunk(self, **kwargs) -> Tuple[int, int]:
        """
        Process Tenable SC chunk

        :param kwargs: Keyword arguments
        :return: Tuple of findings and assets
        :rtype: Tuple[int, int]
        """
        integration_mapping = kwargs.get("override")
        vulns = kwargs.get("vulns")
        dir_path = kwargs.get("dir_path")
        page_num = kwargs.get("page")

        # If no vulnerabilities, return early
        if not vulns:
            return (0, 0)

        # Set up file handler
        generated_file_name = f"tenable_scan_page_{page_num}.pkl"
        pickled_file_handler = PickleFileHandler(str(dir_path / generated_file_name))

        # Process vulnerabilities into findings and assets
        findings, assets = self._process_vulnerability_data(vulns, integration_mapping, kwargs)

        # Write results to file
        pickled_file_handler.write({"assets": assets, "findings": findings})

        # Log progress
        thread = current_thread()
        logger.info(
            "Submitting %i findings and %i assets to the CLI Job Queue from Tenable SC Page %i...",
            len(findings),
            len(assets),
            page_num,
        )
        logger.debug(f"Completed thread: name={thread.name}, ident={get_ident()}, id={get_native_id()}")

        return (len(findings), len(assets))

    def _process_vulnerability_data(
        self, vulns: List[dict], integration_mapping: IntegrationOverride, kwargs: dict
    ) -> Tuple[List, List]:
        """
        Process vulnerability data into findings and assets.

        :param List[dict] vulns: List of vulnerability dictionaries
        :param IntegrationOverride integration_mapping: Integration mapping
        :param dict kwargs: Additional parameters
        :return: Tuple of (findings, assets)
        :rtype: Tuple[List, List]
        """
        # Convert to TenableAsset objects
        tenable_vulns = [TenableAsset(**vuln) for vuln in vulns]

        # Ensure DNS name is set
        for vuln in tenable_vulns:
            if not vuln.dnsName:
                vuln.dnsName = vuln.ip

        # Generate findings and assets
        findings = []
        assets = set()  # Use a set to track unique asset names
        asset_objects = []

        for vuln in tenable_vulns:
            # Add findings for this vulnerability
            findings.extend(self.parse_findings(vuln=vuln, integration_mapping=integration_mapping))

            # Add asset if not already processed
            if vuln.dnsName not in assets:
                assets.add(vuln.dnsName)
                asset_objects.append(self.to_integration_asset(vuln, **kwargs))

        return findings, asset_objects

    def tenable_dir_to_tuple_generator(self, dir_path: Path) -> Tuple[Any, Any]:
        """
        Generate a tuple of chained generators for Tenable directories.

        :param Path dir_path: Directory path containing pickled files
        :return: Tuple of asset and finding generators
        :rtype: Tuple[Any, Any]
        """
        from itertools import chain

        assets_gen = chain.from_iterable(
            (dat["assets"] for dat in PickleFileHandler(file).read()) for file in dir_path.iterdir()
        )
        findings_gen = chain.from_iterable(
            (dat["findings"] for dat in PickleFileHandler(file).read()) for file in dir_path.iterdir()
        )

        return assets_gen, findings_gen

    def fetch_vulns_query(self, query_id: int) -> None:
        """
        Class method to fetch and sync vulnerabilities from Tenable SC by query ID

        :param int query_id: Tenable SC query ID
        :raises ValueError: If authentication to Tenable SC fails
        :raises Exception: If an error occurs during the fetch process
        """
        logger.info(f"Fetching vulnerabilities from Tenable SC for query ID {query_id} and plan ID {self.plan_id}")
        self.fetch_vulns_by_query_id(query_id=query_id)
