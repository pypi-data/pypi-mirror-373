#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract Compliance Integration Base Class

This module provides a base class for implementing compliance integrations
that follow common patterns across different compliance tools (Wiz, Tenable, Sicura).
"""
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Any, Iterator

from regscale.core.app.utils.app_utils import get_current_datetime, regscale_string_to_datetime
from regscale.integrations.scanner_integration import (
    ScannerIntegration,
    IntegrationAsset,
    IntegrationFinding,
)
from regscale.models import regscale_models
from regscale.models.regscale_models import (
    Catalog,
    SecurityControl,
    ControlImplementation,
    Assessment,
    ImplementationObjective,
)

logger = logging.getLogger("regscale")

# Safer, linear-time regex for control-id parsing/normalization used across
# compliance integrations. Supports: 'AC-4', 'AC-4(2)', 'AC-4 (2)', 'AC-4-2', 'AC-4 2'
# Distinct branches ('(', '-' or whitespace) avoid ambiguous nested alternation
# and excessive backtracking that could be used for DoS.
SAFE_CONTROL_ID_RE = re.compile(  # NOSONAR
    r"^([A-Za-z]{2}-\d+)(?:\s*\(\s*(\d+)\s*\)|-\s*(\d+)|\s+(\d+))?$",  # NOSONAR
    re.IGNORECASE,  # NOSONAR
)


class ComplianceItem(ABC):
    """
    Abstract base class representing a compliance assessment item.

    This represents a single compliance check result for a specific
    resource against a specific control.
    """

    @property
    @abstractmethod
    def resource_id(self) -> str:
        """Unique identifier for the resource being assessed."""
        pass

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Human-readable name of the resource."""
        pass

    @property
    @abstractmethod
    def control_id(self) -> str:
        """Control identifier (e.g., AC-3, SI-2)."""
        pass

    @property
    @abstractmethod
    def compliance_result(self) -> str:
        """Result of compliance check (PASS, FAIL, etc)."""
        pass

    @property
    @abstractmethod
    def severity(self) -> Optional[str]:
        """Severity level of the compliance violation (if failed)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the compliance check."""
        pass

    @property
    @abstractmethod
    def framework(self) -> str:
        """Compliance framework (e.g., NIST800-53R5, CSF)."""
        pass


