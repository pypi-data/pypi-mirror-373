#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper classes and utilities for Wiz Policy Compliance Integration."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

from regscale.core.app.utils.app_utils import get_current_datetime, regscale_string_to_datetime
from regscale.integrations.scanner_integration import IntegrationFinding
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


@dataclass
class ControlAssessmentResult:
    """Result of a control assessment operation."""

    control_id: str
    implementation_id: Optional[int]
    assessment_id: Optional[int]
    result: str
    asset_count: int
    created: bool = False


@dataclass
class IssueProcessingResult:
    """Result of issue processing operation."""

    control_id: Optional[str]
    implementation_id: Optional[int]
    assessment_id: Optional[int]
    success: bool
    error_message: Optional[str] = None


class ControlImplementationCache:
    """Cache for control implementation lookups to avoid repeated database queries."""

    def __init__(self) -> None:
        self._impl_id_by_control: Dict[str, int] = {}
        self._assessment_by_impl_today: Dict[int, regscale_models.Assessment] = {}
        self._security_control_cache: Dict[int, regscale_models.SecurityControl] = {}
        self._loaded = False

    def get_implementation_id(self, control_id: str) -> Optional[int]:
        """
        Get control implementation ID for normalized control ID.

        :param control_id: Normalized control ID (e.g., 'AC-2(1)')
        :return: Control implementation ID if found, None otherwise
        """
        return self._impl_id_by_control.get(control_id)

    def set_implementation_id(self, control_id: str, impl_id: int) -> None:
        """
        Cache control implementation ID.

        :param control_id: Normalized control ID (e.g., 'AC-2(1)')
        :param impl_id: Control implementation ID to cache
        """
        self._impl_id_by_control[control_id] = impl_id

    def get_assessment(self, impl_id: int) -> Optional[regscale_models.Assessment]:
        """
        Get assessment for implementation ID.

        :param impl_id: Control implementation ID
        :return: Cached assessment object if found, None otherwise
        """
        return self._assessment_by_impl_today.get(impl_id)

    def set_assessment(self, impl_id: int, assessment: regscale_models.Assessment) -> None:
        """
        Cache assessment for implementation.

        :param impl_id: Control implementation ID
        :param assessment: Assessment object to cache
        """
        self._assessment_by_impl_today[impl_id] = assessment

    def get_security_control(self, control_id: int) -> Optional[regscale_models.SecurityControl]:
        """
        Get cached security control.

        :param control_id: Security control ID
        :return: Cached security control object if found, None otherwise
        """
        return self._security_control_cache.get(control_id)

    def set_security_control(self, control_id: int, security_control: regscale_models.SecurityControl) -> None:
        """
        Cache security control.

        :param control_id: Security control ID
        :param security_control: Security control object to cache
        """
        self._security_control_cache[control_id] = security_control

    @property
    def implementation_count(self) -> int:
        """
        Number of cached implementations.

        :return: Count of cached control implementation mappings
        """
        return len(self._impl_id_by_control)

    @property
    def assessment_count(self) -> int:
        """
        Number of cached assessments.

        :return: Count of cached assessment objects
        """
        return len(self._assessment_by_impl_today)


class AssetConsolidator:
    """Handles consolidation of asset identifiers for findings."""

    MAX_DISPLAY_ASSETS = 10

    @staticmethod
    def create_consolidated_asset_identifier(asset_mappings: Dict[str, Dict[str, str]]) -> str:
        """
        Create a consolidated asset identifier from asset mappings.

        :param asset_mappings: Dict mapping resource IDs to asset info
        :return: Consolidated asset identifier string
        """
        if not asset_mappings:
            return ""

        # Create clean format: "Asset Name (wiz-resource-id)"
        identifiers = []
        for resource_id, info in asset_mappings.items():
            asset_name = info.get("name", resource_id)
            identifier = f"{asset_name} ({resource_id})"
            identifiers.append(identifier)

        # Sort by asset name for consistency
        identifiers.sort(key=lambda x: x.split(" (")[0])

        return "\n".join(identifiers)

    @staticmethod
    def update_finding_description_for_multiple_assets(
        finding: IntegrationFinding, asset_count: int, asset_names: List[str]
    ) -> None:
        """
        Update finding description to indicate multiple affected assets.

        :param finding: Finding to update
        :param asset_count: Number of affected assets
        :param asset_names: List of asset names
        """
        if asset_count <= 1:
            return

        display_names = asset_names[: AssetConsolidator.MAX_DISPLAY_ASSETS]
        description_suffix = f"\n\nThis control failure affects {asset_count} assets: {', '.join(display_names)}"

        if asset_count > AssetConsolidator.MAX_DISPLAY_ASSETS:
            remaining = asset_count - AssetConsolidator.MAX_DISPLAY_ASSETS
            description_suffix += f" (and {remaining} more)"

        finding.description = f"{finding.description}{description_suffix}"


