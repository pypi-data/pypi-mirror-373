import unittest
from typing import List, Iterator
from unittest.mock import MagicMock

import freezegun
import pytest

from regscale.core.utils.date import date_str, get_day_increment
from regscale.integrations.scanner_integration import (
    ScannerIntegration,
    ScannerIntegrationType,
    IntegrationAsset,
    IntegrationFinding,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import regscale_models
from regscale.models.regscale_models.regscale_model import RegScaleModel

TEST_TIME = "2024-08-06 14:17:06"


def create_test_assets():
    """
    Create test assets.
    """
    for i in range(1, 3):
        regscale_models.Asset(
            id=i,
            name=f"New Asset {i}",
            otherTrackingNumber=f"new_asset{i}",
            assetType="Server",
            assetCategory="Physical",
            assetOwnerId="test_owner",
            status="Active (On Network)",
            parentModule="securityplans",
            parentId=1,
        ).create()


class TestScannerIntegration(ScannerIntegration):
    """
    A concrete implementation of ScannerIntegration for testing purposes.
    """

    title = "Test Scanner"
    asset_identifier_field = "otherTrackingNumber"
    type = ScannerIntegrationType.VULNERABILITY

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetch mock assets for testing.

        :param args: Variable length argument list
        :param kwargs: Arbitrary keyword arguments
        :return: An iterator of IntegrationAsset objects
        """
        assets = [
            IntegrationAsset(
                identifier=f"new_asset{i}",
                name=f"New Asset {i}",
                asset_type="Server",
                asset_category="Physical",
                software_inventory=[],
                ports_and_protocols=[],
                source_data={"key": "value"},
                asset_owner_id="test_owner",
                url="http://example.com",
            )
            for i in range(1, 3)
        ]
        return iter(assets)

    def fetch_findings(self, *args, **kwargs) -> List[IntegrationFinding]:
        """
        Fetch mock findings for testing.

        :rtype: List[IntegrationFinding]
        :return: A list of IntegrationFinding objects
        """
        return [
            IntegrationFinding(
                title=f"Test Finding {i}",
                asset_identifier=f"new_asset{i}",
                description="This is a test finding description",
                external_id=f"FINDING-00{i}",
                remediation="Apply the latest security patch",
                control_labels=[],
                category="Vulnerability",
                severity=regscale_models.IssueSeverity.High,
                status=regscale_models.IssueStatus.Open,
                cve="CVE-2023-12345",
                first_seen=TEST_TIME,
                last_seen=TEST_TIME,
                plugin_name="Testing Issue Creation",
            )
            for i in range(1, 3)
        ]

    @staticmethod
    def mark_asset_inactive(asset: regscale_models.Asset) -> None:
        """
        Mark an asset as inactive.

        :param regscale_models.Asset asset: The asset to mark as inactive
        """
        asset.status = "Inactive"
        asset.save()


@pytest.fixture(autouse=True)
def setup_scanner(mock_regscale_models) -> TestScannerIntegration:
    """
    Fixture to set up a TestScannerIntegration instance for testing.

    :param MagicMock mock_regscale_models: Mocked RegScaleModel
    :rtype: TestScannerIntegration
    :return: A configured TestScannerIntegration instance
    """
    RegScaleModel.clear_cache()
    create_test_assets()
    scanner = TestScannerIntegration(plan_id=1)
    scanner.regscale_version = "5.64.0"
    return scanner


class TestVulnerabilityScanning:
    """
    Test class for vulnerability scanning functionality.
    """

    def test_sync_assets(self, mock_regscale_models, setup_scanner):
        """
        Test the sync_assets method of the scanner.

        :param MagicMock mock_regscale_models: Mocked RegScaleModel
        :param TestScannerIntegration setup_scanner: Configured TestScannerIntegration instance
        """
        # COVERED: The sync_assets method calls instance.update_regscale_assets(assets=assets),
        # which handles asset creation for non-existent assets.
        scanner = setup_scanner

        # Call the sync_assets method
        processed_assets_count = scanner.sync_assets(plan_id=1)

        # Verify that two assets were processed
        assert processed_assets_count == 2

        assets: List[regscale_models.Asset] = regscale_models.Asset.get_all_by_parent(
            parent_id=1, parent_module=regscale_models.SecurityPlan.get_module_string()
        )
        assert len(assets) == 2
        created_asset = assets[0]

        # Check that the asset was created with the correct values
        assert created_asset == regscale_models.Asset(
            id=created_asset.id,
            name="New Asset 1",
            otherTrackingNumber="new_asset1",
            assetType="Server",
            assetCategory="Physical",
            assetOwnerId="test_owner",
            status="Active (On Network)",
            parentModule="securityplans",
            parentId=created_asset.parentId,
        )

    @freezegun.freeze_time(TEST_TIME)
    @pytest.mark.parametrize(
        "issue_creation,vulnerability_creation,expected_issue_count,expected_poam,expected_second_asset_issues",
        [
            ("PerAsset", "IssueCreation", 2, False, 1),
            ("Consolidated", "PoamCreation", 1, True, 0),
        ],
    )
    def test_sync_findings(
        self,
        mock_regscale_models,
        setup_scanner,
        issue_creation,
        vulnerability_creation,
        expected_issue_count,
        expected_poam,
        expected_second_asset_issues,
    ):
        """
        Test the sync_findings method with different configurations.

        :param MagicMock mock_regscale_models: Mocked RegScaleModel
        :param TestScannerIntegration setup_scanner: Configured TestScannerIntegration instance
        :param str issue_creation: The issue creation strategy
        :param str vulnerability_creation: The vulnerability creation strategy
        :param int expected_issue_count: The expected number of issues created
        :param bool expected_poam: Whether the created issue should be a POAM
        :param int expected_second_asset_issues: The expected number of issues for the second asset
        """
        # COVERED: This test checks the creation of a scan history per import,
        # creation of vulnerabilities for each finding as a child of the affected asset,
        # and creation of issues per unique asset / vulnerability pair.
        ScannerVariables.issueCreation = issue_creation
        ScannerVariables.vulnerabilityCreation = vulnerability_creation
        scanner = setup_scanner

        # Call the sync_findings method
        processed_findings_count = scanner.sync_findings(plan_id=1)

        # Verify that two findings were processed
        assert processed_findings_count == 2

        # Check that a scan history was created
        scan_histories: List[regscale_models.ScanHistory] = regscale_models.ScanHistory.get_all_by_parent(
            parent_id=1, parent_module=regscale_models.SecurityPlan.get_module_string()
        )
        assert len(scan_histories) == 1
        created_scan_history = scan_histories[0]

        assert created_scan_history == regscale_models.ScanHistory(
            id=created_scan_history.id,
            scanDate=created_scan_history.scanDate,
            scanningTool="Test Scanner",
            parentModule="securityplans",
            parentId=1,
        )

        # Check that a vulnerability was created
        vulnerabilities: List[regscale_models.Vulnerability] = regscale_models.Vulnerability.get_all_by_parent(
            parent_id=1, parent_module=regscale_models.SecurityPlan.get_module_string()
        )
        assert len(vulnerabilities) == 1
        for vulnerability in vulnerabilities:
            if vulnerability.title == "Test Finding 2":
                created_vulnerability = vulnerability
                break

        assert created_vulnerability == regscale_models.Vulnerability(  # type: ignore
            id=created_vulnerability.id,
            title="Test Finding 2",
            description="This is a test finding description",
            severity=regscale_models.VulnerabilitySeverity.High,
            status=regscale_models.VulnerabilityStatus.Open,
            parent_id=1,
            parent_module=regscale_models.SecurityPlan.get_module_string(),
            dns="unknown",
            cve="CVE-2023-12345",
            plugInName="CVE-2023-12345",
            plugInText="",
            scan_id=created_scan_history.id,
            last_seen=TEST_TIME,
            first_seen=TEST_TIME,
            plug_in_name="CVE-2023-12345",
            plug_in_text="",
        )

        # Check that issues were created as expected
        total_issues = 0
        assets: List[regscale_models.Asset] = regscale_models.Asset.get_all_by_parent(
            parent_id=1, parent_module=regscale_models.SecurityPlan.get_module_string()
        )
        for asset in assets:
            issues: List[regscale_models.Issue] = regscale_models.Issue.get_all_by_parent(
                parent_id=asset.id, parent_module="assets"
            )
            total_issues += len(issues)

        assert total_issues == expected_issue_count

        # Get the first created issue for further checks
        first_asset_issues: List[regscale_models.Issue] = (
            regscale_models.Issue.get_all_by_parent(parent_id=assets[0].id, parent_module="assets") if assets else []
        )
        created_issue = first_asset_issues[0] if first_asset_issues else None

        expected_asset_identifier = "new_asset1\nnew_asset2" if issue_creation == "Consolidated" else "new_asset1"
        expected_other_identifier = (
            "1:CVE-2023-12345" if issue_creation == "Consolidated" else "1:CVE-2023-12345:new_asset1"
        )

        if created_issue:
            assert created_issue == regscale_models.Issue(
                id=created_issue.id,
                title="Test Finding 1",
                severityLevel=regscale_models.IssueSeverity.High,
                issueOwnerId=scanner.get_assessor_id(),
                dueDate=date_str(get_day_increment(TEST_TIME, 60)),
                identification="Vulnerability Assessment",
                sourceReport="Test Scanner",
                description="This is a test finding description",
                status="Open",
                securityPlanId=1,
                cve="CVE-2023-12345",
                assetIdentifier=expected_asset_identifier,
                dateFirstDetected=TEST_TIME,
                parentId=assets[0].id,
                parentModule="assets",
                dateLastUpdated=TEST_TIME,
                securityChecks="FINDING-001",
                recommendedActions="",
                isPoam=expected_poam,
                otherIdentifier=expected_other_identifier,
                remediationDescription="",
                vulnerabilityId=created_vulnerability.id,
            )

        # Check issues for the second asset
        second_asset_issues: List[regscale_models.Issue] = regscale_models.Issue.get_all_by_parent(
            parent_id=assets[1].id, parent_module="assets"
        )
        assert len(second_asset_issues) == expected_second_asset_issues

    # NOTE: To fully confirm coverage of all test cases, additional tests may be needed to check:
    # - Closing of vulnerabilities that no longer exist in the scan
    # - Updating of existing issues when findings change
    # - Closing of issues that are no longer in the scan
    # - Handling of different vulnerability creation and issue creation configurations


if __name__ == "__main__":
    unittest.main()
