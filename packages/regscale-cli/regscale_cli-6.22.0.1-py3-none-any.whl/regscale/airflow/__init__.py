"""Provide Airflow integrations with RegScale."""

try:
    import airflow
except ImportError:
    raise ImportError(
        "The 'apache-airflow' package is required for using regscale.airflow. "
        "To install it, run: `pip install regscale-cli[airflow]`"
    )
