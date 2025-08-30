"""Tasks for debugging purposes."""

import os
import logging


def set_logging():
    os.environ["LOGLEVEL"] = "DEBUG"
    logging.getLogger("airflow.task").setLevel(logging.DEBUG)
