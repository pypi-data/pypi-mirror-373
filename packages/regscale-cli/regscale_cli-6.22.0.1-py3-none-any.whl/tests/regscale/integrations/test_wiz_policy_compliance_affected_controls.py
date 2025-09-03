#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test affected controls functionality in Wiz Policy Compliance Integration.
"""

import pytest
from unittest.mock import patch, MagicMock

from regscale.integrations.commercial.wizv2.policy_compliance import WizPolicyComplianceIntegration
from regscale.integrations.compliance_integration import ComplianceItem
from regscale.models import regscale_models


class DummyItem(ComplianceItem):
    """Dummy compliance item for testing."""

    def __init__(self, rid: str, rname: str, cid: str, framework: str, result: str):
        self._rid = rid
        self._rname = rname
        self._cid = cid
        self._framework = framework
        self._result = result

    @property
    def resource_id(self) -> str:
        """Get resource ID."""
        return self._rid

    @property
    def resource_name(self) -> str:
        """Get resource name."""
        return self._rname

    @property
    def control_id(self) -> str:
        """Get control ID."""
        return self._cid

    @property
    def compliance_result(self) -> str:
        """Get compliance result."""
        return self._result

    @property
    def severity(self):
        """Get severity."""
        return "HIGH"

    @property
    def description(self) -> str:
        """Get description."""
        return "desc"

    @property
    def framework(self) -> str:
        """Get framework."""
        return self._framework


@pytest.mark.parametrize("control_id", ["AC-2(1)", "ac-2 (1)", "AC-2-1"])
@patch("regscale.integrations.commercial.wizv2.policy_compliance.wiz_authenticate")
@patch("regscale.integrations.commercial.wizv2.policy_compliance.check_license")
def test_issue_affected_controls_from_external_id(mock_check_license, mock_wiz_auth, monkeypatch, control_id):
    """Test that affected controls are properly set from normalized control IDs."""
    # Mock authentication to prevent 401 errors - using same pattern as main test file
    mock_app = MagicMock()
    mock_app.config = {"wizUrl": "https://api.wiz.io/graphql"}
    mock_check_license.return_value = mock_app
    mock_wiz_auth.return_value = "test-token"

    # Mock the base class methods that make API calls
    with patch.object(WizPolicyComplianceIntegration, "_load_existing_records_cache"), patch.object(
        WizPolicyComplianceIntegration, "get_asset_by_identifier", return_value=None
    ), patch.object(WizPolicyComplianceIntegration, "_ensure_asset_for_finding", return_value=None):

        integ = WizPolicyComplianceIntegration(
            plan_id=999,
            wiz_project_id="proj",
            client_id="cid",
            client_secret="secret",
            framework_id="wf-id-4",
        )
        integ.parent_module = regscale_models.SecurityPlan.get_module_string()

        # Create a minimal raw compliance node matching the selected framework
        raw_node = {
            "id": "node-1",
            "result": "FAIL",
            "policy": {
                "name": "Policy X",
                "securitySubCategories": [{"category": {"framework": {"id": "wf-id-4"}}}],
            },
            "resource": {"id": "asset-1", "name": "name", "type": "VM"},
        }

        comp_item = integ.create_compliance_item(raw_node)
        # Monkeypatch control id onto the item to simulate parsed control
        comp_item.policy = {
            "name": "Policy X",
            "securitySubCategories": [
                {
                    "externalId": control_id,
                    "category": {"framework": {"id": "wf-id-4"}},
                }
            ],
        }

        finding = integ.create_finding_from_compliance_item(comp_item)
        assert finding is not None

        # Ensure affected_controls on finding is set to normalized control ID
        expected_normalized = integ._normalize_control_id_string(control_id)
        assert (
            finding.affected_controls == expected_normalized
        ), f"Expected {expected_normalized}, got {finding.affected_controls}"

        # Mock the base class issue creation method more thoroughly
        with patch.object(
            WizPolicyComplianceIntegration, "_find_existing_issue_cached", return_value=None
        ), patch.object(
            WizPolicyComplianceIntegration, "_create_or_update_issue", return_value=None
        ) as mock_base_create:

            # Create a proper mock issue that behaves like the real Issue model
            mock_issue = MagicMock(spec=regscale_models.Issue)
            mock_issue.id = 123
            mock_issue.affectedControls = None
            mock_issue.assetIdentifier = finding.asset_identifier
            mock_issue.controlId = None
            mock_issue.assessmentId = None
            mock_issue.isPoam = False
            mock_issue.parentId = None
            mock_issue.parentModule = None

            # Make the base method return our mock issue
            mock_base_create.return_value = mock_issue

            # This should call the parent method and then apply post-processing
            with patch.object(
                WizPolicyComplianceIntegration.__bases__[0],
                "create_or_update_issue_from_finding",
                return_value=mock_issue,
            ):
                issue = integ.create_or_update_issue_from_finding(title=finding.title, finding=finding)

                # Verify we got our mock issue back
                assert issue is mock_issue

                # Verify the issue's affectedControls was set to the normalized control ID
                # (This gets set in the post-processing step of create_or_update_issue_from_finding)
                assert (
                    issue.affectedControls == expected_normalized
                ), f"Issue affectedControls should be {expected_normalized}, got {issue.affectedControls}"
