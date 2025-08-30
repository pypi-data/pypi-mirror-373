"""Functions for parsing STIG output from Tenable"""

import logging
import re
from typing import Union

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.scanner_integration import IntegrationFinding, issue_due_date
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


def parse_stig_output(output: str, finding: IntegrationFinding) -> IntegrationFinding:
    """
    Parses STIG output and constructs a finding dictionary matching IntegrationFinding.

    :param str output: The STIG output string to parse.
    :param IntegrationFinding finding: The finding to update.
    :return: An IntegrationFinding object containing the parsed finding information.
    :rtype: IntegrationFinding
    """

    def _extract_field(pattern: str, text: str, flags: Union[int, re.RegexFlag] = 0, group: int = 1) -> str:
        """
        Extracts a field from a string using a regular expression

        :param str pattern: The regular expression pattern to search for
        :param str text: The string to search in
        :param int flags: Optional regular expression flags, defaults to 0
        :param int group: The group number to return from the match, defaults to 1
        :return: The extracted field as a string. Empty string if no match was found
        :rtype: str
        """
        match = re.search(pattern, text, flags)
        return match.group(group).strip() if match else ""

    # Extract fields
    check_name_full = _extract_field(r"Check Name:\s*(.*?)\n", output, flags=re.DOTALL | re.MULTILINE)
    check_name_parts = check_name_full.split(":", 1)
    rule_id = check_name_parts[0].strip()
    check_description = check_name_parts[1].strip() if len(check_name_parts) > 1 else ""

    baseline = _extract_field(r"(.*?)\s+Target\s+(.*)", check_description, group=2)
    if target_match := _extract_field(r"(.*?)\s+Target\s+(.*)", check_description):
        check_description = check_description[: check_description.find(target_match) + len(target_match)].strip()

    information = _extract_field(r"Information:\s*(.*?)\n", output, flags=re.DOTALL | re.MULTILINE)
    vuln_discuss = _extract_field(r"VulnDiscussion='(.*?)'\s", output, flags=re.DOTALL | re.MULTILINE)
    result = _extract_field(r"Result:\s*(.*?)(?:\n|$)", output, flags=re.IGNORECASE | re.DOTALL)
    solution = _extract_field(r"Solution:\s*(.*?)\n\nReference Information:", output, flags=re.DOTALL | re.MULTILINE)

    # Extract reference information
    ref_info = _extract_field(r"Reference Information:\s*(.*)", output, flags=re.DOTALL | re.MULTILINE)
    ref_dict = dict(item.split("|", 1) for item in ref_info.split(",") if "|" in item)

    # Extract specific references
    cci_ref = ref_dict.get("CCI", "CCI-000366")
    severity = ref_dict.get("SEVERITY", "").lower()
    oval_def = ref_dict.get("OVAL-DEF", "")
    generated_date = ref_dict.get("GENERATED-DATE", "")
    updated_date = ref_dict.get("UPDATED-DATE", "")
    scan_date = ref_dict.get("SCAN-DATE", "")
    rule_id_full = ref_dict.get("RULE-ID", "")
    group_id = ref_dict.get("GROUP-ID", "")

    vuln_num_match = re.search(r"SV-\d+r\d+_rule", rule_id)
    vuln_num = vuln_num_match.group(0) if vuln_num_match else "unknown"

    title = f"{vuln_num}: {check_description}"
    issue_title = title

    status_map = {
        "PASSED": regscale_models.ChecklistStatus.PASS,
        "FAILED": regscale_models.ChecklistStatus.FAIL,
        "ERROR": regscale_models.ChecklistStatus.FAIL,
        "NOT APPLICABLE": regscale_models.ChecklistStatus.NOT_APPLICABLE,
        "NOT_APPLICABLE": regscale_models.ChecklistStatus.NOT_APPLICABLE,
    }

    result_key = result.upper().replace("_", " ").strip()
    if result_key not in status_map:
        logger.warning(f"Result '{result}' not found in status map")
        status = regscale_models.ChecklistStatus.NOT_REVIEWED
    else:
        status = status_map[result_key]

    # Map severity to IssueSeverity enum
    priority = (severity or "").title()
    severity_map = {
        "critical": regscale_models.IssueSeverity.Critical,
        "high": regscale_models.IssueSeverity.High,
        "medium": regscale_models.IssueSeverity.Moderate,
        "low": regscale_models.IssueSeverity.Low,
    }
    severity = severity_map.get(severity.lower(), regscale_models.IssueSeverity.NotAssigned)

    results = (
        f"Vulnerability Number: {vuln_num}, Severity: {severity.value}, "
        f"Rule Title: {check_description}<br><br>"
        f"Check Content: {information}<br><br>"
        f"Vulnerability Discussion: {vuln_discuss}<br><br>"
        f"Fix Text: {solution}<br><br>"
        f"STIG Reference: {rule_id}"
    )

    current_datetime = get_current_datetime()
    finding.title = title
    finding.category = "STIG"
    finding.plugin_id = cci_ref
    finding.plugin_name = rule_id
    finding.severity = severity
    finding.description = f"{information}\n\nVulnerability Discussion: {vuln_discuss}\n\nSolution: {solution}"
    finding.status = status
    finding.priority = priority  # Set priority based on severity
    finding.first_seen = current_datetime
    finding.last_seen = current_datetime
    finding.issue_title = issue_title
    finding.issue_type = "Risk"
    finding.date_created = generated_date
    finding.date_last_updated = updated_date
    finding.due_date = issue_due_date(severity, generated_date)
    finding.external_id = f"{cci_ref}:{vuln_num}:{finding.asset_identifier}"
    finding.recommendation_for_mitigation = solution
    finding.cci_ref = cci_ref
    finding.rule_id = rule_id
    finding.results = results
    finding.baseline = baseline
    finding.vulnerability_number = vuln_num
    finding.oval_def = oval_def
    finding.scan_date = scan_date
    finding.rule_id_full = rule_id_full
    finding.group_id = group_id

    # Future values
    # finding.comments = ""
    # finding.poam_comments = ""
    # finding.rule_version = ""

    return finding
