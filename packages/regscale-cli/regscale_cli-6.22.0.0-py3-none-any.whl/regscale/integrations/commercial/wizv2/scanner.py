"""Module for Wiz vulnerability scanning integration."""

import datetime
import json
import logging
import os
import re
from collections.abc import Iterator
from typing import Any, Dict, List, Optional, Tuple, Union

from regscale.core.app.utils.app_utils import check_file_path, error_and_exit, get_current_datetime
from regscale.core.utils import get_base_protocol_from_port
from regscale.core.utils.date import format_to_regscale_iso
from regscale.integrations.commercial.wizv2.async_client import run_async_queries
from regscale.integrations.commercial.wizv2.constants import (
    END_OF_LIFE_FILE_PATH,
    EXTERNAL_ATTACK_SURFACE_FILE_PATH,
    INVENTORY_FILE_PATH,
    INVENTORY_QUERY,
    NETWORK_EXPOSURE_FILE_PATH,
    SECRET_FINDINGS_FILE_PATH,
    WizVulnerabilityType,
    get_wiz_vulnerability_queries,
)
from regscale.integrations.commercial.wizv2.parsers import (
    collect_components_to_create,
    fetch_wiz_data,
    get_disk_storage,
    get_latest_version,
    get_network_info,
    get_product_ids,
    get_software_name_from_cpe,
    handle_container_image_version,
    handle_provider,
    handle_software_version,
    pull_resource_info_from_props,
)
from regscale.integrations.commercial.wizv2.utils import (
    create_asset_type,
    get_notes_from_wiz_props,
    handle_management_type,
    map_category,
)
from regscale.integrations.commercial.wizv2.variables import WizVariables
from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import IssueStatus, regscale_models
from regscale.models.regscale_models.compliance_settings import ComplianceSettings

logger = logging.getLogger("regscale")


