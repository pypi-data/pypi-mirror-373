import pytest

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.issue import Issue, IssueSeverity, IssueStatus


def test_bad_issue_instance():
    issue = Issue(
        id=1,
        title="Test Issue",
        severityLevel=IssueSeverity.NotAssigned,
        status=IssueStatus.Draft,
        description="This is a test issue",
        parentId=1,
        parentModule="securityplans",
        pluginId=1,
        dateCreated=get_current_datetime(),
    )
    # Assert issue.model_fields_set raises an AttributeError
    with pytest.raises(AttributeError):
        issue.model_fields_set


def test_good_issue_instance():
    issue = Issue(
        id=1,
        title="Test Issue",
        severityLevel=IssueSeverity.NotAssigned,
        status=IssueStatus.Draft,
        description="This is a test issue",
        parentId=1,
        parentModule="securityplans",
        pluginId=str(1),
        dateCreated=get_current_datetime(),
    )
    assert isinstance(issue, Issue)
