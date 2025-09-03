"""Class to handle mapping RegScale models to OCSF models for Synqly integration"""

from datetime import datetime
from typing import Any, Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from regscale.models.integration_models.synqly_models.connectors import Edr, Ticketing, Vulnerabilities
    from synqly.engine.resources.ocsf.resources.v_1_1_0.resources.securityfinding import ResourceDetails, Vulnerability

from synqly import engine
from synqly.engine import CreateTicketRequest
from synqly.engine.resources.ticketing.types.priority import Priority

from regscale.core.app.utils.app_utils import (
    error_and_exit,
    convert_datetime_to_regscale_string,
)
from synqly.engine.resources.ticketing.types.ticket import Ticket
from synqly.engine.resources.vulnerabilities.types import Asset as OCSFAsset, SecurityFinding
from synqly.engine.resources.events.types import Event_DetectionFinding as Alerts
from synqly.engine.resources.ocsf.resources.v_1_3_0.resources.softwareinfo import SoftwareInfo
from synqly.engine.resources.ocsf.resources.v_1_3_0.resources.inventoryinfo import InventoryInfo
from regscale.models.regscale_models import Issue
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding


class Mapper:
    """Mapping class to handle RegScale models to OCSF models for Synqly integration"""

    date_format = "%Y-%m-%dT%H:%M:%S"

    def to_ocsf(self, regscale_object: Any, **kwargs) -> Any:
        """
        Convert RegScale object to OCSF object

        :param Any regscale_object: RegScale object to convert to an OCSF object
        :return: The comparable OCSF object
        :rtype: Any
        """
        if isinstance(regscale_object, Issue):
            return self._regscale_issue_to_ticket(regscale_object, **kwargs)
        else:
            error_and_exit(f"Unsupported object type {type(regscale_object)}")

    def to_regscale(self, ocsf_object: Any, connector: Union["Edr", "Ticketing", "Vulnerabilities"], **kwargs) -> Any:
        """
        Convert OCSF object to RegScale object

        :param Any ocsf_object: OCSF object to convert to a RegScale object
        :param Union["Edr", "Ticketing", "Vulnerabilities"] connector: Connector class object
        :return: The comparable RegScale object
        :rtype: Any
        """
        if isinstance(ocsf_object, Ticket):
            return self._ticket_to_regscale(connector, ocsf_object, **kwargs)
        elif (
            isinstance(ocsf_object, OCSFAsset)
            or isinstance(ocsf_object, SoftwareInfo)
            or isinstance(ocsf_object, InventoryInfo)
        ):
            return self._ocsf_asset_to_regscale(connector, ocsf_object, **kwargs)
        elif isinstance(ocsf_object, SecurityFinding):
            return self._security_finding_to_regscale(connector, ocsf_object, **kwargs)
        elif isinstance(ocsf_object, Alerts):
            return self._security_alert_to_regscale(connector, ocsf_object, **kwargs)
        else:
            error_and_exit(f"Unsupported object type {type(ocsf_object)}")

    def _ticket_to_regscale(self, connector: "Ticketing", ticket: Ticket, **kwargs) -> Issue:
        """
        Convert OCSF Ticket to RegScale Issue

        :param "Ticketing" connector: Ticketing connector class object
        :param Ticket ticket: OCSF Ticket to convert to a RegScale Issue
        :param dict **kwargs: Keyword Arguments
        :return: The comparable RegScale Issue
        :rtype: Issue
        """
        due_date = convert_datetime_to_regscale_string(ticket.due_date)
        if not due_date:
            due_date = self._determine_due_date(ticket.priority)
        ticket_dict = ticket.dict()
        key_val_desc = "All fields:\n"
        for k, v in ticket_dict.items():
            key_val_desc += f"{k.replace('_', ' ').title()}: {str(v) or 'NULL'}\n"
        regscale_issue = Issue(
            title=ticket.summary,
            severityLevel=Issue.assign_severity(ticket.priority),
            dueDate=due_date,
            description=f"Description {ticket.description}\n{key_val_desc}",
            status=("Closed" if ticket.status.lower() == "done" else "Draft"),
            dateCompleted=(
                convert_datetime_to_regscale_string(ticket.completion_date) if ticket.status.lower() == "done" else None
            ),
            **kwargs,
        )
        # update the correct integration field names or manual detection fields
        if connector.has_integration_field:
            setattr(regscale_issue, connector.integration_id_field, ticket.id)
        else:
            regscale_issue.manualDetectionSource = connector.integration
            regscale_issue.manualDetectionId = ticket.id
        return regscale_issue

    @staticmethod
    def _ocsf_asset_to_regscale(
        connector: Union["Edr", "Vulnerabilities"], asset: Union[InventoryInfo, OCSFAsset, SoftwareInfo], **kwargs
    ) -> IntegrationAsset:
        """
        Convert OCSF Asset to RegScale Asset

        :param Union["Edr", "Vulnerabilities"] connector: Edr or Vulnerabilities connector class object
        :param Union[InventoryInfo, OCSFAsset, SoftwareInfo] asset: OCSF Asset data to convert to an IntegrationAsset
        :return: The comparable IntegrationAsset object
        :rtype: IntegrationAsset
        """
        from regscale.models.regscale_models import AssetCategory, SecurityPlan

        device_data = asset.device
        os_data = device_data.os
        if device_data.sw_info:
            software_inventory = [
                {"name": sw.name, "version": sw.version} for sw in device_data.sw_info if getattr(sw, "name", None)
            ]
        else:
            software_inventory = []
        if isinstance(asset, OCSFAsset):  # this is a hardware asset
            name = device_data.name or device_data.hostname or f"{connector.provider} Asset: {device_data.instance_uid}"
            category = AssetCategory.Hardware
        else:
            name = device_data.name or device_data.hostname or f"{connector.provider} Asset: {device_data.uid}"
            category = AssetCategory.Software
        return IntegrationAsset(
            name=name,
            identifier=device_data.uid,
            asset_type=device_data.type or "Other",
            asset_category=category,
            parent_id=kwargs.pop("regscale_ssp_id"),
            parent_module=SecurityPlan.get_module_string(),
            mac_address=device_data.mac,
            fqdn=device_data.hostname,
            ip_address=", ".join(device_data.ip_addresses) if device_data.ip_addresses else device_data.ip,
            location=device_data.location or device_data.zone,
            vlan_id=device_data.vlan_uid,
            other_tracking_number=device_data.uid,
            serial_number=device_data.hw_info.serial_number if device_data.hw_info else None,
            cpu=device_data.hw_info.cpu_cores if device_data.hw_info else None,
            ram=device_data.hw_info.ram_size if device_data.hw_info else None,
            operating_system=os_data.name or os_data.type if os_data else None,
            os_version=os_data.version if os_data else None,
            software_inventory=software_inventory,
        )

    @staticmethod
    def _parse_finding_data(finding: "SecurityFinding", vuln: Optional["Vulnerability"] = None) -> dict:
        """
        Parse the data from the SecurityFinding object

        :param Optional[Vulnerability] vuln: OCSF Vulnerability object, defaults to None
        :return: A dictionary of the parsed data
        :rtype: dict
        """
        from synqly.engine.resources.ocsf.resources.v_1_1_0.resources.securityfinding import Remediation

        finding_data = {
            "cve": None,
            "first_seen": vuln.first_seen_time_dt if vuln else finding.finding.first_seen_time_dt,
            "last_seen": vuln.last_seen_time_dt if vuln else finding.finding.last_seen_time_dt,
            "plugin_id": vuln.cve.uid if vuln else finding.finding.product_uid,
            "severity": int(vuln.severity) if vuln else finding.severity_id,
            "remediation": getattr(vuln, "remediation") if vuln else finding.finding.remediation.desc,
        }
        if vuln:
            finding_data["cve"] = vuln.cve.uid
        else:
            finding_data["cve"] = finding.finding.title if "cve" in finding.finding.title.lower() else None
        if isinstance(finding_data["remediation"], Remediation):
            finding_data["remediation"] = finding_data["remediation"].desc
        elif isinstance(finding_data["remediation"], dict):
            remediation_string = ""
            for f, v in finding_data["remediation"].items():
                remediation_string += f"{f}: {v}\n"
            finding_data["remediation"] = remediation_string
        elif isinstance(finding_data["remediation"], list):
            finding_data["remediation"] = "\n".join(finding_data["remediation"])
        return finding_data

    @staticmethod
    def _populate_cvs_scores(finding_obj: IntegrationFinding, vuln: Optional["Vulnerability"] = None) -> None:
        """
        Populates the CVSS scores for the provided IntegrationFinding object

        :param IntegrationFinding finding_obj: IntegrationFinding object
        :param Vulnerability vuln: OCSF Vulnerability object, defaults to None
        :rtype: None
        """
        if vuln:
            for cvs in getattr(vuln.cve, "cvss", []):
                if "3" in cvs.version:
                    finding_obj.cvss_v3_score = cvs.base_score
                elif "2" in cvs.version:
                    finding_obj.cvss_v2_score = cvs.base_score
                else:
                    finding_obj.cvss_score = cvs.base_score

    def _security_finding_to_regscale(
        self, connector: "Vulnerabilities", finding: SecurityFinding, **_
    ) -> list[IntegrationFinding]:
        """
        Convert OCSF SecurityFinding to RegScale IntegrationFinding

        :param "Vulnerabilities" connector: Vulnerabilities connector class object
        :param SecurityFinding finding: OCSF SecurityFinding to convert to an IntegrationFinding
        :return: List of comparable IntegrationFinding objects
        :rtype: list[IntegrationFinding]
        """
        findings = []

        def _create_finding(resource: "ResourceDetails", vuln: Optional["Vulnerability"] = None) -> IntegrationFinding:
            """
            Create an IntegrationFinding object from a resource and vulnerability

            :param ResourceDetails resource: OCSF ResourceDetails object
            :param Optional[Vulnerability] vuln: OCSF Vulnerability object, defaults to None
            :return: An IntegrationFinding object
            :rtype: IntegrationFinding
            """
            base = vuln if vuln else finding.finding
            finding_data = self._parse_finding_data(finding, vuln)
            if resource.data:
                dns = resource.data.get("hostname")
                ip_address = resource.data.get("ipv4")
            else:
                dns = resource.uid if vuln else None
                ip_address = None

            finding_obj = IntegrationFinding(
                control_labels=[],
                category=f"{connector.integration_name} Vulnerability",
                title=base.title,
                plugin_name=connector.integration_name,
                severity=Issue.assign_severity(finding.severity),  # type: ignore
                description=base.desc,
                status=finding.status or "Open",
                first_seen=self._datetime_to_str(finding_data["first_seen"]),
                last_seen=self._datetime_to_str(finding_data["last_seen"]),
                ip_address=ip_address,
                plugin_id=finding_data["plugin_id"],
                dns=dns,
                severity_int=finding_data["severity"],
                issue_title=base.title,
                cve=finding_data["cve"],
                evidence=finding.evidence,
                impact=finding.impact,
                asset_identifier=resource.uid,
                source_report=connector.integration_name,
                remediation=finding_data["remediation"],
            )

            self._populate_cvs_scores(finding_obj, vuln)

            return finding_obj

        for asset in finding.resources:
            if finding.vulnerabilities:
                findings.extend(_create_finding(asset, vuln) for vuln in finding.vulnerabilities)
            else:
                findings.append(_create_finding(asset))

        return findings

    def _security_alert_to_regscale(self, connector: "Edr", finding: Alerts, **_) -> IntegrationFinding:
        """
        Converts an OCSF Event_DetectionFinding (Alerts) to a RegScale IntegrationFinding

        :param "Edr" connector: Edr connector class object
        :param Alerts finding: OCSF Event_DetectionFinding (Alerts) to convert to an IntegrationFinding
        :return: Comparable IntegrationFinding object
        :rtype: IntegrationFinding
        """
        from regscale.models.regscale_models.issue import IssueStatus

        asset = finding.device
        vuln = finding.finding_info

        return IntegrationFinding(
            control_labels=[],
            category=f"{connector.integration_name} Vulnerability",
            title=vuln.title,
            plugin_name=connector.integration_name,
            severity=Issue.assign_severity(finding.severity),  # type: ignore
            description=vuln.desc or finding.comment,
            status=IssueStatus.Open,
            first_seen=self._datetime_to_str(vuln.first_seen_time_dt),
            last_seen=self._datetime_to_str(vuln.last_seen_time_dt),
            ip_address=asset.ip,
            plugin_id=vuln.product_uid,
            dns=asset.hostname,
            issue_title=vuln.title,
            impact=finding.impact,
            asset_identifier=asset.uid,
            source_report=connector.integration_name,
        )

    def _datetime_to_str(self, date_time: Optional[datetime] = None) -> str:
        """
        Convert a datetime object to a string

        :param Optional[datetime] date_time: The datetime object to convert, defaults to None
        :return: The datetime as a string
        :rtype: str
        """
        from regscale.core.utils.date import datetime_str

        return datetime_str(date_time, self.date_format)

    @staticmethod
    def _map_ticket_priority(severity: str) -> Priority:
        """
        Map RegScale severity to OCSF priority

        :param str severity: RegScale severity
        :return: OCSF priority
        :rtype: Priority
        """
        if "high" in severity.lower():
            return Priority.HIGH
        elif "moderate" in severity.lower():
            return Priority.MEDIUM
        else:
            return Priority.LOW

    def _determine_due_date(self, severity: str) -> str:
        """
        Determine the due date based on the provided severity

        :param str severity: RegScale severity
        :return: Due date for the issue
        :rtype: str
        """
        from datetime import timedelta

        if "high" in severity.lower():
            return (datetime.now() + timedelta(days=30)).strftime(self.date_format)
        elif "medium" in severity.lower():
            return (datetime.now() + timedelta(days=60)).strftime(self.date_format)
        else:
            return (datetime.now() + timedelta(days=90)).strftime(self.date_format)

    def _regscale_issue_to_ticket(self, regscale_issue: Issue, **kwargs) -> CreateTicketRequest:
        """
        Maps a RegScale issue to a JIRA issue

        :param Issue regscale_issue: RegScale issue object
        :return: Synqly CreateTicketRequest object
        :rtype: CreateTicketRequest
        """
        description = ""
        for key, value in regscale_issue.dict().items():
            if key not in ["id"] and value:
                description += f"{key.title()}: {value}\n"
        if project := kwargs.get("default_project"):
            kwargs.pop("default_project")
            return engine.CreateTicketRequest(
                name=regscale_issue.title,
                description=f"RegScale Issue #{regscale_issue.id}:\n{description}",
                summary=regscale_issue.title,
                creator=kwargs.get("creator", "RegScale CLI"),
                priority=self._map_ticket_priority(regscale_issue.severityLevel),
                project=project,
                **kwargs,
            )
        else:
            return engine.CreateTicketRequest(
                name=regscale_issue.title,
                description=f"RegScale Issue #{regscale_issue.id}:\n{description}",
                summary=regscale_issue.title,
                creator=kwargs.get("creator", "RegScale CLI"),
                priority=self._map_ticket_priority(regscale_issue.severityLevel),
                **kwargs,
            )
