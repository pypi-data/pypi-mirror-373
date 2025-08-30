"""Test fixture class used during CLI testing"""

import logging
import os
import random
import sys
import uuid
from logging import Logger
from pathlib import Path
from typing import Optional, Union

import pytest
import yaml

from regscale.models import SecurityPlan, Assessment, Issue
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import login, parse_user_id_from_jwt, validate_user_id
from regscale.core.app.utils.app_utils import get_current_datetime
from tests.conftest_utils import INIT_CONF_PYTEST


class CLITestFixture:
    """
    Test fixture for the CLI application
    """

    app: Application
    api: Api
    config: dict
    logger: Logger
    title_prefix: str
    security_plan: SecurityPlan

    def update_config_with_env(self):
        """
        Update the Application.config values with the corresponding env values if both conditions are met:
        - the config value is the same as the template
        - the env value is not empty
        """
        key_env = {
            "domain": "REGSCALE_DOMAIN",
            "token": "REGSCALE_TOKEN",
            "jiraUrl": "JIRA_URL",
            "jiraUserName": "JIRA_USERNAME",
            "jiraApiToken": "JIRA_API_TOKEN",
            "wizClientId": "WIZCLIENTID",
            "wizClientSecret": "WIZCLIENTSECRET",
            "snowUrl": "SNOW_URL",
            "snowUserName": "SNOW_USERNAME",
            "snowPassword": "SNOW_PASSWORD",
            "sicuraUrl": "SICURA_URL",
            "sicuraToken": "SICURA_TOKEN",
            "nistCpeApiKey": "NIST_CPE_API_KEY",
            "qualysUserName": "QUALYS_USERNAME",
            "qualysPassword": "QUALYS_PASSWORD",
            "qualysUrl": "QUALYS_URL",
        }
        for key, env in key_env.items():
            config_value = self.app.config.get(key, "")
            template_value = self.app.template.get(key, "")
            env_value = os.getenv(env, "")
            self.app.config[key] = env_value if config_value == template_value and env_value else config_value

        hard_coded_test_values = {
            "gcpScanType": "organization",
            "gcpOrganizationId": "000000000000",
            "timeout": 360,
        }
        for key, value in hard_coded_test_values.items():
            self.app.config[key] = value

    def verify_config(self, config_key: Union[str, list[str]], compare_template: bool = True) -> None:
        """
        Verify the configuration values and compare them to the template

        :param Union[str, list[str]] config_key: Configuration key or list of keys to verify
        :param bool compare_template: Whether to compare the configuration values to the template, defaults to True
        :rtype: None
        """
        if isinstance(config_key, list):
            for key in config_key:
                self.verify_config(key, compare_template)
        else:
            assert self.app.config.get(config_key) is not None
            if compare_template:
                assert self.app.config.get(config_key) != self.app.template.get(config_key)

    @staticmethod
    def get_tests_dir(suffix: Optional[Union[str, Path]] = None) -> Path:
        """
        Get the current working directory

        :param Optional[Union[str, Path]] suffix: The suffix to append to the path, defaults to None
        :return: Path of the responses directory with a trailing slash
        :rtype: Path
        """
        cur_dir = Path(os.getcwd())
        if cur_dir.stem.lower() in ["commercial", "internal", "public"]:
            # get the repo root
            # EX: regscale-cli/tests/regscale/integrations/INTEGRATIONTYPE/test_name.py
            cwd = cur_dir.parent.parent.parent.parent
        elif cur_dir.stem.lower() == "tests":
            cwd = Path("../")
        else:
            cwd = Path(os.getcwd())
        return cwd / suffix if suffix else cwd

    @pytest.fixture(scope="session")
    def generate_uuid(self) -> str:
        """
        Generate a string with the python version and random UUID

        :return: A string with the python version and random UUID
        :rtype: str
        """
        python_info = f"Python{sys.version_info.major}.{sys.version_info.minor}"
        random_id = uuid.uuid1()
        return f"{python_info} Test {random_id}"

    @pytest.fixture(autouse=True)
    def cli_test_fixture(self, request, generate_uuid):
        """
        Test fixture for the CLI application

        :param request: Pytest request object
        :return: RegScale CLI Application object
        :rtype: Application
        """
        logger = logging.getLogger(__name__)
        logger.info("Test Setup")

        # Application is already set up, so we just need to update the config with the environment variables
        self.app = Application()
        self.app.local_config = False
        self.update_config_with_env()
        # Convert the INIT_CONF_PYTEST string into a dictionary
        config_dict = yaml.safe_load(INIT_CONF_PYTEST)
        test_config = {**config_dict, **self.app.config}
        self.app.save_config(test_config)
        self.config = self.app.config
        self.title_prefix = generate_uuid
        # login with token if available
        if token := os.getenv("REGSCALE_TOKEN") or self.config.get("token"):
            login(token=token, app=self.app)
        elif "REGSCALE_USERNAME" in os.environ and "REGSCALE_PASSWORD" in os.environ:
            login(
                str_user=os.getenv("REGSCALE_USERNAME"),
                str_password=os.getenv("REGSCALE_PASSWORD"),
                app=self.app,
            )
        self.api = Api()
        self.logger = logger

        logger.info(f"Test Setup Complete: {self.title_prefix}")
        # Test Execution
        yield self.app

    @pytest.fixture(scope="class")
    def create_security_plan(self, request, generate_uuid):
        """Create a security plan for testing"""
        security_plan = None
        try:
            ssp = SecurityPlan(
                systemName=generate_uuid,
                description="Test SSP",
            )
            security_plan = ssp.create()

            yield security_plan
        finally:
            # Cleanup after all tests in the class are done
            if security_plan:
                security_plan.delete()

    @pytest.fixture(scope="class")
    def create_assessment(self, request, generate_uuid, create_security_plan):
        """Create an assessment for testing"""
        assessment = None
        security_plan = create_security_plan

        app = Application()
        token = os.getenv("REGSCALE_TOKEN") or app.config.get("token")
        if not token:
            pytest.skip("No token found, skipping assessment creation")

        user_id = parse_user_id_from_jwt(app, token)

        if not validate_user_id(app, user_id):
            pytest.skip("Invalid user id, skipping assessment creation")

        try:
            assessment_obj = Assessment(
                parentId=security_plan.id,
                parentModule=security_plan.get_module_string(),
                title=generate_uuid,
                status="In Progress",
                leadAssessorId=user_id,
                assessmentType="Self",
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
            )
            assessment = assessment_obj.create()

            yield assessment
        finally:
            if assessment:
                assessment.delete()

    @pytest.fixture(scope="class")
    def create_issue(self, request, generate_uuid, create_security_plan):
        """Create an issue for testing"""
        issue = None
        security_plan = create_security_plan
        try:
            issue = Issue(
                parentId=security_plan.id,
                parentModule=security_plan.get_module_string(),
                title=generate_uuid,
                dueDate=get_current_datetime(),
                status="Open",
                description="Test Issue",
            )
            issue = issue.create()

            yield issue
        finally:
            if issue:
                issue.delete()
