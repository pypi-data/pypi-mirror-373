"""Wiz Issue Integration class"""

import logging
import re
from typing import List, Dict, Any, Iterator, Optional

from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.integrations.scanner_integration import IntegrationFinding
from regscale.utils.dict_utils import get_value
from regscale.models import Issue
from .constants import (
    get_wiz_issue_queries,
    WizVulnerabilityType,
)
from .scanner import WizVulnerabilityIntegration

logger = logging.getLogger(__name__)


class WizIssue(WizVulnerabilityIntegration):
    """
    Wiz Issue class
    """

    title = "Wiz-Issue"
    asset_identifier_field = "wizId"
    issue_identifier_field = "wizId"

    def get_query_types(self, project_id: str) -> List[Dict[str, Any]]:
        """Get the query types for issue scanning.

        :param str project_id: The project ID to get queries for
        :return: List of query types
        :rtype: List[Dict[str, Any]]
        """
        return get_wiz_issue_queries(project_id=project_id)

    def parse_findings(
        self, nodes: List[Dict[str, Any]], vulnerability_type: WizVulnerabilityType
    ) -> Iterator[IntegrationFinding]:
        """
        Parse the Wiz issues into IntegrationFinding objects
        :param nodes:
        :param vulnerability_type:
        :return:
        """
        for node in nodes:
            finding = self.parse_finding(node, vulnerability_type)
            if finding:
                yield finding

    def _parse_security_subcategories(self, source_rule: Dict[str, Any]) -> List[str]:
        """
        Parse security subcategories from a source rule.

        :param Dict[str, Any] source_rule: The source rule containing security subcategories
        :return: List of formatted security subcategories
        :rtype: List[str]
        """
        if not source_rule or "securitySubCategories" not in source_rule:
            return []

        subcategories = []
        for subcat in source_rule.get("securitySubCategories", []):
            if control_id := self._extract_nist_control_id(subcat):
                subcategories.append(control_id)

        return subcategories

    def _extract_nist_control_id(self, subcat: Dict[str, Any]) -> Optional[str]:
        """
        Extract and format NIST control ID from a security subcategory.

        :param Dict[str, Any] subcat: The security subcategory data
        :return: Formatted control ID or None if invalid
        :rtype: Optional[str]
        """
        framework = subcat.get("category", {}).get("framework", {}).get("name", "")
        external_id = subcat.get("externalId", "")

        if not external_id or "NIST SP 800-53" not in framework:
            return None

        return self._format_control_id(external_id.strip())

    @staticmethod
    def _format_control_id(control_id: str) -> Optional[str]:
        """
        Format a control ID into RegScale format.

        :param str control_id: The raw control ID
        :return: Formatted control ID or None if invalid
        :rtype: Optional[str]
        """
        match = re.match(r"^([A-Z]{2})-(\d+)(?:\s*\((\d+)\))?$", control_id)
        if not match:
            return None

        family = match.group(1).lower()
        number = match.group(2)
        enhancement = match.group(3)

        return f"{family}-{number}" + (f".{enhancement}" if enhancement else "")

    @staticmethod
    def _get_asset_identifier(wiz_issue: Dict[str, Any]) -> str:
        """
        Get the asset identifier from a Wiz issue.

        :param Dict[str, Any] wiz_issue: The Wiz issue
        :return: The asset identifier
        :rtype: str
        """
        # Check entitySnapshot first
        if entity_snapshot := wiz_issue.get("entitySnapshot"):
            if entity_id := entity_snapshot.get("id"):
                return entity_id

        # Check related entities
        if "relatedEntities" in wiz_issue:
            entities = wiz_issue.get("relatedEntities", [])
            if entities and isinstance(entities, list):
                for entity in entities:
                    if entity and isinstance(entity, dict) and (entity_id := entity.get("id")):
                        return entity_id

        # Check common asset ID paths
        asset_paths = [
            "vulnerableAsset.id",
            "entity.id",
            "resource.id",
            "relatedEntity.id",
            "sourceEntity.id",
            "target.id",
        ]

        for path in asset_paths:
            if asset_id := get_value(wiz_issue, path):
                return asset_id

        # Try source rule as fallback
        if source_rule := wiz_issue.get("sourceRule"):
            if rule_id := source_rule.get("id"):
                return f"wiz-rule-{rule_id}"

        # Final fallback - use the issue ID
        return f"wiz-issue-{wiz_issue.get('id', 'unknown')}"

    @staticmethod
    def _format_control_description(control: Dict[str, Any]) -> str:
        """
        Format the control description with additional context.

        :param Dict[str, Any] control: The control data
        :return: Formatted description
        :rtype: str
        """
        formatted_desc = []
        if description := control.get("controlDescription", ""):
            formatted_desc.append("Description:")
            formatted_desc.append(description)

        if recommendation := control.get("resolutionRecommendation", ""):
            if formatted_desc:
                formatted_desc.append("\n")
            formatted_desc.append("Resolution Recommendation:")
            formatted_desc.append(recommendation)

        return "\n".join(formatted_desc) if formatted_desc else "No description available"

    def _get_plugin_name(self, wiz_issue: Dict[str, Any]) -> str:
        """
        Generate a unique plugin name based on the Wiz issue type and source rule.

        :param Dict[str, Any] wiz_issue: The Wiz issue data
        :return: A unique plugin name
        :rtype: str
        """
        source_rule = wiz_issue.get("sourceRule", {})
        typename = source_rule.get("__typename", "")
        service_type = source_rule.get("serviceType", "")
        name = source_rule.get("name", "")

        if not typename:
            return "Wiz-Finding"

        if typename == "CloudConfigurationRule":
            return self._get_config_plugin_name(name, service_type)
        if typename == "Control":
            return self._get_control_plugin_name(source_rule, name)
        if typename == "CloudEventRule":
            return self._get_event_plugin_name(name, service_type)

        return "Wiz-Finding"

    @staticmethod
    def _get_config_plugin_name(name: str, service_type: str) -> str:
        """
        Generate plugin name for CloudConfigurationRule type.

        :param str name: Rule name
        :param str service_type: Service type
        :return: Plugin name
        :rtype: str
        """
        if not name:
            return f"Wiz-{service_type}-Config"

        # Simplified regex pattern that just looks for service name at start
        service_match = re.match(r"^([A-Za-z\s]+?)\s+(?:public|private|should|must|needs|to)", name)
        if not service_match:
            return f"Wiz-{service_type}-Config"

        service_name = service_match.group(1).strip()
        if service_name == "App Configuration":
            return f"Wiz-{service_type}-AppConfiguration"

        service_name = "".join(word.capitalize() for word in service_name.split())
        return f"Wiz-{service_type}-{service_name}"

    @staticmethod
    def _get_control_plugin_name(source_rule: Dict[str, Any], name: str) -> str:
        """
        Generate plugin name for Control type.

        :param Dict[str, Any] source_rule: Source rule data
        :param str name: Rule name
        :return: Plugin name
        :rtype: str
        """
        # Try to get NIST category first
        subcategories = source_rule.get("securitySubCategories", [])
        for subcat in subcategories:
            category = subcat.get("category", {})
            if category.get("framework", {}).get("name", "").lower() == "nist sp 800-53 revision 5":
                category_name = category.get("name", "")
                category_match = re.match(r"^([A-Z]+)\s", category_name)
                if category_match:
                    return f"Wiz-Control-{category_match.group(1)}"
                break

        # Fallback to control name prefix
        if name:
            prefix_match = re.match(r"^([A-Za-z\s]+?)\s+(?:exposed|misconfigured|vulnerable|security|access)", name)
            if prefix_match:
                prefix = "".join(word.capitalize() for word in prefix_match.group(1).strip().split())
                return f"Wiz-Control-{prefix}"

        return "Wiz-Security-Control"

    @staticmethod
    def _get_event_plugin_name(name: str, service_type: str) -> str:
        """
        Generate plugin name for CloudEventRule type.

        :param str name: Rule name
        :param str service_type: Service type
        :return: Plugin name
        :rtype: str
        """
        if not service_type:
            return "Wiz-Event"
        if not name:
            return f"Wiz-{service_type}-Event"
        event_match = re.match(r"^([A-Za-z\s]+?)\s+(detection|event|alert|activity)", name)
        if not event_match:
            return f"Wiz-{service_type}-Event"

        event_type = event_match.group(1).strip()
        if event_type == "Suspicious" and event_match.group(2).strip().lower() == "activity":
            return f"Wiz-{service_type}-SuspiciousActivity"

        event_type = "".join(word.capitalize() for word in event_type.split())
        return f"Wiz-{service_type}-{event_type}"

    @staticmethod
    def _get_source_rule_id(source_rule: Dict[str, Any]) -> str:
        """
        Generate a source rule identifier that includes the type and ID.

        :param Dict[str, Any] source_rule: The source rule data
        :return: A formatted source rule identifier
        :rtype: str
        """
        typename = source_rule.get("__typename", "")
        rule_id = source_rule.get("id", "")
        service_type = source_rule.get("serviceType", "")

        if typename and rule_id:
            if service_type:
                return f"{typename}-{service_type}-{rule_id}"
            return f"{typename}-{rule_id}"
        return rule_id

    # noinspection PyMethodOverriding
    def parse_finding(self, wiz_issue: Dict[str, Any], vulnerability_type: WizVulnerabilityType) -> IntegrationFinding:
        """
        Parses a Wiz issue into an IntegrationFinding object.

        :param Dict[str, Any] wiz_issue: The Wiz issue to parse
        :param WizVulnerabilityType vulnerability_type: The type of vulnerability
        :return: The parsed IntegrationFinding
        :rtype: IntegrationFinding
        """
        wiz_id = wiz_issue.get("id", "N/A")
        severity = self.get_issue_severity(wiz_issue.get("severity", "Low"))
        status = self.map_status_to_issue_status(wiz_issue.get("status", "OPEN"))
        date_created = safe_datetime_str(wiz_issue.get("createdAt"))
        name: str = wiz_issue.get("name", "")

        # Handle source rule (Control) specific fields
        source_rule = wiz_issue.get("sourceRule", {})
        control_name = source_rule.get("name", "")

        # Get control labels from security subcategories
        control_labels = self._parse_security_subcategories(source_rule)

        # Get asset identifier
        asset_id = self._get_asset_identifier(wiz_issue)

        # Format description with control context
        description = self._format_control_description(source_rule) if source_rule else wiz_issue.get("description", "")

        # Handle CVE if present
        cve = (
            name
            if name and (name.startswith("CVE") or name.startswith("GHSA")) and not wiz_issue.get("cve")
            else wiz_issue.get("cve")
        )

        # Get plugin name and source rule ID
        plugin_name = self._get_plugin_name(wiz_issue)
        source_rule_id = self._get_source_rule_id(source_rule)

        # Get Security Check from plugin name
        security_check = f"Wiz {plugin_name}"

        return IntegrationFinding(
            control_labels=control_labels,
            category="Wiz Control" if source_rule else "Wiz Vulnerability",
            title=control_name or wiz_issue.get("name") or f"unknown - {wiz_id}",
            security_check=security_check,
            description=description,
            severity=severity,
            status=status,
            asset_identifier=asset_id,
            external_id=wiz_id,
            first_seen=date_created,
            last_seen=safe_datetime_str(wiz_issue.get("lastDetectedAt")),
            remediation=source_rule.get("resolutionRecommendation")
            or f"Update to version {wiz_issue.get('fixedVersion')} or higher",
            cve=cve,
            plugin_name=plugin_name,
            source_rule_id=source_rule_id,
            vulnerability_type=vulnerability_type.value,
            date_created=date_created,
            due_date=Issue.get_due_date(severity, self.app.config, "wiz", date_created),
            recommendation_for_mitigation=source_rule.get("resolutionRecommendation")
            or wiz_issue.get("description", ""),
            poam_comments=None,
            basis_for_adjustment=None,
        )
