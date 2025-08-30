"""Assets Connector Model"""

from typing import Iterator, Optional
import pandas as pd
import datetime
from datetime import date
import warnings
import json
import re

from pydantic import ConfigDict

from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
    ScannerIntegrationType,
)
from regscale.models.regscale_models import IssueSeverity, AssetStatus, ControlImplementation, SecurityControl
from regscale.core.app.api import Api
from regscale.core.app.application import Application


class AxoniusIntegration(ScannerIntegration):
    from regscale.integrations.variables import ScannerVariables

    title = "Axonius"
    # Required fields from ScannerIntegration
    asset_identifier_field = "otherTrackingNumber"
    finding_severity_map = {
        "I": IssueSeverity.Critical,
        "II": IssueSeverity.High,
        "III": IssueSeverity.Moderate,
        "IV": IssueSeverity.Low,
    }
    type = (
        ScannerIntegrationType.CHECKLIST
        if ScannerVariables.complianceCreation.lower() == "assessment"
        else ScannerIntegrationType.CONTROL_TEST
    )
    app = Application()

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from Axonius

        :yields: Iterator[IntegrationAsset]
        """

        # TEST: Parse Sample Axonius Object
        axonius_object = pd.read_json("regscale/integrations/commercial/axonius/sample_axonius_object.json")

        for ind, asset in axonius_object.iterrows():
            integration_asset = IntegrationAsset(
                name=asset["hostname"],
                identifier=asset.COMPLIANCE_TABLE[0]["FISMA"],
                serial_number=asset["serial"],
                ip_address=asset["ip"],
                status=AssetStatus.Active,
                asset_category="Software",
                asset_type="Other",
            )
            yield integration_asset

    def fetch_findings(self, plan_id: int, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Unused method, but required by the parent class

        :yields: Iterator[IntegrationFinding]

        """
        # TEST: Parse Sample Axonius Object
        axonius_object = pd.read_json("regscale/integrations/commercial/axonius/sample_axonius_object.json")

        for ind, asset in axonius_object.iterrows():
            for finding in asset.COMPLIANCE_TABLE:
                if finding["ComplianceResult"] != "PASSED":

                    # Look for Control Title, Otherwise use Control ID
                    existing_implementations = ControlImplementation.get_list_by_parent(
                        regscale_id=plan_id, regscale_module="securityplans"
                    )
                    finding_control = re.search("[A-Z]{2}-\d+\d?(\(\d+\d?\))?", str(finding["800-53r5"]))[  # noqa: W605
                        0
                    ].lower()
                    try:
                        control_title = [
                            control
                            for control in existing_implementations
                            if control["controlId"].lower() == finding_control
                        ][0]["title"]
                    except Exception:
                        control_title = finding["800-53r5"]

                    integration_finding = IntegrationFinding(
                        title=f"Assessment Failure for Control ID: {control_title}",
                        asset_identifier=finding["FISMA"],
                        severity=self.finding_severity_map.get(finding["SEV"], IssueSeverity.NotAssigned),
                        identification="Security Control Assessment",
                        source_report="Axonius",
                        status="Open",
                        description=f"Issue for {finding['PLUGIN']}",
                        plugin_name=finding["PLUGIN"],
                        category="Other",
                        control_labels=[finding["800-53r5"]],
                        security_check=f"<strong>PLUGIN: </strong>{finding['PLUGIN']}<br><br><strong>FISMA: </strong>{finding['FISMA']}<br><br><strong>Compliance Result: </strong>{finding['ComplianceResult']}<br><br><strong>CCI: </strong>{finding['CCI']}<br><br><strong>800-53r5: </strong>{finding['800-53r5']}<br><br><strong>CSF: </strong>{finding['CSF']}<br><br><strong>VULID: </strong>{finding['VULID']}<br><br><strong>STIG: </strong>{finding['STIG']}",
                        baseline=finding["STIG"],
                        results=finding["ComplianceResult"],
                        affected_controls=finding["800-53r5"],
                    )
                    yield integration_finding