class IssueFieldSetter:
    """Handles setting control and assessment IDs on issues."""

    def __init__(self, cache: ControlImplementationCache, plan_id: int, parent_module: str) -> None:
        """
        Initialize the issue field setter.

        :param cache: Control implementation cache for lookups
        :param plan_id: RegScale security plan ID
        :param parent_module: Parent module name (e.g., 'securityplans')
        """
        self.cache = cache
        self.plan_id = plan_id
        self.parent_module = parent_module

    def set_control_and_assessment_ids(self, issue: regscale_models.Issue, control_id: str) -> IssueProcessingResult:
        """
        Set control implementation and assessment IDs on an issue.

        :param issue: Issue to update
        :param control_id: Normalized control ID
        :return: Result of the operation
        """
        try:
            # Get or find control implementation ID
            impl_id = self._get_or_find_implementation_id(control_id)
            if not impl_id:
                return IssueProcessingResult(
                    control_id=control_id,
                    implementation_id=None,
                    assessment_id=None,
                    success=False,
                    error_message=f"No control implementation found for control '{control_id}'",
                )

            # Set control implementation ID
            issue.controlId = impl_id

            # Get or find assessment ID
            assess_id = self._get_or_find_assessment_id(impl_id)
            if assess_id:
                issue.assessmentId = assess_id

                # Verify the field is set correctly
                if not (hasattr(issue, "assessmentId") and issue.assessmentId == assess_id):
                    logger.error(
                        f"❌ VERIFICATION FAILED: Expected {assess_id}, got {getattr(issue, 'assessmentId', 'NO_ATTR')}"
                    )
            else:
                logger.warning(
                    f"⚠️ No assessment found for control implementation {impl_id} (control '{control_id}') - assessmentId will not be set"
                )

            return IssueProcessingResult(
                control_id=control_id, implementation_id=impl_id, assessment_id=assess_id, success=True
            )

        except Exception as e:
            logger.error(f"Error setting control and assessment IDs: {e}")
            return IssueProcessingResult(
                control_id=control_id, implementation_id=None, assessment_id=None, success=False, error_message=str(e)
            )

    def _get_or_find_implementation_id(self, control_id: str) -> Optional[int]:
        """
        Get implementation ID from cache or database.

        :param control_id: Normalized control ID to search for
        :return: Control implementation ID if found, None otherwise
        """
        # Check cache first
        impl_id = self.cache.get_implementation_id(control_id)
        if impl_id:
            return impl_id

        # Query database
        impl_id = self._find_implementation_id_in_database(control_id)
        if impl_id:
            self.cache.set_implementation_id(control_id, impl_id)

        return impl_id

    def _find_implementation_id_in_database(self, control_id: str) -> Optional[int]:
        """
        Find control implementation ID by querying database.

        :param control_id: Normalized control ID to search for
        :return: Control implementation ID if found, None otherwise
        """
        try:
            implementations = regscale_models.ControlImplementation.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            for impl in implementations:
                if not hasattr(impl, "controlID") or not impl.controlID:
                    continue

                # Check cache for security control
                security_control = self.cache.get_security_control(impl.controlID)
                if not security_control:
                    security_control = regscale_models.SecurityControl.get_object(object_id=impl.controlID)
                    if security_control:
                        self.cache.set_security_control(impl.controlID, security_control)

                if security_control and hasattr(security_control, "controlId"):
                    from regscale.integrations.commercial.wizv2.policy_compliance import WizPolicyComplianceIntegration

                    impl_control_id = WizPolicyComplianceIntegration._normalize_control_id_string(
                        security_control.controlId
                    )

                    if impl_control_id == control_id:
                        logger.debug(f"✓ Found control implementation {impl.id} for control {control_id}")
                        return impl.id

            return None
        except Exception as e:
            logger.error(f"Error finding control implementation for {control_id}: {e}")
            return None

    def _get_or_find_assessment_id(self, impl_id: int) -> Optional[int]:
        """
        Get assessment ID from cache or database.

        IMPROVED: More robust assessment lookup with better logging.

        :param impl_id: Control implementation ID to search for
        :return: Assessment ID if found, None otherwise
        """
        # Check cache first
        assessment = self.cache.get_assessment(impl_id)
        if assessment and hasattr(assessment, "id"):
            return assessment.id

        # Query database
        assessment = self._find_most_recent_assessment(impl_id)
        if assessment:
            self.cache.set_assessment(impl_id, assessment)
            return assessment.id

        return None

    def _find_most_recent_assessment(self, impl_id: int) -> Optional[regscale_models.Assessment]:
        """
        Find most recent assessment for implementation.

        IMPROVED: Better error handling, logging, and assessment selection logic.

        :param impl_id: Control implementation ID to search for
        :return: Most recent assessment object if found, None otherwise
        """
        try:
            assessments = regscale_models.Assessment.get_all_by_parent(parent_id=impl_id, parent_module="controls")

            if not assessments:
                return None

            # Find today's assessments first
            today = datetime.now().date()
            today_assessments = []
            other_assessments = []

            for assessment in assessments:
                assessment_date = self._extract_assessment_date(assessment)
                if assessment_date == today:
                    today_assessments.append(assessment)
                else:
                    other_assessments.append((assessment, assessment_date))

            # Prefer today's assessments (most recently created)
            if today_assessments:
                best_assessment = max(today_assessments, key=lambda a: getattr(a, "id", 0))
                return best_assessment

            # Fall back to most recent overall (by date, then by ID)
            if other_assessments:
                best_assessment = max(
                    other_assessments, key=lambda x: (x[1] or datetime.min.date(), getattr(x[0], "id", 0))
                )[0]
                return best_assessment

            return None
        except Exception as e:
            logger.error(f"Error finding assessment for implementation {impl_id}: {e}")
            import traceback

            return None

    def _extract_assessment_date(self, assessment) -> Optional[datetime.date]:
        """
        Extract date from assessment object.

        :param assessment: Assessment object to extract date from
        :return: Extracted date if found, None otherwise
        """
        try:
            date_fields = ["plannedStart", "actualFinish", "plannedFinish", "dateCreated"]
            for field in date_fields:
                if hasattr(assessment, field):
                    date_value = getattr(assessment, field)
                    if date_value:
                        if isinstance(date_value, str):
                            return regscale_string_to_datetime(date_value).date()
                        elif hasattr(date_value, "date"):
                            return date_value.date()
                        else:
                            return date_value
            return None
        except Exception:
            return None


