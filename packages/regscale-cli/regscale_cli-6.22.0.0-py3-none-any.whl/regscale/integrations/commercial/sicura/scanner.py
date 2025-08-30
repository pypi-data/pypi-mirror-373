#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RegScale Sicura Integration
"""
import datetime
from typing import Generator, Iterator, Any

from regscale.core.utils.date import date_str
from regscale.integrations.commercial.sicura.api import SicuraAPI, ScanReport, SicuraProfile, Device, ScanResult
from regscale.integrations.scanner_integration import (
    logger,
    IntegrationFinding,
    ScannerIntegration,
    IntegrationAsset,
    ScannerIntegrationType,
    issue_due_date,
)
from regscale.models import regscale_models
from regscale.models.regscale_models import AssetType


class SicuraIntegration(ScannerIntegration):
    """
    Sicura Integration for RegScale

    This integration fetches assets and scan findings from Sicura
    """

    options_map_assets_to_components = True
    import_closed_findings = False

    title = "Sicura"
    type = ScannerIntegrationType.CHECKLIST

    # Map Sicura scan result states to RegScale checklist statuses
    checklist_status_map = {
        "pass": regscale_models.ChecklistStatus.PASS,
        "fail": regscale_models.ChecklistStatus.FAIL,
    }

    # Map severity levels
    finding_severity_map = {
        "high": regscale_models.IssueSeverity.High,
        "medium": regscale_models.IssueSeverity.Moderate,
        "low": regscale_models.IssueSeverity.Low,
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the Sicura Integration

        :param args: Arguments to pass to the parent class
        :param kwargs: Keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.api = SicuraAPI()

    def fetch_findings(self, **kwargs) -> Generator[IntegrationFinding, None, None]:
        """
        Fetches findings from Sicura API

        :param kwargs: Additional arguments
        :yields: IntegrationFinding objects
        :return: Generator of IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        logger.info("Fetching findings from Sicura...")

        # Get all devices
        devices = kwargs.get("devices", self.api.get_devices())

        if not devices:
            logger.warning("No devices found in Sicura")
            return

        self.num_findings_to_process = 0
        findings_count = 0

        # Process each device
        for device in devices:
            for finding in self._process_device_findings(device):
                findings_count += 1
                yield finding

        self.num_findings_to_process = findings_count

    def _process_device_findings(self, device: Device) -> Generator[IntegrationFinding, None, None]:
        """
        Process findings for a single device

        :param Device device: The device to process
        :yield: IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        logger.info(f"Fetching scan results for device: {device.fqdn}")
        if not device.fqdn:
            logger.warning(f"Device {device.name} has no FQDN, skipping")
            return

        # Profiles to scan
        profiles = [SicuraProfile.I_MISSION_CRITICAL_CLASSIFIED, SicuraProfile.LEVEL_1_SERVER]

        for profile in profiles:
            yield from self._process_profile_findings(device, profile)

    def _process_profile_findings(
        self, device: Device, profile: SicuraProfile
    ) -> Generator[IntegrationFinding, None, None]:
        """
        Process findings for a device with a specific profile

        :param Device device: The device to process
        :param SicuraProfile profile: The profile to process
        :yield: IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        scan_report = self.api.get_scan_results(fqdn=device.fqdn, profile=profile)

        if not scan_report:
            logger.warning(f"No scan results found for device: {device.fqdn} with profile: {profile}")
            return

        # Process scan results based on the report type
        if isinstance(scan_report, ScanReport):
            yield from self._process_scan_report_findings(device, scan_report.scans)
        elif isinstance(scan_report, dict) and scan_report.get("scans"):
            yield from self._process_scan_report_findings(device, scan_report.get("scans", []))

    def _process_scan_report_findings(self, device: Device, scans: list) -> Generator[IntegrationFinding, None, None]:
        """
        Process findings from a scan report

        :param Device device: The device being scanned
        :param list scans: The list of scans to process
        :yield: IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        for scan in scans:
            yield from self.parse_finding(device, scan)

    def parse_finding(
        self,
        device: Device,
        scan: Any,
    ) -> Generator[IntegrationFinding, None, None]:
        """
        Creates and yields IntegrationFinding objects from Sicura scan results, one per CCI reference

        :param Device device: The device object
        :param Any scan: The scan data
        :yield: IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        # Extract basic information from device and scan
        asset_identifier = device.fqdn
        platform = device.platforms

        # Extract scan data
        scan_data = self._extract_scan_data(scan)
        title = scan_data["title"]
        ce_name = scan_data["ce_name"]
        result = scan_data["result"]
        description = scan_data["description"]
        state = scan_data["state"]
        state_reason = scan_data["state_reason"]
        controls = scan_data["controls"]

        # Extract control references
        cci_refs, srg_refs = self._extract_control_refs(controls)

        # Determine severity and due date
        severity = self._determine_severity(title)
        created_date = date_str(datetime.datetime.now())
        due_date = issue_due_date(severity, created_date, title=self.title)

        # Common mitigation recommendation
        mitigation = f"Fix the issues identified: {', '.join(state_reason) if state_reason else 'See description'}"

        # If no CCI references, use empty string as the only CCI ref
        if not cci_refs:
            cci_refs = [""]

        # Create a finding for each CCI reference
        for cci_ref in cci_refs:
            # Create a ScanResult object to hold the scan data
            scan_result = ScanResult(
                title=title,
                ce_name=ce_name,
                result=result,
                description=description,
                state=state,
                state_reason=state_reason,
                controls=controls,
            )

            yield from self._create_finding_for_cci(
                asset_identifier=asset_identifier,
                platform=platform,
                cci_ref=cci_ref,
                scan_result=scan_result,
                srg_refs=srg_refs,
                severity=severity,
                created_date=created_date,
                due_date=due_date,
                mitigation=mitigation,
            )

    def _extract_scan_data(self, scan: Any) -> dict:
        """
        Extract scan data from the scan object

        :param Any scan: The scan object
        :return: Dictionary with scan data
        :rtype: dict
        """
        if isinstance(scan, dict):
            return {
                "title": scan.get("title", ""),
                "ce_name": scan.get("ce_name", ""),
                "result": scan.get("result", ""),
                "description": scan.get("description", ""),
                "state": scan.get("state", ""),
                "state_reason": scan.get("state_reason", []),
                "controls": scan.get("controls", {}),
            }
        else:
            return {
                "title": scan.title,
                "ce_name": scan.ce_name,
                "result": scan.result,
                "description": scan.description,
                "state": scan.state,
                "state_reason": scan.state_reason,
                "controls": scan.controls if hasattr(scan, "controls") else {},
            }

    def _extract_control_refs(self, controls: dict) -> tuple:
        """
        Extract CCI and SRG references from controls

        :param dict controls: The controls dictionary
        :return: Tuple of (cci_refs, srg_refs)
        :rtype: tuple
        """
        cci_refs = []
        srg_refs = []

        for control_key, control_value in controls.items():
            if control_key.startswith("cci:"):
                # Extract CCI number (e.g., "cci:CCI-000366" -> "CCI-000366")
                cci_ref = control_key.split(":", 1)[1] if ":" in control_key else control_key
                cci_refs.append(cci_ref)
            elif control_key.startswith("SRG-"):
                srg_refs.append(control_key)

        return cci_refs, srg_refs

    def _determine_severity(self, title: str) -> regscale_models.IssueSeverity:
        """
        Determine severity based on title

        :param str title: The finding title
        :return: Severity enum value
        :rtype: regscale_models.IssueSeverity
        """
        severity_text = "medium"
        if "critical" in title.lower() or "cat i" in title.lower():
            severity_text = "high"
        elif "low" in title.lower() or "cat iii" in title.lower():
            severity_text = "low"

        return self.get_finding_severity(severity_text)

    def _create_finding_for_cci(
        self,
        asset_identifier,
        platform,
        cci_ref,
        scan_result: ScanResult,
        srg_refs,
        severity,
        created_date,
        due_date,
        mitigation,
    ) -> Generator[IntegrationFinding, None, None]:
        """
        Create a finding for a single CCI reference

        :param str asset_identifier: The asset identifier
        :param str platform: The platform
        :param str cci_ref: The CCI reference
        :param ScanResult scan_result: The scan result data
        :param list srg_refs: The SRG references
        :param regscale_models.IssueSeverity severity: The severity
        :param str created_date: The created date
        :param str due_date: The due date
        :param str mitigation: The mitigation
        :yield: IntegrationFinding objects
        :rtype: Generator[IntegrationFinding, None, None]
        """
        # Determine if this is a CCI finding or a regular finding
        is_cci_finding = cci_ref != ""

        # Extract values from scan_result
        title = scan_result.title
        ce_name = scan_result.ce_name
        result = scan_result.result
        description = scan_result.description
        state = scan_result.state
        state_reason = scan_result.state_reason

        # Set title based on whether it's a CCI finding
        finding_title = title if not is_cci_finding else f"{title} (CCI: {cci_ref})"

        # Create results text
        results = self._create_results_text(
            title, ce_name, result, description, state, state_reason, cci_ref, srg_refs, is_cci_finding
        )

        # Create external ID
        external_id = (
            f"{ce_name}:{asset_identifier}" if not is_cci_finding else f"{ce_name}:{cci_ref}:{asset_identifier}"
        )

        # Create and yield the finding
        yield IntegrationFinding(
            asset_identifier=asset_identifier,
            control_labels=[],  # Empty list as controls will be mapped via other mechanisms
            title=finding_title,
            issue_title=finding_title,
            category=ce_name,
            severity=severity,
            description=description,
            status=regscale_models.IssueStatus.Open if result == "fail" else regscale_models.IssueStatus.Closed,
            checklist_status=self.get_checklist_status(result),
            external_id=external_id,
            vulnerability_number=ce_name,
            cci_ref=cci_ref,
            rule_id=ce_name,
            rule_version="1.0",
            results=results,
            recommendation_for_mitigation=mitigation,
            comments="",
            poam_comments="",
            date_created=created_date,
            due_date=due_date,
            plugin_name=ce_name,
            observations=f"Result: {result}, State: {state}",
            gaps=description,
            evidence=f"State reasons: {', '.join(state_reason) if state_reason else 'N/A'}",
            impact="Security compliance impact",
            baseline=platform,
        )

    def _create_results_text(
        self, title, ce_name, result, description, state, state_reason, cci_ref, srg_refs, is_cci_finding
    ) -> str:
        """
        Create the results text for a finding

        :param str title: The finding title
        :param str ce_name: The CE name
        :param str result: The result
        :param str description: The description
        :param str state: The state
        :param list state_reason: The state reason
        :param str cci_ref: The CCI reference
        :param list srg_refs: The SRG references
        :param bool is_cci_finding: Whether this is a CCI finding
        :return: The results text
        :rtype: str
        """
        # Create the results text with conditional CCI reference section
        results_parts = [
            f"Title: {title}",
            f"Check: {ce_name}",
            f"Result: {result}",
            f"Description: {description}",
            f"State: {state}",
            f"State Reason: {', '.join(state_reason) if state_reason else 'N/A'}",
        ]

        # Add CCI reference only if it exists
        if is_cci_finding:
            results_parts.append(f"CCI Reference: {cci_ref}")

        # Always add SRG references
        results_parts.append(f"SRG References: {', '.join(srg_refs)}")

        # Join all parts with newlines
        return "\n".join(results_parts)

    def fetch_assets(self, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from Sicura API

        :param kwargs: Additional arguments
        :yield: IntegrationAsset objects
        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        logger.info("Fetching assets from Sicura...")

        # Get all devices
        pending_devices = self.api.get_pending_devices()
        for pending_device in pending_devices:
            print(f"Pending device: {pending_device}")
            self.api.accept_pending_device(pending_device.id)
            task_id = self.api.create_scan_task(
                device_id=pending_device.id,
                platform=pending_device.platform,
                profile=SicuraProfile.I_MISSION_CRITICAL_CLASSIFIED,
            )
            if task_id:
                self.api.wait_for_scan_results(
                    task_id=task_id,
                    fqdn=pending_device.fqdn,
                    platform=pending_device.platform,
                    profile=SicuraProfile.I_MISSION_CRITICAL_CLASSIFIED,
                )
            else:
                logger.warning(f"Failed to create scan task for device {pending_device.fqdn}")
                continue  # Continue to next device if creating scan task failed

            task_id = self.api.create_scan_task(
                device_id=pending_device.id, platform=pending_device.platform, profile=SicuraProfile.LEVEL_1_SERVER
            )
            if task_id:
                self.api.wait_for_scan_results(
                    task_id=task_id,
                    fqdn=pending_device.fqdn,
                    platform=pending_device.platform,
                    profile=SicuraProfile.LEVEL_1_SERVER,
                )
            else:
                logger.warning(f"Failed to create scan task for device {pending_device.fqdn}")
                # No continue needed here as we're at the end of the loop iteration

        devices = self.api.get_devices()

        if not devices:
            logger.warning("No devices found in Sicura")
            return

        self.num_assets_to_process = len(devices)

        loading_devices = self.asset_progress.add_task(
            f"[#f8b737]Loading {len(devices)} Sicura devices.",
            total=len(devices),
        )

        for device in devices:
            # Skip devices without an FQDN
            if not device.fqdn:
                logger.warning(f"Device {device.name} has no FQDN, skipping")
                self.asset_progress.update(loading_devices, advance=1)
                continue

            # Extract platform as the component name if available
            component_names = []
            if device.platforms:
                component_names.append(device.platforms)

            # Create an asset from the device information
            yield IntegrationAsset(
                name=device.name,
                identifier=device.fqdn,
                asset_type=AssetType.VM,  # Default to server type
                ip_address=device.ip_address,
                fqdn=device.fqdn,
                asset_owner_id=self.assessor_id,
                parent_id=self.plan_id,
                parent_module=regscale_models.SecurityPlan.get_module_slug(),
                asset_category=regscale_models.AssetCategory.Hardware,
                component_names=component_names,
                component_type=regscale_models.ComponentType.Hardware,
                external_id=str(device.id) if device.id else None,
            )

            self.asset_progress.update(loading_devices, advance=1)
