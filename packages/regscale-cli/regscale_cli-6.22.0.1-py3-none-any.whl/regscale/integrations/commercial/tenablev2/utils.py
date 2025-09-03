"""
Tenable V2 Utils
"""

import datetime
from typing import List

from dateutil.relativedelta import relativedelta

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.utils.date import date_str, datetime_obj
from regscale.models import ScanHistory, regscale_models


def get_last_pull_epoch(regscale_ssp_id: int) -> int:
    """
    Gather last pull epoch from RegScale Security Plan

    :param int regscale_ssp_id: RegScale System Security Plan ID
    :return: Last pull epoch
    :rtype: int
    """
    two_months_ago = datetime.datetime.now() - relativedelta(months=2)
    two_weeks_ago = datetime.datetime.now() - relativedelta(weeks=2)
    last_pull = round(two_weeks_ago.timestamp())  # default the last pull date to two weeks

    # Limit the query with a filter_date to avoid taxing the database in the case of a large number of scans
    filter_date = date_str(two_months_ago)

    if res := ScanHistory.get_by_parent_recursive(
        parent_id=regscale_ssp_id, parent_module="securityplans", filter_date=filter_date
    ):
        # Sort by ScanDate desc
        res = sorted(res, key=lambda x: (datetime_obj(x.scanDate) or get_current_datetime()), reverse=True)
        # Convert to timestamp
        last_pull = round(datetime_obj(res[0].scanDate).timestamp()) if res else 0

    return last_pull


def get_filtered_severities() -> List[regscale_models.IssueSeverity]:
    """
    Return a list of severities that we want from Tenable

    :return: A list of severities
    :rtype: List[regscale_models.IssueSeverity]
    """
    app = Application()
    severity_filter = app.config.get("tenableMinimumSeverityFilter", "low").lower()
    severity_map = {
        "info": [
            regscale_models.IssueSeverity.NotAssigned,
            regscale_models.IssueSeverity.Low,
            regscale_models.IssueSeverity.Moderate,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
        "low": [
            regscale_models.IssueSeverity.Low,
            regscale_models.IssueSeverity.Moderate,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
        "moderate": [
            regscale_models.IssueSeverity.NotAssigned,
            regscale_models.IssueSeverity.Moderate,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
        "medium": [
            regscale_models.IssueSeverity.NotAssigned,
            regscale_models.IssueSeverity.Moderate,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
        "high": [
            regscale_models.IssueSeverity.NotAssigned,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
        "critical": [
            regscale_models.IssueSeverity.NotAssigned,
            regscale_models.IssueSeverity.Critical,
        ],
    }
    return severity_map.get(
        severity_filter,
        [
            regscale_models.IssueSeverity.Low,
            regscale_models.IssueSeverity.Moderate,
            regscale_models.IssueSeverity.High,
            regscale_models.IssueSeverity.Critical,
        ],
    )