class ControlAssessmentProcessor:
    """Handles control assessment creation and updates."""

    def __init__(self, plan_id: int, parent_module: str, scan_date: str, title: str, framework: str) -> None:
        """
        Initialize the control assessment processor.

        :param plan_id: RegScale security plan ID
        :param parent_module: Parent module name (e.g., 'securityplans')
        :param scan_date: Date of the assessment scan
        :param title: Title for assessments
        :param framework: Framework name (e.g., 'NIST800-53R5')
        """
        self.plan_id = plan_id
        self.parent_module = parent_module
        self.scan_date = scan_date
        self.title = title
        self.framework = framework
        self.cache = ControlImplementationCache()

    def create_or_update_assessment(
        self,
        implementation: regscale_models.ControlImplementation,
        control_id: str,
        result: str,
        compliance_items: List[Any],
    ) -> Optional[regscale_models.Assessment]:
        """
        Create or update a control assessment.

        :param implementation: Control implementation
        :param control_id: Control identifier
        :param result: Assessment result ('Pass' or 'Fail')
        :param compliance_items: List of compliance items for this control
        :return: Created or updated assessment
        """
        try:
            # Check for existing assessment today
            existing_assessment = self._find_existing_assessment_for_today(implementation.id)

            assessment_report = self._create_assessment_report(control_id, result, compliance_items)

            if existing_assessment:
                # Update existing
                existing_assessment.assessmentResult = result
                existing_assessment.assessmentReport = assessment_report
                existing_assessment.actualFinish = get_current_datetime()
                existing_assessment.dateLastUpdated = get_current_datetime()
                existing_assessment.save()

                self.cache.set_assessment(implementation.id, existing_assessment)
                logger.info(f"✅ Updated existing assessment {existing_assessment.id} for control {control_id}")
                return existing_assessment
            else:
                # Create new
                assessment = regscale_models.Assessment(
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

                self.cache.set_assessment(implementation.id, assessment)
                logger.info(f"✅ Created new assessment {assessment.id} for control {control_id}")
                return assessment

        except Exception as e:
            logger.error(f"Error creating/updating assessment for control {control_id}: {e}")
            return None

    def _find_existing_assessment_for_today(self, impl_id: int) -> Optional[regscale_models.Assessment]:
        """
        Find existing assessment for today.

        :param impl_id: Control implementation ID to search for
        :return: Today's assessment if found, None otherwise
        """
        # Check cache first
        cached = self.cache.get_assessment(impl_id)
        if cached:
            return cached

        # Query database for today's assessments
        try:
            today = datetime.now().date()
            assessments = regscale_models.Assessment.get_all_by_parent(parent_id=impl_id, parent_module="controls")

            for assessment in assessments:
                if hasattr(assessment, "actualFinish") and assessment.actualFinish:
                    try:
                        if isinstance(assessment.actualFinish, str):
                            assessment_date = regscale_string_to_datetime(assessment.actualFinish).date()
                        elif hasattr(assessment.actualFinish, "date"):
                            assessment_date = assessment.actualFinish.date()
                        else:
                            assessment_date = assessment.actualFinish

                        if assessment_date == today:
                            self.cache.set_assessment(impl_id, assessment)
                            return assessment
                    except Exception:
                        continue

            return None
        except Exception:
            return None

    def _create_assessment_report(self, control_id: str, result: str, compliance_items: List[Any]) -> str:
        """
        Create HTML assessment report.

        :param control_id: Control identifier (e.g., 'AC-2(1)')
        :param result: Assessment result ('Pass' or 'Fail')
        :param compliance_items: List of compliance items for this control
        :return: HTML formatted assessment report
        """
        result_color = "#d32f2f" if result == "Fail" else "#2e7d32"
        bg_color = "#ffebee" if result == "Fail" else "#e8f5e8"

        html_parts = [
            f"""
            <div style="margin-bottom: 20px; padding: 15px; border: 2px solid {result_color};
                        border-radius: 5px; background-color: {bg_color};">
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
        ]

        if compliance_items:
            pass_count = len(
                [
                    item
                    for item in compliance_items
                    if hasattr(item, "compliance_result")
                    and item.compliance_result in ["PASS", "PASSED", "pass", "passed"]
                ]
            )
            fail_count = len(compliance_items) - pass_count

            unique_resources = set()
            unique_policies = set()

            for item in compliance_items:
                if hasattr(item, "resource_id"):
                    unique_resources.add(item.resource_id)
                if hasattr(item, "description") and item.description:
                    policy_desc = item.description[:50] + "..." if len(item.description) > 50 else item.description
                    unique_policies.add(policy_desc)

            html_parts.append(
                f"""
            <div style="margin-top: 20px;">
                <h4>Assessment Summary</h4>
                <p><strong>Policy Assessments:</strong> {len(compliance_items)} total</p>
                <p><strong>Unique Policies:</strong> {len(unique_policies)}</p>
                <p><strong>Unique Resources:</strong> {len(unique_resources)}</p>
                <p><strong>Passing:</strong> <span style="color: #2e7d32;">{pass_count}</span></p>
                <p><strong>Failing:</strong> <span style="color: #d32f2f;">{fail_count}</span></p>
            </div>
            """
            )

        return "\n".join(html_parts)
