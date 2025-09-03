#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the _handle_property_and_milestone_creation method in ScannerIntegration.

This module provides comprehensive test coverage for the property and milestone creation
functionality in scanner integrations.
"""

import unittest
from typing import Iterator, Optional
from unittest.mock import MagicMock, patch, call

import pytest

from regscale.integrations.scanner_integration import (
    ScannerIntegration,
    ScannerIntegrationType,
    IntegrationFinding,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import regscale_models


class TestScannerIntegration(ScannerIntegration):
    """
    A concrete implementation of ScannerIntegration for testing purposes.
    """

    title = "Test Scanner"
    type = ScannerIntegrationType.VULNERABILITY

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """Mock implementation for testing."""
        return iter([])

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """Mock implementation for testing."""
        return iter([])


class TestPropertyAndMilestoneCreation:
    """
    Test cases for the _handle_property_and_milestone_creation method.

    This class provides comprehensive test coverage for all code paths in the method,
    including property creation for POC and CWE, and milestone creation for various
    issue status transitions.
    """

    @pytest.fixture(autouse=True)
    def setup_scanner(self) -> TestScannerIntegration:
        """
        Set up a test scanner instance with mocked dependencies.

        :return: Configured test scanner instance
        :rtype: TestScannerIntegration
        """
        scanner = TestScannerIntegration(plan_id=1, tenant_id=1)
        scanner.assessor_id = "test_assessor"
        scanner.scan_date = "2024-01-01 00:00:00"
        return scanner

    @pytest.fixture
    def mock_issue(self) -> MagicMock:
        """
        Create a mock issue for testing.

        :return: Mock issue object
        :rtype: MagicMock
        """
        issue = MagicMock(spec=regscale_models.Issue)
        issue.id = 123
        issue.status = regscale_models.IssueStatus.Open
        issue.dateCompleted = "2024-01-02 00:00:00"
        return issue

    @pytest.fixture
    def mock_finding(self) -> MagicMock:
        """
        Create a mock finding for testing.

        :return: Mock finding object
        :rtype: MagicMock
        """
        finding = MagicMock(spec=IntegrationFinding)
        finding.external_id = "test_external_id"
        finding.point_of_contact = None
        finding.is_cwe = False
        finding.plugin_id = "CWE-123"
        return finding

    @pytest.fixture
    def mock_property_class(self) -> MagicMock:
        """
        Create a mock Property class for testing.

        :return: Mock Property class
        :rtype: MagicMock
        """
        return MagicMock(spec=regscale_models.Property)

    @pytest.fixture
    def mock_milestone_class(self) -> MagicMock:
        """
        Create a mock Milestone class for testing.

        :return: Mock Milestone class
        :rtype: MagicMock
        """
        return MagicMock(spec=regscale_models.Milestone)

    def test_handle_property_and_milestone_creation_no_properties_no_milestones(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test when no properties or milestones should be created.

        This test covers the case where:
        - finding.point_of_contact is None
        - finding.is_cwe is False
        - ScannerVariables.useMilestones is False
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            mock_property_class.assert_not_called()
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_with_poc_property(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of POC property when point_of_contact is provided.

        This test covers the case where:
        - finding.point_of_contact has a value
        - finding.is_cwe is False
        - ScannerVariables.useMilestones is False
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding
        finding.point_of_contact = "test_poc@example.com"

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            mock_property_class.assert_called_once_with(
                key="POC",
                value="test_poc@example.com",
                parentId=123,
                parentModule="issues",
            )
            mock_property_class.return_value.create_or_update.assert_called_once()
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_with_cwe_property(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of CWE property when is_cwe is True.

        This test covers the case where:
        - finding.point_of_contact is None
        - finding.is_cwe is True
        - ScannerVariables.useMilestones is False
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding
        finding.is_cwe = True

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            mock_property_class.assert_called_once_with(
                key="CWE",
                value="CWE-123",
                parentId=123,
                parentModule="issues",
            )
            mock_property_class.return_value.create_or_update.assert_called_once()
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_with_both_properties(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of both POC and CWE properties.

        This test covers the case where:
        - finding.point_of_contact has a value
        - finding.is_cwe is True
        - ScannerVariables.useMilestones is False
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding
        finding.point_of_contact = "test_poc@example.com"
        finding.is_cwe = True

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            # Check that Property was called twice (once for each property)
            assert mock_property_class.call_count == 2

            # Check the first call (POC property)
            first_call = mock_property_class.call_args_list[0]
            assert first_call[1]["key"] == "POC"
            assert first_call[1]["value"] == "test_poc@example.com"
            assert first_call[1]["parentId"] == 123
            assert first_call[1]["parentModule"] == "issues"

            # Check the second call (CWE property)
            second_call = mock_property_class.call_args_list[1]
            assert second_call[1]["key"] == "CWE"
            assert second_call[1]["value"] == "CWE-123"
            assert second_call[1]["parentId"] == 123
            assert second_call[1]["parentModule"] == "issues"

            # Verify create_or_update was called for each property
            assert mock_property_class.return_value.create_or_update.call_count == 2
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_milestones_disabled(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test that milestones are not created when useMilestones is False.

        This test covers the case where:
        - ScannerVariables.useMilestones is False
        - All milestone creation logic should be skipped
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_issue_reopened_milestone(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of milestone when issue is reopened.

        This test covers the case where:
        - ScannerVariables.useMilestones is True
        - existing_issue.status is Closed
        - issue.status is Open
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        issue.status = regscale_models.IssueStatus.Open
        finding = mock_finding

        existing_issue = MagicMock(spec=regscale_models.Issue)
        existing_issue.status = regscale_models.IssueStatus.Closed

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch(
            "regscale.integrations.scanner_integration.get_current_datetime", return_value="2024-01-03 00:00:00"
        ), patch.object(
            ScannerVariables, "useMilestones", True
        ):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            mock_milestone_class.assert_called_once_with(
                title="Issue reopened from Test Scanner scan",
                milestoneDate="2024-01-03 00:00:00",
                responsiblePersonId="test_assessor",
                parentID=123,
                parentModule="issues",
            )
            mock_milestone_class.return_value.create_or_update.assert_called_once()

    def test_handle_property_and_milestone_creation_issue_closed_milestone(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of milestone when issue is closed.

        This test covers the case where:
        - ScannerVariables.useMilestones is True
        - existing_issue.status is Open
        - issue.status is Closed
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        issue.status = regscale_models.IssueStatus.Closed
        issue.dateCompleted = "2024-01-02 00:00:00"
        finding = mock_finding

        existing_issue = MagicMock(spec=regscale_models.Issue)
        existing_issue.status = regscale_models.IssueStatus.Open

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", True):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            mock_milestone_class.assert_called_once_with(
                title="Issue closed from Test Scanner scan",
                milestoneDate="2024-01-02 00:00:00",
                responsiblePersonId="test_assessor",
                parentID=123,
                parentModule="issues",
            )
            mock_milestone_class.return_value.create_or_update.assert_called_once()

    def test_handle_property_and_milestone_creation_new_issue_milestone(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test creation of milestone for a new issue.

        This test covers the case where:
        - ScannerVariables.useMilestones is True
        - existing_issue is None (new issue)
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", True):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            mock_milestone_class.assert_called_once_with(
                title="Issue created from Test Scanner scan",
                milestoneDate="2024-01-01 00:00:00",
                responsiblePersonId="test_assessor",
                parentID=123,
                parentModule="issues",
            )
            mock_milestone_class.return_value.create_or_update.assert_called_once()

    def test_handle_property_and_milestone_creation_no_milestone_created(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test case where no milestone is created due to status conditions.

        This test covers the case where:
        - ScannerVariables.useMilestones is True
        - existing_issue.status is Open
        - issue.status is Open (no status change)
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        issue.status = regscale_models.IssueStatus.Open
        finding = mock_finding

        existing_issue = MagicMock(spec=regscale_models.Issue)
        existing_issue.status = regscale_models.IssueStatus.Open

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", True):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            mock_milestone_class.assert_not_called()

    def test_handle_property_and_milestone_creation_comprehensive_scenario(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test comprehensive scenario with all properties and milestone creation.

        This test covers the case where:
        - finding.point_of_contact has a value
        - finding.is_cwe is True
        - ScannerVariables.useMilestones is True
        - Issue is being reopened (milestone creation)
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        issue.status = regscale_models.IssueStatus.Open
        finding = mock_finding
        finding.point_of_contact = "test_poc@example.com"
        finding.is_cwe = True

        existing_issue = MagicMock(spec=regscale_models.Issue)
        existing_issue.status = regscale_models.IssueStatus.Closed

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch(
            "regscale.integrations.scanner_integration.get_current_datetime", return_value="2024-01-03 00:00:00"
        ), patch.object(
            ScannerVariables, "useMilestones", True
        ):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            # Check that Property was called twice (once for each property)
            assert mock_property_class.call_count == 2

            # Check the first call (POC property)
            first_call = mock_property_class.call_args_list[0]
            assert first_call[1]["key"] == "POC"
            assert first_call[1]["value"] == "test_poc@example.com"
            assert first_call[1]["parentId"] == 123
            assert first_call[1]["parentModule"] == "issues"

            # Check the second call (CWE property)
            second_call = mock_property_class.call_args_list[1]
            assert second_call[1]["key"] == "CWE"
            assert second_call[1]["value"] == "CWE-123"
            assert second_call[1]["parentId"] == 123
            assert second_call[1]["parentModule"] == "issues"

            # Check milestone creation call
            mock_milestone_class.assert_called_once_with(
                title="Issue reopened from Test Scanner scan",
                milestoneDate="2024-01-03 00:00:00",
                responsiblePersonId="test_assessor",
                parentID=123,
                parentModule="issues",
            )

            # Verify create_or_update was called for all created objects
            assert mock_property_class.return_value.create_or_update.call_count == 2
            mock_milestone_class.return_value.create_or_update.assert_called_once()

    def test_handle_property_and_milestone_creation_with_logging(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test that logging occurs when properties and milestones are created.

        This test verifies that debug logging is called appropriately.
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding
        finding.point_of_contact = "test_poc@example.com"
        finding.is_cwe = True

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch("regscale.integrations.scanner_integration.logger") as mock_logger, patch.object(
            ScannerVariables, "useMilestones", True
        ):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            # Verify debug logging calls
            expected_log_calls = [
                call.debug("Added POC property %s to issue %s", "test_poc@example.com", 123),
                call.debug("Added CWE property %s to issue %s", "CWE-123", 123),
                call.debug("Created milestone for issue %s from finding %s", 123, "test_external_id"),
            ]
            mock_logger.assert_has_calls(expected_log_calls)

    def test_handle_property_and_milestone_creation_no_milestone_logging(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test logging when no milestone is created.

        This test verifies that the appropriate debug log is called when no milestone
        is created due to status conditions.
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        issue.status = regscale_models.IssueStatus.Open
        finding = mock_finding

        existing_issue = MagicMock(spec=regscale_models.Issue)
        existing_issue.status = regscale_models.IssueStatus.Open

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch("regscale.integrations.scanner_integration.logger") as mock_logger, patch.object(
            ScannerVariables, "useMilestones", True
        ):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            mock_logger.debug.assert_called_with(
                "No milestone created for issue %s from finding %s", 123, "test_external_id"
            )

    def test_handle_property_and_milestone_creation_edge_cases(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test edge cases and boundary conditions.

        This test covers various edge cases to ensure robust behavior.
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding

        # Test with empty string values
        finding.point_of_contact = ""
        finding.is_cwe = True

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", False):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            # Should only create CWE property (empty string is falsy for POC)
            mock_property_class.assert_called_once_with(
                key="CWE",
                value="CWE-123",
                parentId=123,
                parentModule="issues",
            )

    def test_handle_property_and_milestone_creation_with_none_values(
        self, setup_scanner, mock_issue, mock_finding, mock_property_class, mock_milestone_class
    ):
        """
        Test behavior with None values for optional fields.

        This test ensures the method handles None values gracefully.
        """
        # Arrange
        scanner = setup_scanner
        issue = mock_issue
        finding = mock_finding
        finding.point_of_contact = None
        finding.is_cwe = False
        finding.plugin_id = None

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch.object(ScannerVariables, "useMilestones", True):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding)

            # Assert
            # Should only create milestone (no properties due to None values)
            mock_property_class.assert_not_called()
            mock_milestone_class.assert_called_once()

    @pytest.mark.parametrize(
        "issue_status,existing_issue_status,expected_title,expected_date",
        [
            (
                regscale_models.IssueStatus.Open,
                regscale_models.IssueStatus.Closed,
                "Issue reopened from Test Scanner scan",
                "2024-01-03 00:00:00",
            ),
            (
                regscale_models.IssueStatus.Closed,
                regscale_models.IssueStatus.Open,
                "Issue closed from Test Scanner scan",
                "2024-01-02 00:00:00",
            ),
            (regscale_models.IssueStatus.Open, None, "Issue created from Test Scanner scan", "2024-01-01 00:00:00"),
        ],
    )
    def test_handle_property_and_milestone_creation_milestone_status_transitions(
        self,
        setup_scanner,
        mock_issue,
        mock_finding,
        mock_property_class,
        mock_milestone_class,
        issue_status,
        existing_issue_status,
        expected_title,
        expected_date,
    ):
        """
        Test all possible milestone status transitions.

        This test ensures all milestone creation scenarios are covered.
        """
        # Arrange
        scanner = setup_scanner
        finding = mock_finding

        # Reset mocks
        mock_property_class.reset_mock()
        mock_milestone_class.reset_mock()

        # Setup issue
        issue = mock_issue
        issue.status = issue_status

        # Setup existing issue if needed
        existing_issue = None
        if existing_issue_status is not None:
            existing_issue = MagicMock(spec=regscale_models.Issue)
            existing_issue.status = existing_issue_status

        with patch("regscale.integrations.scanner_integration.regscale_models.Property", mock_property_class), patch(
            "regscale.integrations.scanner_integration.regscale_models.Milestone", mock_milestone_class
        ), patch(
            "regscale.integrations.scanner_integration.get_current_datetime", return_value="2024-01-03 00:00:00"
        ), patch.object(
            ScannerVariables, "useMilestones", True
        ):

            # Act
            scanner._handle_property_and_milestone_creation(issue, finding, existing_issue)

            # Assert
            mock_milestone_class.assert_called_once_with(
                title=expected_title,
                milestoneDate=expected_date,
                responsiblePersonId="test_assessor",
                parentID=123,
                parentModule="issues",
            )
            mock_milestone_class.return_value.create_or_update.assert_called_once()