class WizVulnerabilityIntegration(ScannerIntegration):
    """Integration class for Wiz vulnerability scanning."""

    title = "Wiz"
    asset_identifier_field = "wizId"
    issue_identifier_field = "wizId"
    finding_severity_map = {
        "Critical": regscale_models.IssueSeverity.Critical,
        "High": regscale_models.IssueSeverity.High,
        "Medium": regscale_models.IssueSeverity.Moderate,
        "Low": regscale_models.IssueSeverity.Low,
    }
    asset_lookup = "vulnerableAsset"
    wiz_token = None
    _compliance_settings = None

    @staticmethod
    def get_variables() -> Dict[str, Any]:
        """
        Returns default variables for first and filterBy for Wiz GraphQL queries.

        :return: Default variables for Wiz queries
        :rtype: Dict[str, Any]
        """
        return {
            "first": 100,
            "filterBy": {},
        }

    def authenticate(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:
        """
        Authenticates to Wiz using the client ID and client secret

        :param Optional[str] client_id: Wiz client ID
        :param Optional[str] client_secret: WiZ client secret
        :rtype: None
        """
        client_id = client_id or WizVariables.wizClientId
        client_secret = client_secret or WizVariables.wizClientSecret
        logger.info("Authenticating to Wiz...")
        self.wiz_token = wiz_authenticate(client_id, client_secret)

    def get_query_types(self, project_id: str) -> List[Dict[str, Any]]:
        """Get the query types for vulnerability scanning.

        :param str project_id: The project ID to get queries for
        :return: List of query types
        :rtype: List[Dict[str, Any]]
        """
        return get_wiz_vulnerability_queries(project_id=project_id)

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches Wiz findings using async GraphQL queries for improved performance

        This method automatically uses async concurrent queries by default for better performance,
        with fallback to synchronous queries if async fails.

        :yield: IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        # Check if async processing should be disabled (for debugging or compatibility)
        use_async = kwargs.get("use_async", True)  # Default to async

        if use_async:
            try:
                # Use async concurrent queries for better performance
                yield from self.fetch_findings_async(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Async query failed, falling back to sync: {e!s}")
                # Fallback to synchronous method
                yield from self.fetch_findings_sync(**kwargs)
        else:
            # Use synchronous method if explicitly requested
            yield from self.fetch_findings_sync(**kwargs)

    def _validate_project_id(self, project_id: Optional[str]) -> str:
        """
        Validate and format the Wiz project ID.

        :param Optional[str] project_id: Project ID to validate
        :return: Validated project ID
        :rtype: str
        :raises ValueError: If project ID is invalid or missing
        """
        if not project_id:
            error_and_exit("Wiz project ID is required")

        # Clean and validate project ID format
        project_id = project_id.strip()
        if len(project_id) != 36:
            error_and_exit(
                f"Invalid Wiz project ID format. Expected 36 characters (UUID), "
                f"got {len(project_id)} characters: '{project_id}'"
            )

        # UUID format validation
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if not re.match(uuid_pattern, project_id, re.IGNORECASE):
            error_and_exit(f"Invalid Wiz project ID format. Must be a valid UUID: '{project_id}'")

        return project_id

    def _setup_authentication_headers(self) -> Dict[str, str]:
        """
        Setup authentication headers for API requests.

        :return: Headers dictionary with authentication
        :rtype: Dict[str, str]
        """
        if not self.wiz_token:
            self.authenticate()

        # Debug authentication
        logger.debug(f"Wiz token exists: {bool(self.wiz_token)}")
        logger.debug(f"Wiz token length: {len(self.wiz_token) if self.wiz_token else 0}")
        if self.wiz_token:
            logger.debug(f"Wiz token starts with: {self.wiz_token[:20]}...")

        headers = {"Authorization": f"Bearer {self.wiz_token}", "Content-Type": "application/json"}
        logger.debug(f"Headers for async request: {headers}")
        return headers

    def _execute_concurrent_queries(
        self, query_configs: List[Dict[str, Any]], headers: Dict[str, str]
    ) -> List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]:
        """
        Execute GraphQL queries concurrently or load cached data.

        :param List[Dict[str, Any]] query_configs: Query configurations
        :param Dict[str, str] headers: Request headers
        :return: Query results
        :rtype: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]
        """
        should_fetch_fresh = self._should_fetch_fresh_data(query_configs)

        if should_fetch_fresh:
            logger.info(f"Starting {len(query_configs)} concurrent queries to Wiz API...")
            return run_async_queries(
                endpoint=WizVariables.wizUrl,
                headers=headers,
                query_configs=query_configs,
                progress_tracker=self.finding_progress,
                max_concurrent=5,
            )
        return self._load_cached_data_with_progress(query_configs)

    def _process_query_results(
        self,
        results: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]],
        query_configs: List[Dict[str, Any]],
        project_id: str,
        should_fetch_fresh: bool,
    ) -> Iterator[IntegrationFinding]:
        """
        Process query results and yield findings.

        :param results: Query results from concurrent execution
        :param query_configs: Original query configurations
        :param project_id: Project ID for filtering
        :param should_fetch_fresh: Whether fresh data was fetched
        :yield: IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        parse_task = self.finding_progress.add_task("[magenta]Processing fetched findings...", total=len(results))

        for query_type_str, nodes, error in results:
            if error:
                logger.error(f"Error fetching {query_type_str}: {error}")
                self.finding_progress.advance(parse_task, 1)
                continue

            # Find corresponding vulnerability type and config
            vulnerability_type, config = self._find_vulnerability_config(query_type_str, query_configs)
            if not vulnerability_type or not config:
                logger.warning(f"Could not find vulnerability type for {query_type_str}")
                self.finding_progress.advance(parse_task, 1)
                continue

            # Save fetched data to cache if fresh data was fetched
            if should_fetch_fresh and nodes:
                self._save_data_to_cache(nodes, config.get("file_path"))

            # Apply project filtering for certain vulnerability types
            nodes = self._apply_project_filtering(nodes, vulnerability_type, project_id, query_type_str)

            logger.info(f"Processing {len(nodes)} {query_type_str} findings...")
            yield from self.parse_findings(nodes, vulnerability_type)
            self.finding_progress.advance(parse_task, 1)

        self.finding_progress.update(
            parse_task, description=f"[green]✓ Processed all findings ({self.num_findings_to_process} total)"
        )

    def _find_vulnerability_config(
        self, query_type_str: str, query_configs: List[Dict[str, Any]]
    ) -> Tuple[Optional[WizVulnerabilityType], Optional[Dict[str, Any]]]:
        """
        Find vulnerability type and config for a query type string.

        :param str query_type_str: Query type string to find
        :param List[Dict[str, Any]] query_configs: List of query configurations
        :return: Tuple of vulnerability type and config, or (None, None) if not found
        :rtype: Tuple[Optional[WizVulnerabilityType], Optional[Dict[str, Any]]]
        """
        for query_config in query_configs:
            if query_config["type"].value == query_type_str:
                return query_config["type"], query_config
        return None, None

    def _apply_project_filtering(
        self,
        nodes: List[Dict[str, Any]],
        vulnerability_type: WizVulnerabilityType,
        project_id: str,
        query_type_str: str,
    ) -> List[Dict[str, Any]]:
        """
        Apply project filtering for vulnerability types that need it.

        :param List[Dict[str, Any]] nodes: Nodes to filter
        :param WizVulnerabilityType vulnerability_type: Vulnerability type
        :param str project_id: Project ID to filter by
        :param str query_type_str: Query type string for logging
        :return: Filtered nodes
        :rtype: List[Dict[str, Any]]
        """
        filter_required_types = {
            WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING,
            WizVulnerabilityType.NETWORK_EXPOSURE_FINDING,
            WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE,
        }

        if vulnerability_type in filter_required_types:
            original_count = len(nodes)
            nodes = self._filter_findings_by_project(nodes, project_id)
            if len(nodes) != original_count:
                logger.info(f"Filtered {query_type_str}: {len(nodes)}/{original_count} match project")

        return nodes

    def fetch_findings_async(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches Wiz findings using async GraphQL queries for improved performance

        This method runs multiple GraphQL queries concurrently, significantly reducing
        the total time needed to fetch all finding types from Wiz.

        :yield: IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        try:
            # Step 1: Validate project ID
            project_id = self._validate_project_id(kwargs.get("wiz_project_id"))

            # Step 2: Initialize progress tracking
            logger.info("Fetching Wiz findings using async concurrent queries...")
            self.num_findings_to_process = 0
            query_configs = self.get_query_types(project_id=project_id)

            main_task = self.finding_progress.add_task(
                "[cyan]Running concurrent GraphQL queries...", total=len(query_configs)
            )

            # Step 3: Setup authentication
            headers = self._setup_authentication_headers()

            # Step 4: Execute queries
            results = self._execute_concurrent_queries(query_configs, headers)
            should_fetch_fresh = self._should_fetch_fresh_data(query_configs)

            # Step 5: Update main progress
            self.finding_progress.update(
                main_task,
                description="[green]✓ Completed all concurrent queries",
                completed=len(query_configs),
                total=len(query_configs),
            )

            # Step 6: Process results
            yield from self._process_query_results(results, query_configs, project_id, should_fetch_fresh)

            # Step 7: Complete main task
            self.finding_progress.advance(main_task, len(query_configs))

        except Exception as e:
            logger.error(f"Error in async findings fetch: {e!s}", exc_info=True)
            if "main_task" in locals():
                self.finding_progress.update(
                    main_task, description=f"[red]✗ Error in concurrent queries: {str(e)[:50]}..."
                )
            # Fallback to synchronous method
            logger.info("Falling back to synchronous query method...")
            yield from self.fetch_findings_sync(**kwargs)

        logger.info(
            "Finished async fetching Wiz findings. Total findings to process: %d", self.num_findings_to_process or 0
        )

    def _should_fetch_fresh_data(self, query_configs: List[Dict[str, Any]]) -> bool:
        """
        Check if we should fetch fresh data or use cached data.

        :param List[Dict[str, Any]] query_configs: Query configurations
        :return: True if fresh data should be fetched
        :rtype: bool
        """
        import datetime
        import os

        fetch_interval = datetime.timedelta(hours=WizVariables.wizFullPullLimitHours or 8)
        current_time = datetime.datetime.now()

        # Check if any file is missing or older than the fetch interval
        for config in query_configs:
            file_path = config.get("file_path")
            if not file_path or not os.path.exists(file_path):
                return True

            file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if current_time - file_mod_time >= fetch_interval:
                return True

        return False

    def _load_cached_data_with_progress(
        self, query_configs: List[Dict[str, Any]]
    ) -> List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]:
        """
        Load cached data with progress tracking.

        :param List[Dict[str, Any]] query_configs: Query configurations
        :return: Results in the same format as async queries
        :rtype: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]
        """

        results = []
        cache_task = self.finding_progress.add_task("[green]Loading cached Wiz data...", total=len(query_configs))

        for config in query_configs:
            query_type = config["type"].value
            file_path = config.get("file_path")

            try:
                if file_path and os.path.exists(file_path):
                    with open(file_path, encoding="utf-8") as file:
                        nodes = json.load(file)

                    logger.info(f"Loaded {len(nodes)} cached {query_type} findings from {file_path}")
                    results.append((query_type, nodes, None))
                else:
                    logger.warning(f"No cached data found for {query_type}")
                    results.append((query_type, [], None))

            except Exception as e:
                logger.error(f"Error loading cached data for {query_type}: {e}")
                results.append((query_type, [], e))

            self.finding_progress.advance(cache_task, 1)

        self.finding_progress.update(
            cache_task, description=f"[green]✓ Loaded cached data for {len(query_configs)} query types"
        )

        return results

    def _save_data_to_cache(self, nodes: List[Dict[str, Any]], file_path: Optional[str]) -> None:
        """
        Save fetched data to cache file.

        :param List[Dict[str, Any]] nodes: Data to save
        :param Optional[str] file_path: File path to save to
        :rtype: None
        """
        if not file_path:
            return

        try:
            from regscale.core.app.utils.app_utils import check_file_path

            # Ensure directory exists
            check_file_path(os.path.dirname(file_path))

            # Save data to file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(nodes, file)

            logger.debug(f"Saved {len(nodes)} nodes to cache file: {file_path}")

        except Exception as e:
            logger.warning(f"Failed to save data to cache file {file_path}: {e}")

    def fetch_findings_sync(self, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Original synchronous method for fetching findings (renamed for fallback)
        :param List[Dict[str, Any]] kwargs: Query configurations
        :return: Results in the same format as async queries
        :rtype: Iterator[IntegrationFinding]
        """
        # Use shared validation logic
        project_id = self._validate_project_id(kwargs.get("wiz_project_id"))

        logger.info("Fetching Wiz findings using synchronous queries...")
        self.num_findings_to_process = 0
        query_types = self.get_query_types(project_id=project_id)

        # Create detailed progress tracking for each query type
        main_task = self.finding_progress.add_task(
            "[cyan]Fetching Wiz findings across all query types...", total=len(query_types)
        )

        for i, wiz_vulnerability_type in enumerate(query_types, 1):
            vulnerability_name = self._get_friendly_vulnerability_name(wiz_vulnerability_type["type"])

            # Update main progress with current query type
            self.finding_progress.update(
                main_task, description=f"[cyan]Step {i}/{len(query_types)}: Fetching {vulnerability_name}..."
            )

            # Create subtask for this specific query type
            query_task = self.finding_progress.add_task(
                f"[yellow]Querying Wiz API for {vulnerability_name}...", total=None  # Indeterminate while fetching
            )

            # Use the variables from the query type configuration
            variables = wiz_vulnerability_type.get("variables", self.get_variables())

            nodes = self.fetch_wiz_data_if_needed(
                query=wiz_vulnerability_type["query"],
                variables=variables,
                topic_key=wiz_vulnerability_type["topic_key"],
                file_path=wiz_vulnerability_type["file_path"],
            )

            # Update query task to show data fetched
            self.finding_progress.update(
                query_task, description=f"[green]✓ Fetched {len(nodes)} {vulnerability_name} from Wiz API"
            )

            # Filter findings by project for queries that don't support API-level project filtering
            if wiz_vulnerability_type["type"] in [
                WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING,
                WizVulnerabilityType.NETWORK_EXPOSURE_FINDING,
                WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE,
            ]:
                filter_task = self.finding_progress.add_task(
                    f"[blue]Filtering {vulnerability_name} by project...", total=len(nodes)
                )
                nodes = self._filter_findings_by_project_with_progress(nodes, project_id, filter_task)
                self.finding_progress.update(
                    filter_task, description=f"[green]✓ Filtered to {len(nodes)} {vulnerability_name} for project"
                )

            # Create parsing task
            if nodes:
                parse_task = self.finding_progress.add_task(
                    f"[magenta]Parsing {len(nodes)} {vulnerability_name}...", total=len(nodes)
                )

                yield from self.parse_findings_with_progress(nodes, wiz_vulnerability_type["type"], parse_task)

                self.finding_progress.update(
                    parse_task, description=f"[green]✓ Parsed {len(nodes)} {vulnerability_name} successfully"
                )

            # Mark query complete and advance main progress
            self.finding_progress.update(query_task, completed=1, total=1)
            self.finding_progress.advance(main_task, 1)

        # Update main task completion
        self.finding_progress.update(
            main_task,
            description=f"[green]✓ Completed fetching all Wiz findings ({self.num_findings_to_process or 0} total)",
        )

        logger.info(
            "Finished synchronous fetching Wiz findings. Total findings to process: %d",
            self.num_findings_to_process or 0,
        )

    def _get_friendly_vulnerability_name(self, vulnerability_type: WizVulnerabilityType) -> str:
        """
        Convert vulnerability type enum to user-friendly name for progress display.

        :param WizVulnerabilityType vulnerability_type: The vulnerability type enum
        :return: User-friendly name
        :rtype: str
        """
        friendly_names = {
            WizVulnerabilityType.VULNERABILITY: "Vulnerabilities",
            WizVulnerabilityType.CONFIGURATION: "Configuration Findings",
            WizVulnerabilityType.HOST_FINDING: "Host Findings",
            WizVulnerabilityType.DATA_FINDING: "Data Findings",
            WizVulnerabilityType.SECRET_FINDING: "Secret Findings",
            WizVulnerabilityType.NETWORK_EXPOSURE_FINDING: "Network Exposures",
            WizVulnerabilityType.END_OF_LIFE_FINDING: "End-of-Life Findings",
            WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE: "External Attack Surface",
            WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING: "Excessive Access Findings",
            WizVulnerabilityType.ISSUE: "Issues",
        }
        return friendly_names.get(vulnerability_type, vulnerability_type.value.replace("_", " ").title())

    def parse_findings_with_progress(
        self, nodes: List[Dict[str, Any]], vulnerability_type: WizVulnerabilityType, task_id: Optional[Any] = None
    ) -> Iterator[IntegrationFinding]:
        """
        Parse findings with progress tracking.

        :param List[Dict[str, Any]] nodes: List of Wiz finding nodes
        :param WizVulnerabilityType vulnerability_type: The type of vulnerability
        :param Optional[Any] task_id: Progress task ID for tracking
        :yield: IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        findings_count = 0
        total_nodes = len(nodes)

        for i, node in enumerate(nodes, 1):
            if finding := self.parse_finding(node, vulnerability_type):
                findings_count += 1
                yield finding

            # Update progress if task_id provided
            if task_id is not None:
                self.finding_progress.advance(task_id, 1)

        # Log parsing results for this type
        if findings_count != total_nodes:
            logger.info(
                "Parsed %d/%d %s findings successfully (%d failed/skipped)",
                findings_count,
                total_nodes,
                vulnerability_type.value,
                total_nodes - findings_count,
            )

        # Update the total count once at the end to prevent flashing
        self.num_findings_to_process = (self.num_findings_to_process or 0) + findings_count

    def _filter_findings_by_project_with_progress(
        self, nodes: List[Dict[str, Any]], project_id: str, task_id: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter findings by project ID with progress tracking.

        :param List[Dict[str, Any]] nodes: List of finding nodes
        :param str project_id: Project ID to filter by
        :param Optional[Any] task_id: Progress task ID for tracking
        :return: Filtered list of nodes
        :rtype: List[Dict[str, Any]]
        """
        filtered_nodes = []
        original_count = len(nodes)

        for i, node in enumerate(nodes, 1):
            # Check if any of the node's projects match the target project ID
            projects = node.get("projects", [])
            if any(project.get("id") == project_id for project in projects):
                filtered_nodes.append(node)

            # Update progress if task_id provided
            if task_id is not None:
                self.finding_progress.advance(task_id, 1)

        filtered_count = len(filtered_nodes)
        if filtered_count != original_count:
            logger.info(
                "Filtered findings by project: %d/%d findings match project %s",
                filtered_count,
                original_count,
                project_id,
            )

        return filtered_nodes

    def _filter_findings_by_project(self, nodes: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
        """
        Filter findings by project ID for queries that don't support API-level project filtering.

        :param List[Dict[str, Any]] nodes: List of finding nodes
        :param str project_id: Project ID to filter by
        :return: Filtered list of nodes
        :rtype: List[Dict[str, Any]]
        """
        filtered_nodes = []
        original_count = len(nodes)

        for node in nodes:
            # Check if any of the node's projects match the target project ID
            projects = node.get("projects", [])
            if any(project.get("id") == project_id for project in projects):
                filtered_nodes.append(node)

        filtered_count = len(filtered_nodes)
        if filtered_count != original_count:
            logger.info(
                "Filtered findings by project: %d/%d findings match project %s",
                filtered_count,
                original_count,
                project_id,
            )

        return filtered_nodes

    def parse_findings(
        self, nodes: List[Dict[str, Any]], vulnerability_type: WizVulnerabilityType
    ) -> Iterator[IntegrationFinding]:
        """
        Parses a list of Wiz finding nodes into IntegrationFinding objects.

        This is a compatibility wrapper that calls the progress-aware version.

        :param List[Dict[str, Any]] nodes: List of Wiz finding nodes
        :param WizVulnerabilityType vulnerability_type: The type of vulnerability
        :yield: IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        # Delegate to the progress-aware version without progress tracking
        yield from self.parse_findings_with_progress(nodes, vulnerability_type, task_id=None)

    @classmethod
    def get_issue_severity(cls, severity: str) -> regscale_models.IssueSeverity:
        """
        Get the issue severity from the Wiz severity

        :param str severity: The severity of the vulnerability
        :return: The issue severity
        :rtype: regscale_models.IssueSeverity
        """
        return cls.finding_severity_map.get(severity.capitalize(), regscale_models.IssueSeverity.Low)

    def process_comments(self, comments_dict: Dict) -> Optional[str]:
        """
        Processes comments from Wiz findings to match RegScale's comment format.

        :param Dict comments_dict: The comments from the Wiz finding
        :return: If available the Processed comments in RegScale format
        :rtype:  Optional[str]
        """
        result = None

        if comments := comments_dict.get("comments", {}).get("edges", []):
            formatted_comments = [
                f"{edge.get('node', {}).get('author', {}).get('name', 'Unknown')}: {edge.get('node', {}).get('body', 'No comment')}"
                for edge in comments
            ]
            # Join with newlines
            result = "\n".join(formatted_comments)
        return result

    def get_asset_id_from_node(self, node: Dict[str, Any], vulnerability_type: WizVulnerabilityType) -> Optional[str]:
        """
        Get the asset ID from a node based on the vulnerability type.

        :param Dict[str, Any] node: The Wiz finding node
        :param WizVulnerabilityType vulnerability_type: The type of vulnerability
        :return: The asset ID or None if not found
        :rtype: Optional[str]
        """
        # Define asset lookup patterns for different vulnerability types
        asset_lookup_patterns = {
            # WizVulnerabilityType.VULNERABILITY: "vulnerableAsset",
            # WizVulnerabilityType.CONFIGURATION: "resource",
            # WizVulnerabilityType.HOST_FINDING: "resource",
            # WizVulnerabilityType.DATA_FINDING: "resource",
            WizVulnerabilityType.SECRET_FINDING: "resource",
            WizVulnerabilityType.NETWORK_EXPOSURE_FINDING: "exposedEntity",
            WizVulnerabilityType.END_OF_LIFE_FINDING: "vulnerableAsset",
            WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE: "exposedEntity",
            WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING: "scope",
            WizVulnerabilityType.ISSUE: "entitySnapshot",
        }

        asset_lookup_key = asset_lookup_patterns.get(vulnerability_type, "vulnerableAsset")

        if asset_lookup_key == "scope":
            # Handle special case for excessive access findings where ID is nested
            scope = node.get("scope", {})
            graph_entity = scope.get("graphEntity", {})
            return graph_entity.get("id")

        # Standard case - direct id access
        asset_container = node.get(asset_lookup_key, {})
        return asset_container.get("id")

    def parse_finding(
        self, node: Dict[str, Any], vulnerability_type: WizVulnerabilityType
    ) -> Optional[IntegrationFinding]:
        """
        Parses a Wiz finding node into an IntegrationFinding object

        :param Dict[str, Any] node: The Wiz finding node to parse
        :param WizVulnerabilityType vulnerability_type: The type of vulnerability
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        try:
            # Route to specific parsing method based on vulnerability type
            if vulnerability_type == WizVulnerabilityType.SECRET_FINDING:
                return self._parse_secret_finding(node)
            if vulnerability_type == WizVulnerabilityType.NETWORK_EXPOSURE_FINDING:
                return self._parse_network_exposure_finding(node)
            if vulnerability_type == WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE:
                return self._parse_external_attack_surface_finding(node)
            if vulnerability_type == WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING:
                return self._parse_excessive_access_finding(node)
            if vulnerability_type == WizVulnerabilityType.END_OF_LIFE_FINDING:
                return self._parse_end_of_life_finding(node)
            # Fallback to generic parsing for any other types
            return self._parse_generic_finding(node, vulnerability_type)
        except (KeyError, TypeError, ValueError) as e:
            logger.error("Error parsing Wiz finding: %s", str(e), exc_info=True)
            return None

    def _parse_secret_finding(self, node: Dict[str, Any]) -> Optional[IntegrationFinding]:
        """
        Parse secret finding from Wiz.

        :param Dict[str, Any] node: The Wiz finding node to parse
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        asset_id = node.get("resource", {}).get("id")
        if not asset_id:
            return None

        first_seen = node.get("firstSeenAt") or get_current_datetime()
        first_seen = format_to_regscale_iso(first_seen)
        severity = self.get_issue_severity(node.get("severity", "Low"))
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        # Create meaningful title for secret findings
        secret_type = node.get("type", "Unknown Secret")
        resource_name = node.get("resource", {}).get("name", "Unknown Resource")
        title = f"Secret Detected: {secret_type} in {resource_name}"

        # Build description with secret details
        description_parts = [
            f"Secret type: {secret_type}",
            f"Confidence: {node.get('confidence', 'Unknown')}",
            f"Encrypted: {node.get('isEncrypted', False)}",
            f"Managed: {node.get('isManaged', False)}",
        ]

        if rule := node.get("rule", {}):
            description_parts.append(f"Detection rule: {rule.get('name', 'Unknown')}")

        description = "\n".join(description_parts)

        return IntegrationFinding(
            control_labels=[],
            category="Wiz Secret Detection",
            title=title,
            description=description,
            severity=severity,
            status=self.map_status_to_issue_status(node.get("status", "Open")),
            asset_identifier=asset_id,
            external_id=node.get("id"),
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=format_to_regscale_iso(node.get("lastSeenAt") or get_current_datetime()),
            remediation=f"Remove or properly secure the {secret_type} secret found in {resource_name}",
            plugin_name=f"Wiz Secret Detection - {secret_type}",
            vulnerability_type=WizVulnerabilityType.SECRET_FINDING.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="Secret Scanning",
        )

    def _parse_network_exposure_finding(self, node: Dict[str, Any]) -> Optional[IntegrationFinding]:
        """Parse network exposure finding from Wiz.

        :param Dict[str, Any] node: The Wiz finding node to parse
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        asset_id = node.get("exposedEntity", {}).get("id")
        if not asset_id:
            return None

        first_seen = node.get("firstSeenAt") or get_current_datetime()
        first_seen = format_to_regscale_iso(first_seen)

        # Network exposures typically don't have explicit severity, assume Medium
        severity = regscale_models.IssueSeverity.Moderate
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        # Create meaningful title for network exposure
        exposed_entity = node.get("exposedEntity", {})
        entity_name = exposed_entity.get("name", "Unknown Entity")
        port_range = node.get("portRange", "Unknown Port")
        title = f"Network Exposure: {entity_name} on {port_range}"

        # Build description with network details
        description_parts = [
            f"Exposed entity: {entity_name} ({exposed_entity.get('type', 'Unknown Type')})",
            f"Port range: {port_range}",
            f"Source IP range: {node.get('sourceIpRange', 'Unknown')}",
            f"Destination IP range: {node.get('destinationIpRange', 'Unknown')}",
        ]

        if protocols := node.get("appProtocols"):
            description_parts.append(f"Application protocols: {', '.join(protocols)}")
        if net_protocols := node.get("networkProtocols"):
            description_parts.append(f"Network protocols: {', '.join(net_protocols)}")

        description = "\n".join(description_parts)

        return IntegrationFinding(
            control_labels=[],
            category="Wiz Network Exposure",
            title=title,
            description=description,
            severity=severity,
            status=IssueStatus.Open,
            asset_identifier=asset_id,
            external_id=node.get("id"),
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=first_seen,  # Network exposures may not have lastSeen
            remediation=f"Review and restrict network access to {entity_name} on {port_range}",
            plugin_name=f"Wiz Network Exposure - {port_range}",
            vulnerability_type=WizVulnerabilityType.NETWORK_EXPOSURE_FINDING.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="Network Security Assessment",
        )

    def _parse_external_attack_surface_finding(self, node: Dict[str, Any]) -> Optional[IntegrationFinding]:
        """Parse external attack surface finding from Wiz.

        :param Dict[str, Any] node: The Wiz finding node to parse
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        asset_id = node.get("exposedEntity", {}).get("id")
        if not asset_id:
            return None

        first_seen = node.get("firstSeenAt") or get_current_datetime()
        first_seen = format_to_regscale_iso(first_seen)

        # External attack surface findings are typically high severity
        severity = regscale_models.IssueSeverity.High
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        # Create meaningful title for external attack surface
        exposed_entity = node.get("exposedEntity", {})
        entity_name = exposed_entity.get("name", "Unknown Entity")
        port_range = node.get("portRange", "Unknown Port")
        title = f"External Attack Surface: {entity_name} exposed on {port_range}"

        # Build description with attack surface details
        description_parts = [
            f"Externally exposed entity: {entity_name} ({exposed_entity.get('type', 'Unknown Type')})",
            f"Exposed port range: {port_range}",
            f"Source IP range: {node.get('sourceIpRange', 'Public Internet')}",
        ]

        if protocols := node.get("appProtocols"):
            description_parts.append(f"Application protocols: {', '.join(protocols)}")
        if endpoints := node.get("applicationEndpoints"):
            endpoint_names = [ep.get("name", "Unknown") for ep in endpoints[:3]]  # Limit to first 3
            description_parts.append(f"Application endpoints: {', '.join(endpoint_names)}")

        description = "\n".join(description_parts)

        return IntegrationFinding(
            control_labels=[],
            category="Wiz External Attack Surface",
            title=title,
            description=description,
            severity=severity,
            status=IssueStatus.Open,
            asset_identifier=asset_id,
            external_id=node.get("id"),
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=first_seen,
            remediation=f"Review external exposure of {entity_name} and implement proper access controls",
            plugin_name=f"Wiz External Attack Surface - {port_range}",
            vulnerability_type=WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="External Attack Surface Assessment",
        )

    def _parse_excessive_access_finding(self, node: Dict[str, Any]) -> Optional[IntegrationFinding]:
        """Parse excessive access finding from Wiz.

        :param Dict[str, Any] node: The Wiz finding node to parse
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        scope = node.get("scope", {})
        asset_id = scope.get("graphEntity", {}).get("id")
        if not asset_id:
            return None

        first_seen = get_current_datetime()  # Excessive access findings may not have firstSeen
        first_seen = format_to_regscale_iso(first_seen)
        severity = self.get_issue_severity(node.get("severity", "Medium"))
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        # Use the finding name directly as it's descriptive
        title = node.get("name", "Excessive Access Detected")
        description = node.get("description", "")

        # Add remediation details
        remediation_parts = [node.get("description", "")]
        if remediation_instructions := node.get("remediationInstructions"):
            remediation_parts.append(f"Remediation: {remediation_instructions}")
        if policy_name := node.get("builtInPolicyRemediationName"):
            remediation_parts.append(f"Built-in policy: {policy_name}")

        remediation = "\n".join(filter(None, remediation_parts))

        return IntegrationFinding(
            control_labels=[],
            category="Wiz Excessive Access",
            title=title,
            description=description,
            severity=severity,
            status=self.map_status_to_issue_status(node.get("status", "Open")),
            asset_identifier=asset_id,
            external_id=node.get("id"),
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=first_seen,
            remediation=remediation,
            plugin_name=f"Wiz Excessive Access - {node.get('remediationType', 'Unknown')}",
            vulnerability_type=WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="Access Control Assessment",
        )

    def _parse_end_of_life_finding(self, node: Dict[str, Any]) -> Optional[IntegrationFinding]:
        """Parse end of life finding from Wiz."""
        asset_id = node.get("vulnerableAsset", {}).get("id")
        if not asset_id:
            return None

        first_seen = node.get("firstDetectedAt") or get_current_datetime()
        first_seen = format_to_regscale_iso(first_seen)
        severity = self.get_issue_severity(node.get("severity", "High"))
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        # Create meaningful title for end-of-life findings
        name = node.get("name", "Unknown Technology")
        title = f"End of Life: {name}"

        # Build description with EOL details
        description_parts = [node.get("description", "")]
        if eol_date := node.get("technologyEndOfLifeAt"):
            description_parts.append(f"End of life date: {eol_date}")
        if recommended_version := node.get("recommendedVersion"):
            description_parts.append(f"Recommended version: {recommended_version}")

        description = "\n".join(filter(None, description_parts))

        return IntegrationFinding(
            control_labels=[],
            category="Wiz End of Life",
            title=title,
            description=description,
            severity=severity,
            status=self.map_status_to_issue_status(node.get("status", "Open")),
            asset_identifier=asset_id,
            external_id=node.get("id"),
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=format_to_regscale_iso(node.get("lastDetectedAt") or get_current_datetime()),
            remediation=f"Upgrade {name} to a supported version",
            plugin_name=f"Wiz End of Life - {name}",
            vulnerability_type=WizVulnerabilityType.END_OF_LIFE_FINDING.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="Technology Lifecycle Assessment",
        )

    def _parse_generic_finding(
        self, node: Dict[str, Any], vulnerability_type: WizVulnerabilityType
    ) -> Optional[IntegrationFinding]:
        """Generic parsing method for fallback cases."""
        asset_id = self.get_asset_id_from_node(node, vulnerability_type)
        if not asset_id:
            return None

        first_seen = node.get("firstDetectedAt") or node.get("firstSeenAt") or get_current_datetime()
        first_seen = format_to_regscale_iso(first_seen)
        severity = self.get_issue_severity(node.get("severity", "Low"))
        due_date = regscale_models.Issue.get_due_date(severity, self.app.config, "wiz", first_seen)

        status = self.map_status_to_issue_status(node.get("status", "Open"))
        name: str = node.get("name", "")
        cve = (
            name
            if name and (name.startswith("CVE") or name.startswith("GHSA")) and not node.get("cve")
            else node.get("cve", name)
        )

        comments_dict = node.get("commentThread", {})
        formatted_comments = self.process_comments(comments_dict)

        return IntegrationFinding(
            control_labels=[],
            category="Wiz Vulnerability",
            title=node.get("name", "Unknown vulnerability"),
            description=node.get("description", ""),
            severity=severity,
            status=status,
            asset_identifier=asset_id,
            external_id=f"{node.get('sourceRule', {'id': cve}).get('id')}",
            first_seen=first_seen,
            date_created=first_seen,
            last_seen=format_to_regscale_iso(
                node.get("lastDetectedAt") or node.get("analyzedAt") or get_current_datetime()
            ),
            remediation=node.get("description", ""),
            cvss_score=node.get("score"),
            cve=cve,
            plugin_name=cve,
            cvss_v3_base_score=node.get("score"),
            source_rule_id=node.get("sourceRule", {}).get("id"),
            vulnerability_type=vulnerability_type.value,
            due_date=due_date,
            date_last_updated=format_to_regscale_iso(get_current_datetime()),
            identification="Vulnerability Assessment",
            comments=formatted_comments,
            poam_comments=formatted_comments,
        )

    def get_compliance_settings(self):
        """
        Get compliance settings for status mapping

        :return: Compliance settings instance
        :rtype: Optional[ComplianceSettings]
        """
        if self._compliance_settings is None:
            try:
                settings = ComplianceSettings.get_by_current_tenant()
                self._compliance_settings = next(
                    (comp for comp in settings if comp.title == "Wiz Compliance Setting"), None
                )
                if not self._compliance_settings:
                    logger.debug("No Wiz Compliance Setting found, using default status mapping")
                else:
                    logger.debug("Using Wiz Compliance Setting for status mapping")
            except Exception as e:
                logger.debug(f"Error getting Compliance Setting: {e}")
                self._compliance_settings = None
        return self._compliance_settings

    def map_status_to_issue_status(self, status: str) -> IssueStatus:
        """
        Maps the Wiz status to issue status using compliance settings if available

        :param str status: Status of the vulnerability
        :return: Issue status
        :rtype: IssueStatus
        """
        compliance_settings = self.get_compliance_settings()

        if compliance_settings:
            mapped_status = self._get_status_from_compliance_settings(status, compliance_settings)
            if mapped_status:
                return mapped_status

        # Fallback to default mapping
        return self._get_default_issue_status_mapping(status)

    def _get_status_from_compliance_settings(self, status: str, compliance_settings) -> Optional[IssueStatus]:
        """
        Get issue status from compliance settings

        :param str status: Wiz status
        :param compliance_settings: Compliance settings object
        :return: Issue status or None if not found
        :rtype: Optional[IssueStatus]
        """
        try:
            status_labels = compliance_settings.get_field_labels("status")
            status_lower = status.lower()

            for label in status_labels:
                mapped_status = self._match_wiz_status_to_label(status_lower, label)
                if mapped_status:
                    return mapped_status

            logger.debug(f"No matching compliance setting found for status: {status}")
            return None

        except Exception as e:
            logger.debug(f"Error using compliance settings for status mapping: {e}")
            return None

    def _match_wiz_status_to_label(self, status_lower: str, label: str) -> Optional[IssueStatus]:
        """
        Match a Wiz status to a compliance label and return appropriate IssueStatus

        :param str status_lower: Lowercase Wiz status
        :param str label: Compliance setting label to check
        :return: Matched IssueStatus or None
        :rtype: Optional[IssueStatus]
        """
        label_lower = label.lower()

        # Check for open status mappings
        if status_lower == "open" and label_lower in ["open", "active", "new"]:
            return IssueStatus.Open

        # Check for closed status mappings
        if status_lower in ["resolved", "rejected"] and label_lower in ["closed", "resolved", "rejected", "completed"]:
            return IssueStatus.Closed

        return None

    def _get_default_issue_status_mapping(self, status: str) -> IssueStatus:
        """
        Get default issue status mapping for a Wiz status

        :param str status: Wiz status
        :return: Default issue status
        :rtype: IssueStatus
        """
        status_lower = status.lower()

        if status_lower == "open":
            return IssueStatus.Open
        if status_lower in ["resolved", "rejected"]:
            return IssueStatus.Closed
        return IssueStatus.Open

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches Wiz assets using the GraphQL API with detailed progress tracking

        :yields: Iterator[IntegrationAsset]
        """
        # Create main task for asset fetching process
        main_task = self.asset_progress.add_task("[cyan]Fetching Wiz assets...", total=3)  # Auth, Query, Parse steps

        # Step 1: Authentication
        auth_task = self.asset_progress.add_task("[yellow]Authenticating to Wiz API...", total=None)

        self.authenticate(kwargs.get("client_id"), kwargs.get("client_secret"))

        self.asset_progress.update(
            auth_task, description="[green]✓ Successfully authenticated to Wiz API", completed=1, total=1
        )
        self.asset_progress.advance(main_task, 1)

        # Step 2: Query preparation and execution
        wiz_project_id: str = kwargs.get("wiz_project_id", "")
        filter_by_override: Dict[str, Any] = kwargs.get("filter_by_override") or WizVariables.wizInventoryFilterBy or {}
        filter_by = self.get_filter_by(filter_by_override, wiz_project_id)

        variables = self.get_variables()
        variables["filterBy"].update(filter_by)

        query_task = self.asset_progress.add_task(
            f"[yellow]Querying Wiz inventory for project {wiz_project_id[:8]}...", total=None
        )

        nodes = self.fetch_wiz_data_if_needed(
            query=INVENTORY_QUERY, variables=variables, topic_key="cloudResources", file_path=INVENTORY_FILE_PATH
        )

        self.asset_progress.update(
            query_task, description=f"[green]✓ Fetched {len(nodes)} assets from Wiz inventory", completed=1, total=1
        )
        self.asset_progress.advance(main_task, 1)

        self.num_assets_to_process = len(nodes)

        # Step 3: Parse assets with progress tracking
        if nodes:
            parse_task = self.asset_progress.add_task(f"[magenta]Parsing {len(nodes)} Wiz assets...", total=len(nodes))

            parsed_count = 0
            for i, node in enumerate(nodes, 1):
                if asset := self.parse_asset(node):
                    parsed_count += 1
                    yield asset

                self.asset_progress.advance(parse_task, 1)

            self.asset_progress.update(
                parse_task, description=f"[green]✓ Successfully parsed {parsed_count}/{len(nodes)} assets"
            )

        self.asset_progress.advance(main_task, 1)
        self.asset_progress.update(
            main_task, description=f"[green]✓ Completed Wiz asset fetching ({self.num_assets_to_process} assets)"
        )

        logger.info("Fetched %d Wiz assets.", len(nodes))

    @staticmethod
    def get_filter_by(filter_by_override: Union[str, Dict[str, Any]], wiz_project_id: str) -> Dict[str, Any]:
        """
        Constructs the filter_by dictionary for fetching assets

        :param Union[str, Dict[str, Any]] filter_by_override: Override for the filter_by dictionary
        :param str wiz_project_id: The Wiz project ID
        :return: The filter_by dictionary
        :rtype: Dict[str, Any]
        """
        if filter_by_override:
            return json.loads(filter_by_override) if isinstance(filter_by_override, str) else filter_by_override
        filter_by = {"project": wiz_project_id}
        if WizVariables.wizLastInventoryPull and not WizVariables.wizFullPullLimitHours:
            filter_by["updatedAt"] = {"after": WizVariables.wizLastInventoryPull}  # type: ignore
        return filter_by

    def get_software_details(
        self, wiz_entity_properties: dict, node: dict[str, Any], software_name_dict: dict[str, str], name: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Gets the software version, vendor, and name from the Wiz entity properties and node.
        Handles container images differently by extracting the version and name from the image tags.
        :param Dict wiz_entity_properties: The properties of the Wiz entity
        :param Dict node: The Wiz node containing the entity
        :param Dict software_name_dict: Dictionary containing software name and vendor
        :param str name: The name of the software or container image
        :return: A tuple containing software_version, software_vendor, and software_name
        :rtype: Tuple[Optional[str], Optional[str], Optional[str]]
        """
        if node.get("type", "") == "CONTAINER_IMAGE":
            software_version = handle_container_image_version(
                image_tags=wiz_entity_properties.get("imageTags", []), name=name
            )
            software_name = name.split(":")[0].split("/")[-1] if name else ""
            software_vendor = name.split(":")[0].split("/")[1] if len(name.split(":")[0].split("/")) > 1 else None
        else:
            software_version = self.get_software_version(wiz_entity_properties, node)
            software_name = self.get_software_name(software_name_dict, wiz_entity_properties, node)
            software_vendor = self.get_software_vendor(software_name_dict, wiz_entity_properties, node)

        return software_version, software_vendor, software_name

    def parse_asset(self, node: Dict[str, Any]) -> Optional[IntegrationAsset]:
        """
        Parses Wiz assets

        :param Dict[str, Any] node: The Wiz asset to parse
        :return: The parsed IntegrationAsset
        :rtype: Optional[IntegrationAsset]
        """
        name = node.get("name", "")
        wiz_entity = node.get("graphEntity", {})
        if not wiz_entity:
            logger.warning("No graph entity found for asset %s", name)
            return None

        wiz_entity_properties = wiz_entity.get("properties", {})
        is_public = False
        if (public_exposures := wiz_entity.get("publicExposures")) and (
            exposure_count := public_exposures.get("totalCount")
        ):
            is_public = exposure_count > 0

        network_dict = get_network_info(wiz_entity_properties)
        handle_provider_dict = handle_provider(wiz_entity_properties)
        software_name_dict = get_software_name_from_cpe(wiz_entity_properties, name)
        software_list = self.create_name_version_dict(wiz_entity_properties.get("installedPackages", []))
        ports_and_protocols = self.get_ports_and_protocols(wiz_entity_properties)

        software_version, software_vendor, software_name = self.get_software_details(
            wiz_entity_properties, node, software_name_dict, name
        )

        return IntegrationAsset(
            name=name,
            external_id=node.get("name"),
            asset_tag_number=node.get("id", ""),
            other_tracking_number=node.get("id", ""),
            identifier=node.get("id", ""),
            asset_type=create_asset_type(node.get("type", "")),
            asset_owner_id=ScannerVariables.userId,
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
            asset_category=map_category(node),
            date_last_updated=wiz_entity.get("lastSeen", ""),
            management_type=handle_management_type(wiz_entity_properties),
            status=self.map_wiz_status(wiz_entity_properties.get("status")),
            ip_address=network_dict.get("ip4_address"),
            ipv6_address=network_dict.get("ip6_address"),
            software_vendor=software_vendor,
            software_version=software_version,
            software_name=software_name,
            location=wiz_entity_properties.get("region"),
            notes=get_notes_from_wiz_props(wiz_entity_properties, node.get("id", "")),
            model=wiz_entity_properties.get("nativeType"),
            manufacturer=wiz_entity_properties.get("cloudPlatform"),
            serial_number=get_product_ids(wiz_entity_properties),
            is_public_facing=is_public,
            azure_identifier=handle_provider_dict.get("azureIdentifier", ""),
            mac_address=wiz_entity_properties.get("macAddress"),
            fqdn=network_dict.get("dns") or wiz_entity_properties.get("dnsName"),
            disk_storage=get_disk_storage(wiz_entity_properties) or 0,
            cpu=pull_resource_info_from_props(wiz_entity_properties)[1] or 0,
            ram=pull_resource_info_from_props(wiz_entity_properties)[0] or 0,
            operating_system=wiz_entity_properties.get("operatingSystem"),
            os_version=wiz_entity_properties.get("version"),
            end_of_life_date=wiz_entity_properties.get("versionEndOfLifeDate"),
            vlan_id=wiz_entity_properties.get("zone"),
            uri=network_dict.get("url"),
            aws_identifier=handle_provider_dict.get("awsIdentifier", ""),
            google_identifier=handle_provider_dict.get("googleIdentifier", ""),
            other_cloud_identifier=handle_provider_dict.get("otherCloudIdentifier", ""),
            patch_level=get_latest_version(wiz_entity_properties),
            cpe=wiz_entity_properties.get("cpe"),
            component_names=collect_components_to_create([node], []),
            source_data=node,
            url=wiz_entity_properties.get("cloudProviderURL"),
            ports_and_protocols=ports_and_protocols,
            software_inventory=software_list,
        )

    @staticmethod
    def get_ports_and_protocols(wiz_entity_properties: dict) -> List[Dict[str, Union[int, str]]]:
        """
        Extracts ports and protocols from Wiz entity properties using the "portStart","portEnd", and "protocol" keys.

        :param dict wiz_entity_properties: Dictionary containing Wiz entity properties
        :return: A list of dictionaries containing start_port, end_port, and protocol
        :rtype: List[Dict[str, Union[int, str]]]
        """
        start_port = wiz_entity_properties.get("portStart")
        if start_port is not None and isinstance(start_port, (int, str)):
            end_port = wiz_entity_properties.get("portEnd", start_port)
            if not isinstance(end_port, (int, str)):
                end_port = start_port

            protocol = wiz_entity_properties.get("protocols") or wiz_entity_properties.get("protocol")
            if not protocol or protocol == "other":
                protocol = get_base_protocol_from_port(start_port) or "tcp"

            # Ensure protocol is a string
            if not isinstance(protocol, str):
                protocol = "tcp"

            return [{"start_port": start_port, "end_port": end_port, "protocol": protocol}]
        return []

    @staticmethod
    def get_software_vendor(software_name_dict: dict, wiz_entity_properties: dict, node: dict) -> Optional[str]:
        """
        Gets the software vendor from the software name dictionary or Wiz entity properties.

        :param dict software_name_dict: Dictionary containing software name and vendor
        :param dict wiz_entity_properties: Properties of the Wiz entity
        :param dict node: Node dictionary
        :return: Software vendor
        :rtype: Optional[str]
        """

        if map_category(node) == regscale_models.AssetCategory.Software:
            return software_name_dict.get("software_vendor") or wiz_entity_properties.get("cloudPlatform")
        return None

    @staticmethod
    def get_software_version(wiz_entity_properties: dict, node: dict) -> Optional[str]:
        """
        Gets the software version from the Wiz entity properties or handles it based on the node type.

        :param dict wiz_entity_properties: Properties of the Wiz entity
        :param dict node: Node dictionary
        :return: Software version
        :rtype: Optional[str]
        """
        if map_category(node) == regscale_models.AssetCategory.Software:
            return handle_software_version(wiz_entity_properties, regscale_models.AssetCategory.Software) or "1.0"
        return None

    @staticmethod
    def get_software_name(software_name_dict: dict, wiz_entity_properties: dict, node: dict) -> Optional[str]:
        """
        Gets the software name from the software name dictionary or Wiz entity properties.
        If no software name is present, assigns a name based on the parent asset and assigned component type.

        :param dict software_name_dict: Dictionary containing software name and vendor
        :param dict wiz_entity_properties: Properties of the Wiz entity
        :param dict node: Node dictionary
        :return: Software name
        :rtype: Optional[str]
        """
        if map_category(node) != regscale_models.AssetCategory.Software:
            return None

        # First try CPE-derived software name
        if software_name := software_name_dict.get("software_name"):
            return software_name

        # Then try nativeType if it exists and looks meaningful
        native_type = wiz_entity_properties.get("nativeType")
        if native_type and not native_type.startswith(("Microsoft.", "AWS::", "Google.")):
            return native_type

        # Finally, generate a name based on parent asset and component type
        parent_name = node.get("name", "")
        component_type = node.get("type", "").replace("_", " ").title()

        if not parent_name:
            return component_type

        # Clean up parent name for better readability by removing
        # common prefixes/suffixes that aren't meaningful
        cleaned_parent = parent_name
        for prefix in ["1-", "temp-", "test-"]:
            if cleaned_parent.lower().startswith(prefix):
                cleaned_parent = cleaned_parent[len(prefix) :]
        return f"{cleaned_parent} - {component_type}" if cleaned_parent else component_type

    # Pre-compiled regex for better performance (ReDoS-safe pattern)
    _PACKAGE_PATTERN = re.compile(r"([^()]+) \(([^()]+)\)")

    @classmethod
    def create_name_version_dict(cls, package_list: List[str]) -> List[Dict[str, str]]:
        """
        Creates a list of dictionaries with package names and versions from formatted strings.

        :param List[str] package_list: List of strings in format "name (version)"
        :return: List of dictionaries with name and version keys
        :rtype: List[Dict[str, str]]
        """
        # Use list comprehension with pre-compiled regex for better performance
        return [
            {"name": match.group(1).strip(), "version": match.group(2).strip()}
            for package in package_list
            if (match := cls._PACKAGE_PATTERN.match(package))
        ]

    @staticmethod
    def map_wiz_status(wiz_status: Optional[str]) -> regscale_models.AssetStatus:
        """Map Wiz status to RegScale status."""
        return regscale_models.AssetStatus.Active if wiz_status != "Inactive" else regscale_models.AssetStatus.Inactive

    def fetch_wiz_data_if_needed(self, query: str, variables: Dict, topic_key: str, file_path: str) -> List[Dict]:
        """
        Fetch Wiz data if needed and save to file if not already fetched within the last 8 hours and return the data

        :param str query: GraphQL query string
        :param Dict variables: Query variables
        :param str topic_key: The key for the data in the response
        :param str file_path: Path to save the fetched data
        :return: List of nodes as dictionaries
        :rtype: List[Dict]
        """
        fetch_interval = datetime.timedelta(hours=WizVariables.wizFullPullLimitHours or 8)  # Interval to fetch new data
        current_time = datetime.datetime.now()
        check_file_path(os.path.dirname(file_path))

        if os.path.exists(file_path):
            file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if current_time - file_mod_time < fetch_interval:
                logger.info("File %s is newer than %s hours. Using cached data...", file_path, fetch_interval)
                with open(file_path, encoding="utf-8") as file:
                    return json.load(file)
            else:
                logger.info("File %s is older than %s hours. Fetching new data...", file_path, fetch_interval)
        else:
            logger.info("File %s does not exist. Fetching new data...", file_path)

        self.authenticate(WizVariables.wizClientId, WizVariables.wizClientSecret)

        if not self.wiz_token:
            error_and_exit("Wiz token is not set. Please authenticate first.")

        nodes = fetch_wiz_data(
            query=query,
            variables=variables,
            api_endpoint_url=WizVariables.wizUrl,
            token=self.wiz_token,
            topic_key=topic_key,
        )
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(nodes, file)

        return nodes

    def get_asset_by_identifier(self, identifier: str) -> Optional[regscale_models.Asset]:
        """
        Enhanced asset lookup with diagnostic logging for Wiz integration

        :param str identifier: The identifier of the asset
        :return: The asset
        :rtype: Optional[regscale_models.Asset]
        """
        # First try to get asset using parent method
        asset = self.asset_map_by_identifier.get(identifier)

        # If asset not found and we haven't already alerted for this asset
        if not asset and identifier not in self.alerted_assets:
            self.alerted_assets.add(identifier)

            # Add debug logging to confirm this method is being called
            logger.debug("WizVulnerabilityIntegration.get_asset_by_identifier called for %s", identifier)

            # Try to provide more diagnostic information
            if not getattr(self, "suppress_asset_not_found_errors", False):
                self._log_missing_asset_diagnostics(identifier)
                # Still log the original error for consistency
                self.log_error("1. Asset not found for identifier %s", identifier)

        return asset

    def _log_missing_asset_diagnostics(self, identifier: str) -> None:
        """
        Log diagnostic information about missing assets to help identify patterns

        :param str identifier: The missing asset identifier
        :rtype: None
        """
        logger.info("🔍 Analyzing missing asset: %s", identifier)

        # Define inventory files to search (constant moved up for clarity)
        inventory_files = (
            INVENTORY_FILE_PATH,
            SECRET_FINDINGS_FILE_PATH,
            NETWORK_EXPOSURE_FILE_PATH,
            END_OF_LIFE_FILE_PATH,
            EXTERNAL_ATTACK_SURFACE_FILE_PATH,
        )

        # Search for asset information across files
        asset_info, source_file = self._search_asset_in_files(identifier, inventory_files)

        # Log results based on what was found
        if asset_info:
            self._log_found_asset_details(identifier, asset_info, source_file)
        else:
            self._log_asset_not_found(identifier)

    def _search_asset_in_files(self, identifier: str, file_paths: tuple) -> tuple[Optional[Dict], Optional[str]]:
        """
        Search for asset information across multiple JSON files

        :param str identifier: Asset identifier to search for
        :param tuple file_paths: Tuple of file paths to search
        :return: Tuple of (asset_info, source_file) or (None, None)
        :rtype: tuple[Optional[Dict], Optional[str]]
        """
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            try:
                asset_info = self._search_single_file(identifier, file_path)
                if asset_info:
                    return asset_info, file_path
            except (OSError, json.JSONDecodeError) as e:
                logger.debug("Error reading %s: %s", file_path, e)
                continue

        return None, None

    def _search_single_file(self, identifier: str, file_path: str) -> Optional[Dict]:
        """
        Search for asset in a single JSON file

        :param str identifier: Asset identifier to search for
        :param str file_path: Path to JSON file
        :return: Asset data if found, None otherwise
        :rtype: Optional[Dict]
        """
        logger.debug("Searching for asset %s in %s", identifier, file_path)

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return None

        # Use generator expression for memory efficiency
        return next((item for item in data if self._find_asset_in_node(item, identifier)), None)

    def _log_found_asset_details(self, identifier: str, asset_info: Dict, source_file: str) -> None:
        """
        Log details for found asset with actionable recommendations

        :param str identifier: Asset identifier
        :param Dict asset_info: Asset information from file
        :param str source_file: Source file where asset was found
        :rtype: None
        """
        asset_type = self._extract_asset_type_from_node(asset_info)
        asset_name = self._extract_asset_name_from_node(asset_info)

        logger.warning(
            "🚨 MISSING ASSET FOUND: ID=%s, Type=%s, Name='%s', Source=%s\n"
            "   💡 SOLUTION: Add '%s' to RECOMMENDED_WIZ_INVENTORY_TYPES in constants.py\n"
            "   📍 Then re-run: regscale wiz inventory -id <plan_id> -p <project_id>",
            identifier,
            asset_type,
            asset_name,
            source_file,
            asset_type,
        )

    def _log_asset_not_found(self, identifier: str) -> None:
        """
        Log message when asset is not found in any cached files

        :param str identifier: Asset identifier
        :rtype: None
        """
        logger.warning(
            "❓ MISSING ASSET ANALYSIS: ID=%s\n"
            "   Asset not found in any cached data files.\n"
            "   This may indicate:\n"
            "   - Asset from different Wiz project\n"
            "   - Asset type not included in current queries\n"
            "   - Asset deleted from Wiz but finding still exists",
            identifier,
        )

    # Class-level constants for better performance (avoid recreating lists)
    _ASSET_ID_PATHS = (
        ("id",),
        ("resource", "id"),
        ("exposedEntity", "id"),
        ("vulnerableAsset", "id"),
        ("scope", "graphEntity", "id"),
        ("entitySnapshot", "id"),
    )

    _ASSET_TYPE_PATHS = (
        ("type",),
        ("resource", "type"),
        ("exposedEntity", "type"),
        ("vulnerableAsset", "type"),
        ("scope", "graphEntity", "type"),
        ("entitySnapshot", "type"),
    )

    _ASSET_NAME_PATHS = (
        ("name",),
        ("resource", "name"),
        ("exposedEntity", "name"),
        ("vulnerableAsset", "name"),
        ("scope", "graphEntity", "name"),
        ("entitySnapshot", "name"),
    )

    def _find_asset_in_node(self, node: Dict[str, Any], identifier: str) -> bool:
        """
        Check if a node contains the specified asset identifier.

        :param Dict[str, Any] node: Node to search in
        :param str identifier: Asset identifier to find
        :return: True if identifier found, False otherwise
        :rtype: bool
        """
        return any(self._get_nested_value(node, path) == identifier for path in self._ASSET_ID_PATHS)

    def _extract_asset_type_from_node(self, node: Dict[str, Any]) -> str:
        """
        Extract asset type from a node for diagnostic purposes.

        :param Dict[str, Any] node: Node to extract type from
        :return: Asset type or "Unknown Type"
        :rtype: str
        """
        for path in self._ASSET_TYPE_PATHS:
            value = self._get_nested_value(node, path)
            if isinstance(value, str):
                return value
        return "Unknown Type"

    def _extract_asset_name_from_node(self, node: Dict[str, Any]) -> str:
        """
        Extract asset name from a node for diagnostic purposes.

        :param Dict[str, Any] node: Node to extract name from
        :return: Asset name or "Unknown Name"
        :rtype: str
        """
        for path in self._ASSET_NAME_PATHS:
            value = self._get_nested_value(node, path)
            if isinstance(value, str):
                return value
        return "Unknown Name"

    def _get_nested_value(self, data: Dict[str, Any], path: tuple) -> Any:
        """
        Get a nested value from a dictionary using a path tuple.

        :param Dict[str, Any] data: Dictionary to traverse
        :param tuple path: Tuple of keys representing the path
        :return: Value at path or None if not found
        :rtype: Any
        """
        current = data
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None
        return current
