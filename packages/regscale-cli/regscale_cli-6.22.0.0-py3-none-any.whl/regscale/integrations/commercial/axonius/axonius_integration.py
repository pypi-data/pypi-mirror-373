#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Axonius integration for RegScale CLI to sync assets"""

# Standard python imports
import click
from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    compute_hashes_in_directory,
    convert_datetime_to_regscale_string,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    save_data_to,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models.file import File
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.task import Task
from regscale.utils.threading.threadhandler import create_threads, thread_assignment
from regscale.models import regscale_ssp_id

import pandas as pd
import requests
import datetime
from datetime import date
import warnings
import json
from urllib.parse import urljoin

warnings.filterwarnings("ignore")


####################################################################################################
#
# SYNC ASSETS WITH AXONIUS
# AXONIUS API Docs: https://developer.axonius.com/docs/overview
#
####################################################################################################


# Create group to handle Axonius integration
@click.group()
def axonius():
    """Sync assets between Axonius and RegScale."""


@axonius.command(name="sync_assets")
@regscale_ssp_id()
def sync_assets(regscale_ssp_id: int) -> None:
    """Sync Assets from Axonius into RegScale."""
    from regscale.models.integration_models.axonius_models.connectors.assets import AxoniusIntegration

    scanner = AxoniusIntegration(plan_id=regscale_ssp_id)
    scanner.sync_assets(plan_id=regscale_ssp_id)


@axonius.command(name="sync_findings")
@regscale_ssp_id()
def sync_findings(regscale_ssp_id: int) -> None:
    """Sync Assets from Axonius into RegScale."""
    from regscale.models.integration_models.axonius_models.connectors.assets import AxoniusIntegration

    scanner = AxoniusIntegration(plan_id=regscale_ssp_id)
    scanner.sync_findings(plan_id=regscale_ssp_id)