class ComplianceIntegration(ScannerIntegration, ABC):
    """
    Abstract base class for compliance integrations.

    This class provides common patterns for:
    - Processing compliance data
    - Creating assets from compliance items
    - Creating findings/issues for failed compliance
    - Mapping compliance items to controls
    - Creating assessments and updating control status
    """

    # Status mapping constants
    PASS_STATUSES = ["PASS", "PASSED", "pass", "passed"]
    FAIL_STATUSES = ["FAIL", "FAILED", "fail", "failed"]

    def __init__(
        self,
        plan_id: int,
        catalog_id: Optional[int] = None,
        framework: str = "NIST800-53R5",
        create_issues: bool = True,
        update_control_status: bool = True,
        create_poams: bool = False,
        parent_module: str = "securityplans",
        **kwargs,
    ):
        """
        Initialize compliance integration.

        :param int plan_id: RegScale plan ID
        :param Optional[int] catalog_id: RegScale catalog ID
        :param str framework: Compliance framework
        :param bool create_issues: Whether to create issues for failed compliance
        :param bool update_control_status: Whether to update control implementation status
        :param bool create_poams: Whether to mark issues as POAMs
        """
        super().__init__(plan_id=plan_id, **kwargs)

        self.catalog_id = catalog_id
        self.framework = framework
        self.create_issues = create_issues
        self.update_control_status = update_control_status
        self.create_poams = create_poams

        # Compliance data storage
        self.all_compliance_items: List[ComplianceItem] = []
        self.failed_compliance_items: List[ComplianceItem] = []
        self.passing_controls: Dict[str, ComplianceItem] = {}
        self.failing_controls: Dict[str, ComplianceItem] = {}

        # Asset mapping for compliance to asset correlation
        self.asset_compliance_map: Dict[str, List[ComplianceItem]] = defaultdict(list)

        # Initialize caches for existing records to prevent duplicates
        self._existing_assets_cache: Dict[str, regscale_models.Asset] = {}
        self._existing_issues_cache: Dict[str, regscale_models.Issue] = {}
        self._existing_assessments_cache: Dict[str, regscale_models.Assessment] = {}
        self._cache_loaded = False

        # Mapping caches for linking issues to implementations and assessments
        # Key: canonical control id string (e.g., "AC-2(1)") -> ControlImplementation.id
        self._impl_id_by_control: Dict[str, int] = {}
        # Key: ControlImplementation.id -> Assessment created/updated today
        self._assessment_by_impl_today: Dict[int, regscale_models.Assessment] = {}
        # suppress asset not found errors in non-debug modes
        self.suppress_asset_not_found_errors = logger.level != logging.DEBUG
        # Set scan date
        self.scan_date = get_current_datetime()

    def is_poam(self, finding: IntegrationFinding) -> bool:  # type: ignore[override]
        """
        Determines if an issue should be considered a POAM for compliance integrations.

        - If the integration was initialized with `create_poams=True` (e.g., via `--create-poams/-cp`),
          always return True so newly created and updated issues are POAMs.
        - Otherwise, defer to the generic scanner behavior.
        """
        try:
            if getattr(self, "create_poams", False):
                return True
            if finding.due_date >= get_current_datetime():
                return True
        except Exception:
            pass
        return super().is_poam(finding)

    def _load_existing_records_cache(self) -> None:
        """
        Load existing RegScale records into cache to prevent duplicates.
        This method populates caches for assets, issues, and assessments.

        :return: None
        :rtype: None
        """
        if self._cache_loaded:
            return

        logger.info("Loading existing RegScale records to prevent duplicates...")

        try:
            # Load existing assets for this plan
            self._load_existing_assets()

            # Load existing issues for this plan
            self._load_existing_issues()

            # Load existing assessments for control implementations
            self._load_existing_assessments()

            self._cache_loaded = True
            logger.info("Loaded existing records cache to prevent duplicates:")
            logger.info(f"   - Assets: {len(self._existing_assets_cache)}")
            logger.info(f"   - Issues: {len(self._existing_issues_cache)}")
            logger.info(f"   - Assessments: {len(self._existing_assessments_cache)}")

        except Exception as e:
            logger.error(f"Error loading existing records cache: {e}")
            # Continue without cache to avoid blocking the integration
            self._cache_loaded = True

    def _load_existing_assets(self) -> None:
        """
        Load existing assets into cache.

        :return: None
        :rtype: None
        """
        try:
            # Get all assets for this plan
            existing_assets = regscale_models.Asset.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            for asset in existing_assets:
                # Cache by external_id, identifier, and other_tracking_number for flexible lookup
                if hasattr(asset, "externalId") and asset.externalId:
                    self._existing_assets_cache[asset.externalId] = asset
                if hasattr(asset, "identifier") and asset.identifier:
                    self._existing_assets_cache[asset.identifier] = asset
                if hasattr(asset, "otherTrackingNumber") and asset.otherTrackingNumber:
                    self._existing_assets_cache[asset.otherTrackingNumber] = asset

        except Exception as e:
            logger.debug(f"Error loading existing assets: {e}")

    def _load_existing_issues(self) -> None:
        """
        Load existing issues into cache.

        Uses both plan-level and control-level queries to ensure all relevant issues are found.

        :return: None
        :rtype: None
        """
        try:
            all_issues = set()

            # Method 1: Get issues directly associated with the plan
            plan_issues = regscale_models.Issue.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )
            all_issues.update(plan_issues)
            logger.debug(f"Found {len(plan_issues)} issues directly under plan {self.plan_id}")

            # Method 2: Get issues associated with control implementations (matches scanner integration logic)
            try:
                issues_by_impl = regscale_models.Issue.get_open_issues_ids_by_implementation_id(
                    plan_id=self.plan_id, is_component=getattr(self, "is_component", False)
                )
                impl_issues_count = 0
                for impl_id, issue_list in issues_by_impl.items():
                    for issue_dict in issue_list:
                        # issue_dict contains issue data, need to get the actual issue object
                        issue_id = issue_dict.get("id")
                        if issue_id:
                            try:
                                issue = regscale_models.Issue.get_object(object_id=issue_id)
                                if issue:
                                    all_issues.add(issue)
                                    impl_issues_count += 1
                            except Exception as e:
                                logger.debug(f"Could not load issue {issue_id}: {e}")

                logger.debug(f"Found {impl_issues_count} additional issues via control implementations")
            except Exception as e:
                logger.debug(f"Could not load issues by control implementation: {e}")

            logger.debug(f"Total unique issues found: {len(all_issues)} for plan {self.plan_id}")

            wiz_issues = 0
            for issue in all_issues:
                # Cache by external_id and other_identifier for flexible lookup
                if hasattr(issue, "externalId") and issue.externalId:
                    self._existing_issues_cache[issue.externalId] = issue
                    if "wiz-policy" in issue.externalId.lower():
                        wiz_issues += 1
                        logger.debug(f"Cached Wiz issue: {issue.id} -> external_id: {issue.externalId}")
                if hasattr(issue, "otherIdentifier") and issue.otherIdentifier:
                    self._existing_issues_cache[issue.otherIdentifier] = issue

            logger.debug(f"Cached {wiz_issues} Wiz policy issues out of {len(all_issues)} total issues")

        except Exception as e:
            logger.debug(f"Error loading existing issues: {e}")

    def _load_existing_assessments(self) -> None:
        """
        Load existing assessments into cache.

        :return: None
        :rtype: None
        """
        try:
            # Get control implementations for this plan to find their assessments
            implementations = ControlImplementation.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            for implementation in implementations:
                try:
                    # Get assessments for this implementation
                    assessments = regscale_models.Assessment.get_all_by_parent(
                        parent_id=implementation.id, parent_module="controls"
                    )

                    for assessment in assessments:
                        # Create cache key: impl_id + day (YYYY-MM-DD)
                        if hasattr(assessment, "actualFinish") and assessment.actualFinish:
                            try:
                                # actualFinish may be a string; normalize to date-only key
                                if hasattr(assessment.actualFinish, "date"):
                                    day_key = assessment.actualFinish.date().isoformat()
                                else:
                                    day_key = regscale_string_to_datetime(assessment.actualFinish).date().isoformat()
                                cache_key = f"{implementation.id}_{day_key}"
                                self._existing_assessments_cache[cache_key] = assessment
                            except Exception:
                                continue

                except Exception as e:
                    logger.debug(f"Error loading assessments for implementation {implementation.id}: {e}")

        except Exception as e:
            logger.debug(f"Error loading existing assessments: {e}")

    def _find_existing_asset_cached(self, resource_id: str) -> Optional[regscale_models.Asset]:
        """
        Find existing asset by resource ID using cache.

        :param str resource_id: Resource identifier to search for
        :return: Existing asset or None if not found
        :rtype: Optional[regscale_models.Asset]
        """
        return self._existing_assets_cache.get(resource_id)

    def _find_existing_issue_cached(self, external_id: str) -> Optional[regscale_models.Issue]:
        """
        Find existing issue by external ID using cache.

        :param str external_id: External identifier to search for
        :return: Existing issue or None if not found
        :rtype: Optional[regscale_models.Issue]
        """
        return self._existing_issues_cache.get(external_id)

    def _find_existing_assessment_cached(
        self, implementation_id: int, scan_date
    ) -> Optional[regscale_models.Assessment]:
        """
        Find existing assessment by implementation ID and date using cache.

        :param int implementation_id: Control implementation ID
        :param scan_date: Scan date to check against existing assessments
        :return: Existing assessment or None if not found
        :rtype: Optional[regscale_models.Assessment]
        """
        # Normalize to date-only key
        try:
            if hasattr(scan_date, "date"):
                day_key = scan_date.date().isoformat()
            else:
                day_key = regscale_string_to_datetime(str(scan_date)).date().isoformat()
        except Exception:
            day_key = str(scan_date).split(" ")[0]
        cache_key = f"{implementation_id}_{day_key}"
        return self._existing_assessments_cache.get(cache_key)

    @abstractmethod
    def fetch_compliance_data(self) -> List[Any]:
        """
        Fetch raw compliance data from the external system.

        :return: List of raw compliance data (will be converted to ComplianceItems)
        :rtype: List[Any]
        """
        pass

    @abstractmethod
    def create_compliance_item(self, raw_data: Any) -> ComplianceItem:
        """
        Create a ComplianceItem from raw compliance data.

        :param Any raw_data: Raw compliance data from external system
        :return: ComplianceItem instance
        :rtype: ComplianceItem
        """
        pass

    def process_compliance_data(self) -> None:
        """
        Process compliance data and categorize items.

        Separates passing and failing compliance items and builds
        control status mappings.

        :return: None
        :rtype: None
        """
        logger.info("Processing compliance data...")

        # Reset state to avoid double counting on repeated calls
        self.all_compliance_items = []
        self.failed_compliance_items = []
        self.passing_controls = {}
        self.failing_controls = {}
        self.asset_compliance_map.clear()

        # Build allowed control IDs from plan/catalog controls to restrict scope
        allowed_controls_normalized: set[str] = set()
        try:
            controls = self._get_controls()
            for ctl in controls:
                cid = (ctl.get("controlId") or "").strip()
                if not cid:
                    continue
                base, sub = self._normalize_control_id(cid)
                normalized = f"{base}({sub})" if sub else base
                allowed_controls_normalized.add(normalized)
        except Exception:
            # If controls cannot be loaded, proceed without additional filtering
            allowed_controls_normalized = set()

        # Fetch raw compliance data
        raw_compliance_data = self.fetch_compliance_data()

        # Convert to ComplianceItem objects
        for raw_item in raw_compliance_data:
            try:
                compliance_item = self.create_compliance_item(raw_item)
                # Skip items that do not resolve to a control or resource
                if not getattr(compliance_item, "control_id", "") or not getattr(compliance_item, "resource_id", ""):
                    continue

                # If we have an allowed set, restrict to only controls in current plan/catalog
                if allowed_controls_normalized:
                    base, sub = self._normalize_control_id(getattr(compliance_item, "control_id", ""))
                    norm_item = f"{base}({sub})" if sub else base
                    if norm_item not in allowed_controls_normalized:
                        continue
                self.all_compliance_items.append(compliance_item)

                # Build asset mapping
                self.asset_compliance_map[compliance_item.resource_id].append(compliance_item)

                # Categorize by result
                if compliance_item.compliance_result in self.FAIL_STATUSES:
                    self.failed_compliance_items.append(compliance_item)
                    # Track failing controls (control can fail if ANY asset fails)
                    control_key = compliance_item.control_id.lower()
                    self.failing_controls[control_key] = compliance_item
                    # Remove from passing if it was there
                    self.passing_controls.pop(control_key, None)

                elif compliance_item.compliance_result in self.PASS_STATUSES:
                    control_key = compliance_item.control_id.lower()
                    # Only mark as passing if not already failing
                    if control_key not in self.failing_controls:
                        self.passing_controls[control_key] = compliance_item

            except Exception as e:
                logger.error(f"Error processing compliance item: {e}")
                continue

        logger.debug(
            f"Processed {len(self.all_compliance_items)} compliance items: "
            f"{len(self.all_compliance_items) - len(self.failed_compliance_items)} passing, "
            f"{len(self.failed_compliance_items)} failing"
        )

    def create_asset_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationAsset]:
        """
        Create an IntegrationAsset from a compliance item.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationAsset or None
        :rtype: Optional[IntegrationAsset]
        """
        try:
            # Check if asset already exists
            existing_asset = self._find_existing_asset_by_resource_id(compliance_item.resource_id)
            if existing_asset:
                return None

            asset_type = self._map_resource_type_to_asset_type(compliance_item)

            asset = IntegrationAsset(
                name=compliance_item.resource_name,
                identifier=compliance_item.resource_id,
                external_id=compliance_item.resource_id,
                other_tracking_number=compliance_item.resource_id,  # For deduplication
                asset_type=asset_type,
                asset_category=regscale_models.AssetCategory.Hardware,
                description=f"Asset from {self.title} compliance scan",
                parent_id=self.plan_id,
                parent_module=self.parent_module,
                status=regscale_models.AssetStatus.Active,
                date_last_updated=self.scan_date,
            )

            return asset

        except Exception as e:
            logger.error(f"Error creating asset from compliance item: {e}")
            return None

    def create_finding_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationFinding]:
        """
        Create an IntegrationFinding from a failed compliance item.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationFinding or None
        :rtype: Optional[IntegrationFinding]
        """
        try:
            control_labels = [compliance_item.control_id] if compliance_item.control_id else []
            severity = self._map_severity(compliance_item.severity)

            finding = IntegrationFinding(
                control_labels=control_labels,
                title=f"Compliance Violation: {compliance_item.control_id}",
                category="Compliance",
                plugin_name=f"{self.title} Compliance Scanner",
                severity=severity,
                description=compliance_item.description,
                status=regscale_models.IssueStatus.Open,
                priority=self._map_severity_to_priority(severity),
                external_id=f"{self.title.lower()}-{compliance_item.control_id}-{compliance_item.resource_id}",
                first_seen=self.scan_date,
                last_seen=self.scan_date,
                scan_date=self.scan_date,
                asset_identifier=compliance_item.resource_id,
                vulnerability_type="Compliance Violation",
                rule_id=compliance_item.control_id,
                baseline=compliance_item.framework,
                affected_controls=",".join(compliance_item.control_id),
            )

            # Ensure affected controls are set to the normalized control label (e.g., RA-5, AC-2(1))
            if compliance_item.control_id:
                base, sub = self._normalize_control_id(compliance_item.control_id)
                finding.affected_controls = f"{base}({sub})" if sub else base

            return finding

        except Exception as e:
            logger.error(f"Error creating finding from compliance item: {e}")
            return None

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetch assets from compliance items, avoiding duplicates.

        :param args: Variable positional arguments
        :param kwargs: Variable keyword arguments
        :return: Iterator of integration assets
        :rtype: Iterator[IntegrationAsset]
        """
        logger.info("Fetching assets from compliance items...")

        # Load cache if not already loaded
        self._load_existing_records_cache()

        processed_resources = set()
        for compliance_item in self.all_compliance_items:
            if compliance_item.resource_id not in processed_resources:
                # Check if asset already exists in RegScale
                existing_asset = self._find_existing_asset_cached(compliance_item.resource_id)
                if existing_asset:
                    logger.debug(f"Asset already exists for resource {compliance_item.resource_id}, skipping creation")
                    processed_resources.add(compliance_item.resource_id)
                    continue

                asset = self.create_asset_from_compliance_item(compliance_item)
                if asset:
                    processed_resources.add(compliance_item.resource_id)
                    yield asset

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetch findings from failed compliance items.

        :param args: Variable positional arguments
        :param kwargs: Variable keyword arguments
        :return: Iterator of integration findings
        :rtype: Iterator[IntegrationFinding]
        """
        logger.info("Fetching findings from failed compliance items...")

        total = len(self.failed_compliance_items)
        task_id = self.finding_progress.add_task(
            f"[#f68d1f]Creating findings from {total} failed compliance item(s)...",
            total=total or None,
        )

        for compliance_item in self.failed_compliance_items:
            finding = self.create_finding_from_compliance_item(compliance_item)
            if finding:
                self.finding_progress.advance(task_id, 1)
                yield finding

        # Ensure task completes if total is known
        if total:
            self.finding_progress.update(task_id, completed=total)

    def sync_compliance(self) -> None:
        """
        Main method to sync compliance data.

        This method orchestrates the entire compliance sync process:
        1. Process compliance data
        2. Create assets and findings
        3. Create/update control assessments
        4. Update control implementation status

        :return: None
        :rtype: None
        """
        logger.info(f"Starting {self.title} compliance sync...")

        try:
            scan_history = self.create_scan_history()
            self.process_compliance_data()

            self._sync_assets()
            self._sync_control_assessments()
            self._sync_issues()
            self._finalize_scan_history(scan_history)

            logger.info(f"Completed {self.title} compliance sync")

        except Exception as e:
            logger.error(f"Error during compliance sync: {e}")
            raise

    def _sync_assets(self) -> None:
        """
        Process and sync assets from compliance items.

        :return: None
        :rtype: None
        """
        assets = list(self.fetch_assets())
        if not assets:
            logger.debug("No assets generated from compliance items")
            return

        assets_processed = self.update_regscale_assets(iter(assets))
        self._log_asset_results(assets_processed)

    def _log_asset_results(self, assets_processed: int) -> None:
        """
        Log asset processing results.

        :param int assets_processed: Number of assets processed
        :return: None
        :rtype: None
        """
        results = getattr(self, "_results", {}).get("assets", {})
        created = results.get("created_count", 0)
        updated = results.get("updated_count", 0)
        deleted = results.get("deleted_count", 0) if isinstance(results, dict) else 0

        if deleted > 0:
            logger.info(
                f"Assets processed: {assets_processed} (created: {created}, updated: {updated}, deleted: {deleted})"
            )
        elif created > 0 or updated > 0:
            logger.info(f"Assets processed: {assets_processed} (created: {created}, updated: {updated})")
        else:
            logger.debug(f"Assets processed: {assets_processed} (no changes made)")

    def _sync_control_assessments(self) -> None:
        """
        Process control assessments if enabled.

        :return: None
        :rtype: None
        """
        if self.update_control_status:
            self._process_control_assessments()

    def _sync_issues(self) -> None:
        """
        Process and sync issues from failed compliance items.

        :return: None
        :rtype: None
        """
        if not self.create_issues:
            return

        findings = list(self.fetch_findings())
        if not findings:
            logger.debug("No findings to process into issues")
            return

        issues_created, issues_skipped = self._process_findings_to_issues(findings)
        self._log_issue_results(issues_created, issues_skipped)

    def _process_findings_to_issues(self, findings: List[IntegrationFinding]) -> tuple[int, int]:
        """
        Process findings into issues and return counts.

        :param findings: List of findings to process
        :return: Tuple of (issues_created, issues_skipped)
        """
        issues_created = 0
        issues_skipped = 0

        for finding in findings:
            try:
                if self._process_single_finding(finding):
                    issues_created += 1
                else:
                    issues_skipped += 1
            except Exception as e:
                logger.error(f"Error processing finding: {e}")
                issues_skipped += 1

        return issues_created, issues_skipped

    def _process_single_finding(self, finding: IntegrationFinding) -> bool:
        """
        Process a single finding into an issue.

        :param finding: Finding to process
        :return: True if issue was created/updated, False if skipped
        """
        asset = self._get_or_create_asset_for_finding(finding)
        if not asset:
            self._log_asset_not_found_error(finding)
            return False

        issue_title = self.get_issue_title(finding)
        issue = self.create_or_update_issue_from_finding(title=issue_title, finding=finding)
        return issue is not None

    def _get_or_create_asset_for_finding(self, finding: IntegrationFinding) -> Optional[regscale_models.Asset]:
        """
        Get existing asset or create one on-demand for the finding.

        :param IntegrationFinding finding: Finding needing an asset
        :return: Asset if found/created, None otherwise
        :rtype: Optional[regscale_models.Asset]
        """
        asset = self.get_asset_by_identifier(finding.asset_identifier)
        if not asset:
            asset = self._ensure_asset_for_finding(finding)
        return asset

    def _log_asset_not_found_error(self, finding: IntegrationFinding) -> None:
        """
        Log error when asset is not found for a finding.

        :param IntegrationFinding finding: Finding with missing asset
        :return: None
        :rtype: None
        """
        if not getattr(self, "suppress_asset_not_found_errors", False):
            logger.error(
                f"Asset not found for identifier {finding.asset_identifier} — "
                "skipping issue creation for this finding"
            )

    def _log_issue_results(self, issues_created: int, issues_skipped: int) -> None:
        """
        Log issue processing results.

        :param int issues_created: Number of issues created/updated
        :param int issues_skipped: Number of issues skipped
        :return: None
        :rtype: None
        """
        if issues_created > 0:
            logger.info(f"Issues processed: {issues_created} created/updated, {issues_skipped} skipped")
        elif issues_skipped > 0:
            logger.warning(f"Issues processed: 0 created, {issues_skipped} skipped (assets not found)")
        else:
            logger.debug("No issues processed")

    def _finalize_scan_history(self, scan_history: regscale_models.ScanHistory) -> None:
        """
        Finalize scan history with error handling.

        :param regscale_models.ScanHistory scan_history: Scan history to update
        :return: None
        :rtype: None
        """
        try:
            if getattr(self, "enable_scan_history", True):
                self._update_scan_history(scan_history)
        except Exception:
            self._update_scan_history(scan_history)

    def _ensure_asset_for_finding(self, finding: IntegrationFinding) -> Optional[regscale_models.Asset]:
        """
        Ensure an asset exists for the given finding.

        Attempts to locate the asset by identifier. If missing, it will try to
        build an IntegrationAsset from the first compliance item associated with
        the resource id and upsert it into RegScale, then return the created asset.

        :param IntegrationFinding finding: Finding referencing the asset identifier
        :return: The located or newly created Asset, or None if it cannot be created
        :rtype: Optional[regscale_models.Asset]
        """
        try:
            resource_id = getattr(finding, "asset_identifier", None)
            if not resource_id:
                return None

            # Re-check cache/DB
            asset = self.get_asset_by_identifier(resource_id)
            if asset:
                return asset

            # Use compliance items we already processed to construct an asset
            related_items = self.asset_compliance_map.get(resource_id, [])
            if not related_items:
                return None

            candidate_item = related_items[0]
            integration_asset = self.create_asset_from_compliance_item(candidate_item)
            if not integration_asset:
                return None

            # Persist the asset and refresh lookup
            _ = self.update_regscale_assets(iter([integration_asset]))
            return self.get_asset_by_identifier(resource_id)

        except Exception as ensure_exc:
            logger.debug(
                f"On-demand asset creation failed for {getattr(finding, 'asset_identifier', None)}: {ensure_exc}"
            )
            return None

    def _process_control_assessments(self) -> None:
        """
        Process control assessments based on compliance results.

        This follows the same pattern as the original Wiz compliance integration:
        1. Get control implementations
        2. For each implementation, get the security control using controlID
        3. Match the security control's controlId with the extracted control ID from compliance items

        :return: None
        :rtype: None
        """
        logger.info("Processing control assessments...")

        # Ensure existing records cache (including assessments) is loaded to prevent duplicates
        self._load_existing_records_cache()

        implementations = self._get_control_implementations()
        if not implementations:
            logger.warning("No control implementations found for assessment processing")
            return

        all_control_ids = set(self.passing_controls.keys()) | set(self.failing_controls.keys())
        logger.info(f"Processing assessments for {len(all_control_ids)} controls with compliance data")
        logger.info(f"Control IDs with data: {sorted(list(all_control_ids))}")
        self._log_sample_controls(implementations)

        assessments_created = 0
        processed_impl_today: set[int] = set()
        for control_id in all_control_ids:
            created = self._process_single_control_assessment(
                control_id=control_id,
                implementations=implementations,
                processed_impl_today=processed_impl_today,
            )
            assessments_created += created

        if assessments_created > 0:
            logger.info(f"Successfully created {assessments_created} control assessments")
        passing_assessments = len([cid for cid in all_control_ids if cid not in self.failing_controls])
        failing_assessments = len([cid for cid in all_control_ids if cid in self.failing_controls])
        logger.info(f"Assessment breakdown: {passing_assessments} passing, {failing_assessments} failing")
        logger.debug(f"Control implementation mappings created: {len(self._impl_id_by_control)}")
        if self._impl_id_by_control:
            logger.debug(f"Sample mappings: {dict(list(self._impl_id_by_control.items())[:5])}")
        logger.debug(f"Today's assessments by implementation: {len(self._assessment_by_impl_today)}")
        if self._assessment_by_impl_today:
            logger.debug(f"Sample assessment mappings: {dict(list(self._assessment_by_impl_today.items())[:5])}")

    def _get_control_implementations(self) -> List[ControlImplementation]:
        """
        Get all control implementations for the current plan.

        :return: List of control implementations
        :rtype: List[ControlImplementation]
        """
        implementations: List[ControlImplementation] = ControlImplementation.get_all_by_parent(
            parent_module=self.parent_module, parent_id=self.plan_id
        )
        logger.info(f"Found {len(implementations)} control implementations")
        return implementations

    def _log_sample_controls(self, implementations: List[ControlImplementation]) -> None:
        """
        Log sample control IDs for debugging purposes.

        :param List[ControlImplementation] implementations: List of implementations to sample from
        :return: None
        :rtype: None
        """
        sample_regscale_controls: List[str] = []
        for impl in implementations[:10]:
            try:
                sec_control = SecurityControl.get_object(object_id=impl.controlID)
                if sec_control and sec_control.controlId:
                    sample_regscale_controls.append(f"{sec_control.controlId}")
                else:
                    sample_regscale_controls.append(f"NoControlId-impl:{impl.id}-controlID:{impl.controlID}")
            except Exception as e:  # noqa: BLE001
                sample_regscale_controls.append(f"ERROR-impl:{impl.id}-controlID:{impl.controlID}-error:{str(e)[:50]}")
                logger.error(
                    f"Error fetching SecurityControl for implementation {impl.id} with controlID {impl.controlID}: {e}"
                )
        logger.info(f"Sample RegScale control IDs available: {sample_regscale_controls}")

    def _process_single_control_assessment(
        self,
        *,
        control_id: str,
        implementations: List[ControlImplementation],
        processed_impl_today: set[int],
    ) -> int:
        """
        Process assessment for a single control.

        :param str control_id: Control identifier to process
        :param List[ControlImplementation] implementations: Available control implementations
        :param set[int] processed_impl_today: Set of implementation IDs already processed today
        :return: Number of assessments created (0 or 1)
        :rtype: int
        """
        try:
            logger.debug(f"Processing control assessment for '{control_id}'")
            impl, sec_control = self._find_matching_implementation(control_id, implementations)
            if not impl or not sec_control:
                self._log_no_match(control_id, implementations)
                return 0

            result = self._determine_overall_result(control_id)
            items = self._get_control_compliance_items(control_id)
            logger.debug(f"Control '{control_id}' assessment: {result} (based on {len(items)} policy assessments)")

            if impl.id in processed_impl_today and self._find_existing_assessment_cached(impl.id, self.scan_date):
                logger.debug(f"Skipping duplicate assessment for implementation {impl.id} (already processed today)")
            else:
                self._create_control_assessment(
                    implementation=impl,
                    catalog_control={"id": sec_control.id, "controlId": sec_control.controlId},
                    result=result,
                    control_id=control_id,
                    compliance_items=items,
                )
                processed_impl_today.add(impl.id)

            self._record_control_mapping(control_id, impl.id)
            self._map_assets_to_control_component(sec_control, items)
            return 1
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error processing control assessment for '{control_id}': {e}")
            import traceback

            logger.debug(traceback.format_exc())
            return 0

    def _find_matching_implementation(
        self, control_id: str, implementations: List[ControlImplementation]
    ) -> tuple[Optional[ControlImplementation], Optional[SecurityControl]]:
        """
        Find matching implementation and security control for a control ID.

        :param str control_id: Control identifier to match
        :param List[ControlImplementation] implementations: Available implementations
        :return: Tuple of matching implementation and security control, or (None, None)
        :rtype: tuple[Optional[ControlImplementation], Optional[SecurityControl]]
        """
        matching_implementation = None
        matching_security_control = None
        for implementation in implementations:
            try:
                security_control = SecurityControl.get_object(object_id=implementation.controlID)
                if not security_control:
                    logger.debug(
                        f"No security control found for implementation {implementation.id} with controlID: {implementation.controlID}"
                    )
                    continue
                security_control_id = security_control.controlId
                if not security_control_id:
                    logger.debug(f"Security control {security_control.id} has no controlId")
                    continue
                logger.debug(
                    f"Comparing extracted '{control_id}' with RegScale control '{security_control_id}' (impl: {implementation.id})"
                )
                if self._control_ids_match(control_id, security_control_id):
                    matching_implementation = implementation
                    matching_security_control = security_control
                    logger.info(
                        f"✅ MATCH FOUND: '{security_control_id}' == '{control_id}' (implementation: {implementation.id})"
                    )
                    break
            except Exception as e:  # noqa: BLE001
                logger.error(
                    f"Error processing implementation {implementation.id} with controlID {implementation.controlID}: {e}"
                )
                continue
        return matching_implementation, matching_security_control

    def _log_no_match(self, control_id: str, implementations: List[ControlImplementation]) -> None:
        """
        Log when no matching implementation is found for a control.

        :param str control_id: Control identifier that couldn't be matched
        :param List[ControlImplementation] implementations: Available implementations for context
        :return: None
        :rtype: None
        """
        logger.warning(f"No matching implementation found for control ID '{control_id}'")
        sample_impl_controls = []
        for impl in implementations[:5]:
            try:
                sec_control = SecurityControl.get_object(object_id=impl.controlID)
                if sec_control and sec_control.controlId:
                    sample_impl_controls.append(f"{sec_control.controlId} (impl:{impl.id})")
            except Exception:
                sample_impl_controls.append(f"Unknown (impl:{impl.id})")
        logger.debug(f"Sample implementation control IDs (first 5): {sample_impl_controls}")

    def _determine_overall_result(self, control_id: str) -> str:
        """
        Determine overall assessment result for a control.

        :param str control_id: Control identifier to check
        :return: Assessment result ('Pass' or 'Fail')
        :rtype: str
        """
        is_failing = (
            control_id in self.failing_controls
            or control_id.lower() in self.failing_controls
            or control_id.upper() in self.failing_controls
        )
        return "Fail" if is_failing else "Pass"

    def _get_control_compliance_items(self, control_id: str) -> List[ComplianceItem]:
        """
        Get all compliance items for a specific control.

        :param str control_id: Control identifier to filter by
        :return: List of compliance items for the control
        :rtype: List[ComplianceItem]
        """
        items: List[ComplianceItem] = []
        for item in self.all_compliance_items:
            if hasattr(item, "control_ids"):
                item_control_ids = getattr(item, "control_ids", [])
                if any(cid.lower() == control_id.lower() for cid in item_control_ids):
                    items.append(item)
            elif hasattr(item, "control_id") and item.control_id.lower() == control_id.lower():
                items.append(item)
        return items

    def _record_control_mapping(self, control_id: str, implementation_id: int) -> None:
        """
        Record mapping between normalized control ID and implementation ID.

        :param str control_id: Control identifier to map
        :param int implementation_id: Implementation ID to associate
        :return: None
        :rtype: None
        """
        try:
            base, sub = self._normalize_control_id(control_id)
            canonical = f"{base}({sub})" if sub else base
            self._impl_id_by_control[canonical] = implementation_id
            logger.debug(f"Mapped control '{canonical}' -> implementation ID {implementation_id}")
        except Exception:
            pass

    def _map_assets_to_control_component(self, sec_control: SecurityControl, items: List[ComplianceItem]) -> None:
        """
        Map assets to control-specific components for organization.

        :param SecurityControl sec_control: Security control to create component for
        :param List[ComplianceItem] items: Compliance items with asset references
        :return: None
        :rtype: None
        """
        try:
            component_title = f"Control {sec_control.controlId}"
            component = self.components_by_title.get(component_title) if hasattr(self, "components_by_title") else None
            if not component:
                component = regscale_models.Component(
                    title=component_title,
                    componentType=regscale_models.ComponentType.Hardware,
                    securityPlansId=self.plan_id,
                    description=component_title,
                    componentOwnerId=self.get_assessor_id(),
                ).get_or_create()
                regscale_models.ComponentMapping(
                    componentId=component.id,
                    securityPlanId=self.plan_id,
                ).get_or_create()
                if hasattr(self, "components_by_title"):
                    self.components_by_title[component_title] = component

            for item in items:
                asset = self.get_asset_by_identifier(getattr(item, "resource_id", ""))
                if not asset:
                    continue
                regscale_models.AssetMapping(
                    assetId=asset.id,
                    componentId=component.id,
                ).get_or_create_with_status()
        except Exception as map_exc:  # noqa: BLE001
            logger.debug(f"Control-to-asset mapping skipped due to: {map_exc}")

    @staticmethod
    def _parse_control_id(control_id: str) -> tuple[str, Optional[str]]:
        """
        Parse a control id like 'AC-2(1)', 'AC-2 (1)', 'AC-2-1' into (base, sub).

        Returns (base, None) when no subcontrol.

        :param str control_id: Control identifier to parse
        :return: Tuple of (base_control, subcontrol) where subcontrol may be None
        :rtype: tuple[str, Optional[str]]
        """
        cid = control_id.strip()
        # Use precompiled safe regex to avoid catastrophic backtracking on crafted input
        m = SAFE_CONTROL_ID_RE.match(cid)
        if not m:
            return cid.upper(), None
        base = m.group(1).upper()
        # Subcontrol may be captured in group 2, 3, or 4 depending on the branch matched
        sub = m.group(2) or m.group(3) or m.group(4)
        return base, sub

    @classmethod
    def _control_ids_match(cls, a: str, b: str) -> bool:
        """
        Strict match of control ids. Exact match if equal.
        If subcontrols exist on either side, both must exist and be equal.

        :param str a: First control ID to compare
        :param str b: Second control ID to compare
        :return: True if control IDs match according to strict rules
        :rtype: bool
        """
        if not a or not b:
            return False
        if a.strip().lower() == b.strip().lower():
            return True
        base_a, sub_a = cls._parse_control_id(a)
        base_b, sub_b = cls._parse_control_id(b)
        if base_a != base_b:
            return False
        # If either has a subcontrol, require both and equality
        if sub_a or sub_b:
            return (sub_a is not None) and (sub_b is not None) and (sub_a == sub_b)
        # No subcontrols -> base equals
        return True

    @staticmethod
    def _normalize_control_id(control_id: str) -> tuple[str, Optional[str]]:
        """
        Normalize control id to a canonical tuple (BASE, SUB) for set membership.

        :param str control_id: Control identifier to normalize
        :return: Tuple of (base_control, subcontrol) in canonical form
        :rtype: tuple[str, Optional[str]]
        """
        cid = (control_id or "").strip()
        # Use precompiled safe regex to avoid catastrophic backtracking on crafted input
        m = SAFE_CONTROL_ID_RE.match(cid)
        if not m:
            return cid.upper(), None
        base = m.group(1).upper()
        sub = m.group(2) or m.group(3) or m.group(4)
        return base, sub

    def _create_control_assessment(
        self,
        implementation: ControlImplementation,
        catalog_control: Dict,
        result: str,
        control_id: str,
        compliance_items: List[ComplianceItem] = None,
    ) -> None:
        """
        Create or update an assessment for a control implementation.
        If an assessment for the same day exists, update it instead of creating a duplicate.

        :param ControlImplementation implementation: The control implementation to assess
        :param Dict catalog_control: The catalog control data dictionary
        :param str result: Assessment result ('Pass' or 'Fail')
        :param str control_id: Control identifier string
        :param List[ComplianceItem] compliance_items: Pre-aggregated compliance items for this control
        :return: None
        :rtype: None
        """
        try:
            # Use provided compliance items or get them for this control (backward compatibility)
            if compliance_items is None:
                compliance_items = []
                if (
                    control_id in self.failing_controls
                    or control_id.lower() in self.failing_controls
                    or control_id.upper() in self.failing_controls
                ):
                    compliance_items = [
                        item for item in self.failed_compliance_items if item.control_id.lower() == control_id.lower()
                    ]
                else:
                    compliance_items = [
                        item for item in self.all_compliance_items if item.control_id.lower() == control_id.lower()
                    ]

            # Create assessment report
            assessment_report = self._create_assessment_report(control_id, result, compliance_items)

            # Check for existing assessment on the same day using cache
            existing_assessment = self._find_existing_assessment_cached(implementation.id, self.scan_date)

            if existing_assessment:
                # Update existing assessment
                existing_assessment.assessmentResult = result
                existing_assessment.assessmentReport = assessment_report
                existing_assessment.actualFinish = get_current_datetime()
                existing_assessment.dateLastUpdated = get_current_datetime()
                existing_assessment.save()
                logger.debug(f"Updated existing assessment {existing_assessment.id} for control {control_id}")
                # Refresh cache for today
                try:
                    day_key = regscale_string_to_datetime(self.scan_date).date().isoformat()
                except Exception:
                    day_key = str(self.scan_date).split(" ")[0]
                self._existing_assessments_cache[f"{implementation.id}_{day_key}"] = existing_assessment
                # Track today's assessment by implementation id for linking to issues later
                try:
                    self._assessment_by_impl_today[implementation.id] = existing_assessment
                except Exception:
                    pass
            else:
                # Create new assessment
                assessment = Assessment(
                    leadAssessorId=implementation.createdById,
                    title=f"{self.title} compliance assessment for {control_id.upper()}",
                    assessmentType="Control Testing",
                    plannedStart=get_current_datetime(),
                    plannedFinish=get_current_datetime(),
                    actualFinish=get_current_datetime(),
                    assessmentResult=result,
                    assessmentReport=assessment_report,
                    status="Complete",
                    parentId=implementation.id,
                    parentModule="controls",
                    isPublic=True,
                ).create()
                logger.debug(f"Created new assessment {assessment.id} for control {control_id}")
                # Add to cache for today to prevent duplicate creation in subsequent processing
                try:
                    day_key = regscale_string_to_datetime(self.scan_date).date().isoformat()
                except Exception:
                    day_key = str(self.scan_date).split(" ")[0]
                self._existing_assessments_cache[f"{implementation.id}_{day_key}"] = assessment
                # Track today's assessment by implementation id for linking to issues later
                try:
                    self._assessment_by_impl_today[implementation.id] = assessment
                except Exception:
                    pass

            # Update implementation status if needed
            if self.update_control_status:
                self._update_implementation_status(implementation, result)

        except Exception as e:
            logger.error(f"Error creating control assessment: {e}")

    def _find_existing_assessment(self, implementation: ControlImplementation, scan_date) -> Optional:
        """
        Find existing assessment for the same implementation on the same day.
        DEPRECATED: Use _find_existing_assessment_cached instead.

        :param ControlImplementation implementation: The control implementation
        :param scan_date: The scan date to check
        :return: Existing assessment or None
        :rtype: Optional[regscale_models.Assessment]
        """
        logger.warning("_find_existing_assessment is deprecated, use _find_existing_assessment_cached")
        return self._find_existing_assessment_cached(implementation.id, scan_date)

    def _create_assessment_report(self, control_id: str, result: str, compliance_items: List[ComplianceItem]) -> str:
        """
        Create HTML assessment report.

        :param str control_id: Control identifier
        :param str result: Assessment result ('Pass' or 'Fail')
        :param List[ComplianceItem] compliance_items: Compliance items for this control
        :return: Formatted HTML report string
        :rtype: str
        """
        result_color = "#d32f2f" if result == "Fail" else "#2e7d32"

        html_parts = [
            f"""
            <div style="margin-bottom: 20px; padding: 15px; border: 2px solid {result_color};
                        border-radius: 5px; background-color: {'#ffebee' if result == 'Fail' else '#e8f5e8'};">
                <h3 style="margin: 0 0 10px 0; color: {result_color};">
                    {self.title} Compliance Assessment for Control {control_id.upper()}
                </h3>
                <p><strong>Overall Result:</strong>
                   <span style="color: {result_color}; font-weight: bold;">{result}</span></p>
                <p><strong>Assessment Date:</strong> {self.scan_date}</p>
                <p><strong>Framework:</strong> {self.framework}</p>
                <p><strong>Total Policy Assessments:</strong> {len(compliance_items)}</p>
            </div>
            """
        ]  # NOSONAR

        if compliance_items:
            # Group by result for summary
            pass_count = len([item for item in compliance_items if item.compliance_result in self.PASS_STATUSES])
            fail_count = len(compliance_items) - pass_count

            # Count unique resources across all policy assessments for this control
            unique_resources = set()
            unique_policies = set()

            for item in compliance_items:
                unique_resources.add(item.resource_id)
                # Get policy name for aggregation
                if hasattr(item, "description"):
                    unique_policies.add(
                        item.description[:50] + "..." if len(item.description) > 50 else item.description
                    )
                elif hasattr(item, "policy") and isinstance(item.policy, dict):
                    policy_name = item.policy.get("name", "Unknown Policy")
                    unique_policies.add(policy_name[:50] + "..." if len(policy_name) > 50 else policy_name)

            html_parts.append(
                f"""
            <div style="margin-top: 20px;">
                <h4>Aggregated Assessment Summary</h4>
                <p><strong>Policy Assessments:</strong> {len(compliance_items)} total</p>
                <p><strong>Unique Policies Tested:</strong> {len(unique_policies)}</p>
                <p><strong>Unique Resources Assessed:</strong> {len(unique_resources)}</p>
                <p><strong>Passing Assessments:</strong> <span style="color: #2e7d32;">{pass_count}</span></p>
                <p><strong>Failing Assessments:</strong> <span style="color: #d32f2f;">{fail_count}</span></p>
                <p><strong>Overall Control Result:</strong> <span style="color: {result_color}; font-weight: bold;">{result}</span></p>
            </div>
             """
            )

        return "\n".join(html_parts)

    def _update_implementation_status(self, implementation: ControlImplementation, result: str) -> None:
        """
        Update control implementation status based on assessment result.

        :param ControlImplementation implementation: Control implementation to update
        :param str result: Assessment result ('Pass' or 'Fail')
        :return: None
        :rtype: None
        """
        try:
            if result == "Pass":
                new_status = "Fully Implemented"
            else:
                new_status = "In Remediation"

            # Update implementation status
            implementation.status = new_status
            implementation.dateLastAssessed = get_current_datetime()
            implementation.lastAssessmentResult = result
            implementation.save()

            # Update objectives if they exist
            objectives = ImplementationObjective.get_all_by_parent(
                parent_module=implementation.get_module_slug(),
                parent_id=implementation.id,
            )

            for objective in objectives:
                objective.status = new_status
                objective.save()

            logger.debug(f"Updated implementation status to {new_status}")

        except Exception as e:
            logger.error(f"Error updating implementation status: {e}")

    def _get_controls(self) -> List[Dict]:
        """
        Get controls from catalog or plan.

        :return: List of control dictionaries from catalog or plan
        :rtype: List[Dict]
        """
        if self.catalog_id:
            catalog = Catalog.get_with_all_details(catalog_id=self.catalog_id)
            return catalog.get("controls", []) if catalog else []
        else:
            return SecurityControl.get_controls_by_parent_id_and_module(
                parent_module=self.parent_module, parent_id=self.plan_id, return_dicts=True
            )

    def _find_existing_asset_by_resource_id(self, resource_id: str) -> Optional[regscale_models.Asset]:
        """
        Find existing asset by resource ID.

        :param str resource_id: Resource identifier to search for
        :return: Existing asset or None if not found
        :rtype: Optional[regscale_models.Asset]
        """
        try:
            if hasattr(self, "asset_map_by_identifier") and self.asset_map_by_identifier:
                return self.asset_map_by_identifier.get(resource_id)

            # Query database
            existing_assets = regscale_models.Asset.get_all_by_parent(
                parent_id=self.plan_id,
                parent_module=self.parent_module,
            )

            for asset in existing_assets:
                if hasattr(asset, "otherTrackingNumber") and asset.otherTrackingNumber == resource_id:
                    return asset

            return None

        except Exception as e:
            logger.error(f"Error finding existing asset: {e}")
            return None

    def _map_resource_type_to_asset_type(self, compliance_item: ComplianceItem) -> str:
        """
        Map compliance item resource type to RegScale asset type.

        :param ComplianceItem compliance_item: Compliance item with resource type information
        :return: Asset type string suitable for RegScale
        :rtype: str
        """
        # Default implementation - can be overridden by subclasses
        return "Cloud Resource"

    def _map_severity(self, severity: Optional[str]) -> regscale_models.IssueSeverity:
        """
        Map compliance severity to RegScale severity.

        :param Optional[str] severity: Severity string from compliance source
        :return: Mapped RegScale severity enum value
        :rtype: regscale_models.IssueSeverity
        """
        if not severity:
            return regscale_models.IssueSeverity.Moderate

        severity_mapping = {
            "CRITICAL": regscale_models.IssueSeverity.Critical,
            "HIGH": regscale_models.IssueSeverity.High,
            "MEDIUM": regscale_models.IssueSeverity.Moderate,
            "LOW": regscale_models.IssueSeverity.Low,
        }

        return severity_mapping.get(severity.upper(), regscale_models.IssueSeverity.Moderate)

    def _map_severity_to_priority(self, severity: regscale_models.IssueSeverity) -> str:
        """
        Map severity to priority string.

        :param regscale_models.IssueSeverity severity: Issue severity enum value
        :return: Priority string for issues
        :rtype: str
        """
        priority_mapping = {
            regscale_models.IssueSeverity.Critical: "Critical",
            regscale_models.IssueSeverity.High: "High",
            regscale_models.IssueSeverity.Moderate: "Medium",
            regscale_models.IssueSeverity.Low: "Low",
        }

        return priority_mapping.get(severity, "Medium")

    def _update_scan_history(self, scan_history: regscale_models.ScanHistory) -> None:
        """
        Update scan history with results.

        :param regscale_models.ScanHistory scan_history: Scan history record to update
        :return: None
        :rtype: None
        """
        try:
            scan_history.dateLastUpdated = get_current_datetime()
            scan_history.save()
            logger.debug(f"Updated scan history {scan_history.id}")
        except Exception as e:
            logger.error(f"Error updating scan history: {e}")

    def create_scan_history(self) -> regscale_models.ScanHistory:
        """
        Create or reuse a ScanHistory for the same day and tool.

        If a scan history exists for this plan/module with the same
        scanning tool and scan date (day-level), update and reuse it
        instead of creating a duplicate.

        :return: Created or reused scan history record
        :rtype: regscale_models.ScanHistory
        """
        try:
            # Load existing scans for the plan/module
            existing_scans = regscale_models.ScanHistory.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            # Normalize target date to date component only
            target_dt = self.scan_date
            target_date_only = target_dt.split("T")[0] if isinstance(target_dt, str) else str(target_dt)[:10]

            # Find an existing scan for today and this tool
            for scan in existing_scans:
                try:
                    if getattr(scan, "scanningTool", None) == self.title and getattr(scan, "scanDate", None):
                        scan_date = str(scan.scanDate)
                        scan_date_only = scan_date.split("T")[0]
                        if scan_date_only == target_date_only:
                            # Reuse this scan history; refresh last updated
                            scan.dateLastUpdated = get_current_datetime()
                            scan.save()
                            return scan
                except Exception:
                    # Skip any malformed scan records
                    continue

            # No existing same-day scan found, create new via base behavior
            return super().create_scan_history()
        except Exception:
            # Fallback: create new scan history
            return super().create_scan_history()

    def create_or_update_issue_from_finding(self, title: str, finding: IntegrationFinding) -> regscale_models.Issue:
        """
        Create or update an issue from a finding, using cache to prevent duplicates.

        :param str title: Issue title
        :param IntegrationFinding finding: The finding to create issue from
        :return: Created or updated issue
        :rtype: regscale_models.Issue
        """
        # Load cache if not already loaded
        self._load_existing_records_cache()

        # Check for existing issue by external_id first
        external_id = finding.external_id
        existing_issue = self._find_existing_issue_cached(external_id)

        if existing_issue:
            logger.debug(
                f"Found existing issue {existing_issue.id} for external_id {external_id}, updating instead of creating"
            )

            # Update existing issue with new finding data
            existing_issue.title = title
            existing_issue.description = finding.description
            existing_issue.severity = finding.severity
            existing_issue.status = finding.status
            # Ensure affectedControls is updated from the finding's control id
            try:
                if getattr(finding, "control_labels", None):
                    existing_issue.affectedControls = ",".join(finding.control_labels)
                else:
                    # Fall back to normalized control id from rule_id/control_labels
                    ctl = None
                    if getattr(finding, "rule_id", None):
                        ctl = finding.rule_id
                    elif getattr(finding, "control_labels", None):
                        labels = list(finding.control_labels)
                        ctl = labels[0] if labels else None
                    if ctl:
                        base, sub = self._normalize_control_id(ctl)
                        existing_issue.affectedControls = f"{base}({sub})" if sub else base
            except Exception:
                pass
            existing_issue.dateLastUpdated = self.scan_date
            existing_issue.save()

            return existing_issue
        else:
            # No existing issue found, create new one using parent method
            logger.debug(f"No existing issue found for external_id {external_id}, creating new issue")
            return super().create_or_update_issue_from_finding(title, finding)
