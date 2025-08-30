"""Provide configurations for Airflow."""

from datetime import datetime, timedelta
from regscale.airflow.tasks.groups import email_on_fail


def yesterday():
    """Return yesterday from now in datetime"""
    return datetime.now() - timedelta(days=1)


DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    # 'start_date': (datetime.now() - timedelta(days=1)).date(),  # left here to show we intentionally disable
    "email": ["airflow@regscale.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(hours=3),
    "on_failure_callback": email_on_fail,
    # 'queue': 'whatever queue we want to implement',  # left here for an example
    # 'pool': 'backfill',  # another example default arg
    # 'priority_weight': 10,  # give this a high priority weight
    # 'end_date': datetime(2038, 1, 1),  # left to show that end dates can be set
}
