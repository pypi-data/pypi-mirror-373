#!/usr/bin/env python

import pytest

from regscale.integrations.scanner_integration import issue_due_date
from regscale.models import regscale_models


def test_issue_due_date():
    # Test data
    created_date = "2023-01-01"
    severity = regscale_models.IssueSeverity.High
    title = "test_integration"
    config = {"issues": {"test_integration": {"high": 1, "moderate": 2, "low": 3}}}

    # Expected due date
    expected_due_date = "2023-01-02"

    # Call the function
    result = issue_due_date(severity, created_date, title=title, config=config)

    # Assert the result
    assert result == expected_due_date

    # Test with low value
    severity = regscale_models.IssueSeverity.Low
    expected_due_date = "2023-01-04"
    result = issue_due_date(severity, created_date, title=title, config=config)
    assert result == expected_due_date

    # Test with defaults
    severity = regscale_models.IssueSeverity.Moderate
    expected_due_date = "2023-05-01"
    result = issue_due_date(severity, created_date)
    assert result == expected_due_date

    # Test with no matching title in config
    severity = regscale_models.IssueSeverity.Low
    title = "Nonexistent_Integration"
    expected_due_date = "2023-12-31"  # 364 days is the default
    result = issue_due_date(severity=severity, created_date=created_date, title=title, config=config)
    assert result == expected_due_date


if __name__ == "__main__":
    pytest.main()
