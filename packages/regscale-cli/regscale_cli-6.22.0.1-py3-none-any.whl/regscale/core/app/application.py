#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Configuration"""

import contextlib
import inspect
import json
import os
import platform
import sys
from threading import Lock
from typing import Any, Optional, Union
from urllib.parse import urljoin

import requests
import yaml
from pydantic import Field
from requests import Response
from yaml.scanner import ScannerError

from regscale.core.app.internal.encrypt import IOA21H98
from regscale.core.app.logz import create_logger
from regscale.utils.threading.threadhandler import ThreadManager

DEFAULT_CLIENT = "<myClientIdGoesHere>"
DEFAULT_SECRET = "<mySecretGoesHere>"
DEFAULT_POPULATED = "<createdProgrammatically>"
DEFAULT_TENANT = "<myTenantIdGoesHere>"


class Singleton(type):
    """
    Singleton class to prevent multiple instances of Application
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances or kwargs.get("config"):
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Application(metaclass=Singleton):
    """
    RegScale CLI configuration class

    :param Optional[dict] config: Configuration dictionary to use instead of init.yaml, defaults to None
    :param bool local_config: Whether to use the local config file, defaults to True
    """

    config: dict = Field(default_factory=dict)
    _config_lock = Lock()

    def __init__(
        self,
        config: Optional[dict] = None,
        local_config: bool = True,
    ):
        self.config_file = os.getenv("REGSCALE_CONFIG_FILE", "init.yaml")
        self.api_handler = None
        template = {
            "stigBatchSize": 100,
            "adAccessToken": DEFAULT_POPULATED,
            "adAuthUrl": "https://login.microsoftonline.com/",
            "adClientId": DEFAULT_CLIENT,
            "adClientSecret": DEFAULT_SECRET,
            "adGraphUrl": "https://graph.microsoft.com/.default",
            "adTenantId": DEFAULT_TENANT,
            "assessmentDays": 10,
            "azure365AccessToken": DEFAULT_POPULATED,
            "azure365ClientId": DEFAULT_CLIENT,
            "azure365Secret": DEFAULT_SECRET,
            "azure365TenantId": DEFAULT_TENANT,
            "azureCloudAccessToken": DEFAULT_POPULATED,
            "azureCloudClientId": DEFAULT_CLIENT,
            "azureCloudSecret": DEFAULT_SECRET,
            "azureCloudTenantId": DEFAULT_TENANT,
            "azureCloudSubscriptionId": "<mySubscriptionIdGoesHere>",
            "cisaKev": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            "crowdstrikeClientId": DEFAULT_CLIENT,
            "crowdstrikeClientSecret": DEFAULT_SECRET,
            "crowdstrikeBaseUrl": "<crowdstrikeApiUrl>",
            "csamToken": DEFAULT_SECRET,
            "csamURL": "<myCSAMURLgoeshere>",
            "csamFilter": {},
            "dependabotId": "<myGithubUserIdGoesHere>",
            "dependabotOwner": "<myGithubRepoOwnerGoesHere>",
            "dependabotRepo": "<myGithubRepoNameGoesHere>",
            "dependabotToken": "<myGithubPersonalAccessTokenGoesHere>",
            "domain": "https://regscale.yourcompany.com/",
            "disableCache": False,
            "evidenceFolder": "./evidence",
            "passScore": 80,
            "failScore": 30,
            "gcpCredentials": "<path/to/credentials.json>",
            "gcpOrganizationId": "<000000000000>",
            "gcpProjectId": "<000000000000>",
            "gcpScanType": "<organization | project>",
            "githubDomain": "api.github.com",
            "issues": {
                "aqua": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,
                },
                "amazon": {
                    "high": 30,
                    "low": 365,
                    "moderate": 90,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,
                },
                "defender365": {
                    "high": 30,
                    "low": 365,
                    "moderate": 90,
                    "status": "Open",
                },
                "defenderCloud": {
                    "high": 30,
                    "low": 365,
                    "moderate": 90,
                    "status": "Open",
                },
                "defenderFile": {
                    "high": 30,
                    "low": 365,
                    "moderate": 90,
                    "status": "Open",
                    "useKev": True,
                },
                "ecr": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,
                },
                "jira": {
                    "highest": 7,
                    "high": 30,
                    "medium": 90,
                    "low": 180,
                    "lowest": 365,
                    "status": "Open",
                },
                "qualys": {
                    "high": 30,
                    "moderate": 90,
                    "low": 365,
                    "status": "Open",
                    "useKev": True,
                },
                "salesforce": {
                    "critical": 7,
                    "high": 30,
                    "medium": 90,
                    "low": 365,
                    "status": "Open",
                },
                "snyk": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,  # Override the issue due date with the KEV date
                },
                "sonarcloud": {
                    "blocker": 7,
                    "critical": 30,
                    "major": 90,
                    "minor": 365,
                    "status": "Open",
                },
                "nexpose": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,  # Override the issue due date with the KEV date
                },
                "prisma": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,  # Override the issue due date with the KEV date
                },
                "tenable": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "useKev": False,  # Override the issue due date with the KEV date
                },
                "wiz": {
                    "critical": 30,
                    "high": 90,
                    "low": 365,
                    "medium": 90,
                    "status": "Open",
                },
                "xray": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": True,
                },
                "veracode": {
                    "critical": 30,
                    "high": 30,
                    "moderate": 90,
                    "low": 180,
                    "status": "Open",
                    "minimumSeverity": "low",
                    "useKev": False,
                },
            },
            "jiraApiToken": "<jiraAPIToken>",
            "jiraUrl": "<myJiraUrl>",
            "jiraUserName": "<jiraUserName>",
            "maxThreads": 1000,
            "nistCpeApiKey": "<myNistCpeApiKey>",
            "oktaApiToken": "Can be a SSWS token from Okta or created programmatically",
            "oktaClientId": "<oktaClientIdGoesHere>",
            "oktaUrl": "<oktaUrlGoesHere>",
            "oscalLocation": "/opt/OSCAL",
            "pwshPath": "/opt/microsoft/powershell/7/pwsh",
            "qualysUrl": "https://yourcompany.qualys.com/api/2.0/fo/scan/",
            "qualysUserName": "<qualysUserName>",
            "qualysPassword": "<qualysPassword>",
            "sicuraUrl": "<mySicuraUrl>",
            "sicuraToken": "<mySicuraToken>",
            "salesforceUserName": "<salesforceUserName>",
            "salesforcePassword": "<salesforcePassword>",
            "salesforceToken": "<salesforceSecurityToken>",
            "snowPassword": "<snowPassword>",
            "snowUrl": "<mySnowUrl>",
            "snowUserName": "<snowUserName>",
            "sonarUrl": "https://sonarcloud.io",
            "sonarToken": "<mySonarToken>",
            "tenableAccessKey": "<tenableAccessKeyGoesHere>",
            "tenableSecretKey": "<tenableSecretKeyGoesHere>",
            "tenableUrl": "https://sc.tenalab.online",
            "tenableMinimumSeverityFilter": "low",
            "token": DEFAULT_POPULATED,
            "userId": "enter RegScale user id here",
            "useMilestones": False,
            "otx": "enter AlienVault API key here",
            "wizAccessToken": DEFAULT_POPULATED,
            "wizAuthUrl": "https://auth.wiz.io/oauth/token",
            "wizExcludes": "My things to exclude here",
            "wizScope": "<filled out programmatically after authenticating to Wiz>",
            "wizUrl": "<my Wiz URL goes here>",
            "wizReportAge": 15,
            "wizLastInventoryPull": "<wizLastInventoryPull>",
            "wizInventoryFilterBy": "<wizInventoryFilterBy>",
            "wizIssueFilterBy": "<wizIssueFilterBy>",
            "wizFullPullLimitHours": 8,
            "wizStigMapperFile": os.path.join(
                os.getcwd(), os.makedirs("artifacts", exist_ok=True) or "artifacts/stig_mapper_rules.json"
            ),  # could blow up on missing artifacts folder
            "timeout": 60,
            "tenableGroupByPlugin": False,
            "findingFromMapping": {
                "aqua": {
                    "remediation": "default",
                    "title": "default",
                    "description": "default",
                },
                "tenable_sc": {
                    "remediation": "default",
                    "title": "default",
                    "description": "default",
                },
            },
        }
        logger = create_logger()
        if os.environ.get("LOGLEVEL", "INFO").upper() == "DEBUG":
            stack = inspect.stack()
            logger.debug("*" * 80)
            logger.debug(f"Initializing Application from {stack[1].filename}")
            logger.debug("*" * 80)
            logger.debug(f"Initializing in directory: {os.getcwd()}")
        self.template = template
        self.templated = False
        self.logger = logger
        self.local_config = local_config
        self.running_in_airflow = os.getenv("REGSCALE_AIRFLOW") == "true"
        if isinstance(config, str):
            config = self._read_config_from_str(config)
        if self.running_in_airflow:
            self.config = self._fetch_config_from_regscale(config)
        else:
            self.config = self._gen_config(config)
        self.os = platform.system()
        self.input_host = ""
        # Ensure maxThreads is an integer for ThreadManager
        max_threads = self.config.get("maxThreads", 100)
        if not isinstance(max_threads, int):
            logger.debug(f"maxThreads is not an integer: {max_threads} (type: {type(max_threads)})")
            try:
                max_threads = int(max_threads)
                logger.debug(f"Converted maxThreads to integer: {max_threads}")
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Failed to convert maxThreads '{max_threads}' to integer: {e}. Using default value 100."
                )
                max_threads = 100
        self.thread_manager = ThreadManager(max_threads)
        logger.debug("Finished Initializing Application")
        logger.debug("*" * 80)

    def __getitem__(self, key: Any) -> Any:
        """
        Get an item

        :param Any key: key to retrieve
        :return: value of provided key
        :rtype: Any
        """
        return self.config.__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set an item

        :param Any key: Key to set the provided value
        :param Any value: Value to set the provided key
        :rtype: None
        """
        self.config.__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        """
        Delete an item

        :param Any key: Key desired to delete
        :rtype: None
        """
        self.config.__delitem__(key)

    def __iter__(self):
        """
        Return iterator
        """
        return self.config.__iter__()

    def __len__(self) -> int:
        """
        Get the length of the config

        :return: # of items in config
        :rtype: int
        """
        return len(self.config) if self.config is not None else 0

    def __contains__(self, x: str) -> bool:
        """
        Check config if it contains string

        :param str x: String to check if it exists in the config
        :return: Whether the provided string exists in the config
        :rtype: bool
        """
        return self.config.__contains__(x)

    def _read_config_from_str(self, config: str) -> dict:
        """
        Tries to convert the provided config string to a dictionary, and if it fails, try to use the
        string as a file path, and if that fails it will return an empty dictionary

        :param str config: String to try and convert to a dictionary before trying to use as a file path
        :return: Dictionary of provided string or file, or an empty dictionary
        :rtype: dict
        """
        try:
            return json.loads(config)
        except json.JSONDecodeError:
            self.config_file = config
            try:
                config = self._get_conf()
                return config
            except Exception as ex:
                self.logger.debug(f"Unable to load config from file: {ex}")
                return {}

    def _fetch_config_from_regscale(self, config: Optional[dict] = None) -> dict:
        """
        Fetch config from RegScale via API

        :param Optional[dict] config: configuration dictionary, defaults to None
        :return: Combined config from RegScale and the provided config
        :rtype: dict
        """
        if config is None:
            config = {}
        self.logger.debug(f"Provided config in _fetch_config_from_regscale is: {type(config)}")
        token = config.get("token", os.getenv("REGSCALE_TOKEN"))
        domain = config.get("domain", os.getenv("REGSCALE_DOMAIN"))
        if domain is None or "http" not in domain or domain == self.template["domain"]:
            domain = self.retrieve_domain().rstrip("/")
        self.logger.debug(f"domain: {domain}, token: {token}")
        if domain is not None and token is not None:
            self.logger.info(f"Fetching config from {domain}...")
            try:
                response = requests.get(
                    url=urljoin(domain, "/api/tenants/getDetailedCliConfig"),
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": token,
                    },
                )
                self.logger.debug(f"status_code: {response.status_code} text: {response.text}")

                # Get the encrypted config from the response
                fetched_config = response.json()
                if not fetched_config or response.text == "":
                    self.logger.warning("No secrets found in %s", domain)
                    return {}
                # see if it's just a dictionary
                if isinstance(fetched_config, dict):
                    parsed_dict = fetched_config
                else:
                    decrypted_config = self._decrypt_config(fetched_config, token)
                    parsed_dict = json.loads(decrypted_config)

                parsed_dict["token"] = token
                parsed_dict["domain"] = domain
                from regscale.core.app.internal.login import parse_user_id_from_jwt

                parsed_dict["userId"] = parsed_dict.get("userId") or parse_user_id_from_jwt(self, token)
                self.logger.info("Successfully fetched config from RegScale.")
                # fill in any missing keys with the template
                return {**self.template, **parsed_dict}
            except Exception as ex:
                self.logger.error("Unable to fetch config from RegScale.\n%s", str(ex))
        return {}

    def _decrypt_config(self, encrypted_text: str, bearer_token: str) -> str:
        """
        Decrypt the configuration using AES encryption with the bearer token as key

        :param str encrypted_text: Base64 encoded encrypted text
        :param str bearer_token: Bearer token used as encryption key
        :return: Decrypted configuration string
        :rtype: str
        """
        import base64
        import hashlib
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        try:
            # Convert from base64
            combined = base64.b64decode(encrypted_text)

            # Extract IV (first 16 bytes) and cipher text
            iv = combined[:16]
            cipher_text = combined[16:]

            # Generate key from bearer token using SHA256
            key = hashlib.sha256(bearer_token.encode()).digest()

            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

            # Decrypt
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(cipher_text) + decryptor.finalize()

            # Remove padding and convert to string
            decoded = decrypted.decode("utf-8")
            # Remove all trailing whitespace and control characters
            cleaned = decoded.rstrip()
            # Also remove any trailing null bytes that might remain
            while cleaned.endswith("\0"):
                cleaned = cleaned[:-1]
            # Use regex to remove any ending backslash-like pattern and characters after it
            import re

            # Remove any trailing backslash followed by any characters until the end
            # This handles both literal backslashes and control characters like \x0e
            cleaned = re.sub(r"\\[^\\]*$", "", cleaned)
            # Also remove any trailing control characters that might remain
            # Avoid regex for trailing control character removal to prevent potential catastrophic backtracking.
            # Instead, use rstrip with a string of control characters.
            cleaned = cleaned.rstrip(
                "".join([chr(i) for i in range(0x00, 0x20)]) + "".join([chr(i) for i in range(0x7F, 0xA0)])
            )
            return cleaned
        except Exception as err:
            self.logger.error("Unable to decrypt config: %s", err)
            return "{}"

    def _load_config_from_click_context(self) -> Optional[dict]:
        """
        Load configuration from Click context

        :return: Configuration dictionary
        :rtype: Optional[dict]
        """
        try:
            import click

            ctx = click.get_current_context()
            if ctx and ctx.obj and "CONFIG" in ctx.obj:
                self.logger.debug("Found config in Click context...")
                if click_config := ctx.obj["CONFIG"]:
                    self.logger.debug("Using config from Click context")
                    config = self.verify_config(template=self.template, config=click_config)
                    self.save_config(config)
                    ctx.obj["CONFIG"] = config
                    return config
        except (RuntimeError, ImportError):
            # RuntimeError is raised when there's no active Click context
            # ImportError is raised if Click is not available
            pass
        return None

    def _gen_config(self, config: Optional[Union[dict, str]] = None) -> dict:
        """
        Generate the Application config from file or environment

        :param Optional[Union[dict, str]] config: Configuration dictionary, defaults to None
        :raises: TypeError if unable to generate config file
        :return: configuration as a dictionary
        :rtype: dict
        """
        # Check for Click context first
        if click_config := self._load_config_from_click_context():
            self.logger.debug("Successfully retrieved config from Click context.")
            return click_config

        try:
            if config and self.local_config:
                self.logger.debug(f"Config provided as :\n{type(config)}")
                file_config = config
            elif not self.local_config:
                file_config = {}
            else:
                file_config = self._get_conf() or {}
            # Merge
            env = self._get_env()
            if self.templated is False:
                self.logger.debug(f"Starting with {self.config_file}:{len(file_config)} and merging environment.")
                config = {**file_config, **env}
            else:
                self.logger.debug(
                    f"Starting with config from environment and merging {self.config_file}:{len(file_config)}."
                )
                config = {**env, **file_config}
        except ScannerError:
            config = self.template
        except TypeError:
            self.logger.error(f"ERROR: {self.config_file} has been encrypted! Please decrypt it before proceeding.\n")
            IOA21H98(self.config_file)
            sys.exit()
        if config is not None:
            # verify keys aren't null and the values are the expected data type
            config = self.verify_config(template=self.template, config=config)
            self.save_config(config)
        # Return config
        return config

    def _get_airflow_config(self, config: Optional[Union[dict, str]] = None) -> Optional[dict]:
        """
        Get config from Airflow DAG config, or from the environment variables if not provided.

        :param Optional[Union[dict, str]] config: Configuration dictionary, defaults to None
        :return: Configuration dictionary
        :rtype: Optional[dict]
        """
        if config:
            self.logger.debug(f"Received config from Airflow as: {type(config)}")
            # check to see if config is a string because airflow can pass a string instead of a dict
            try:
                config = json.loads(config.replace("'", '"')) if isinstance(config, str) else config
            except json.JSONDecodeError:
                return None
            if isinstance(config, dict):
                config = self._fetch_config_from_regscale(config=config)
            if isinstance(config, str):
                config = self._read_config_from_str(config)
            return config
        elif os.getenv("REGSCALE_TOKEN") and os.getenv("REGSCALE_DOMAIN"):
            self.logger.debug("No config provided, fetching from RegScale via api.")
            return self._fetch_config_from_regscale(
                config={
                    "token": os.getenv("REGSCALE_TOKEN"),
                    "domain": os.getenv("REGSCALE_DOMAIN"),
                }
            )
        return config or None

    def _get_env(self) -> dict:
        """
        return dict of RegScale keys from system

        :return: Application config
        :rtype: dict
        """
        all_keys = self.template.keys()
        sys_keys = [key for key in os.environ if key in all_keys]
        #  Update Template
        dat = {}
        try:
            dat = self.template.copy()
            for k in sys_keys:
                dat[k] = os.environ[k]
        except KeyError as ex:
            self.logger.error("Key Error!!: %s", ex)
        self.logger.debug("dat: %s", dat)
        self.templated = dat == self.template
        return dat

    def _get_conf(self) -> dict:
        """
        Get configuration from init.yaml if exists

        :return: Application config
        :rtype: dict
        """
        config = None
        # load the config from YAML
        with self._config_lock:  # Acquire the lock
            try:
                with open(self.config_file, encoding="utf-8") as stream:
                    self.logger.debug(f"Loading {self.config_file}")
                    config = yaml.safe_load(stream)
            except FileNotFoundError as ex:
                self.logger.debug(
                    "%s!\n This RegScale CLI application will create the %s file in the current working directory.",
                    ex,
                )
            finally:
                self.logger.debug("_get_conf: %s, %s", config, type(config))
        return config

    def save_config(self, conf: dict) -> None:
        """
        Save Configuration to init.yaml

        :param dict conf: Application configuration
        :rtype: None
        """
        self.config = conf
        if self.api_handler is not None:
            self.api_handler.config = conf
            self.api_handler.domain = conf.get("domain") or self.retrieve_domain()
        if self.running_in_airflow:
            self.logger.debug(
                f"Updated config and not saving to {self.config_file} because CLI is running in an Airflow container."
            )
            return None
        try:
            self.logger.debug(f"Saving config to {self.config_file}.")
            with self._config_lock:
                with open(self.config_file, "w", encoding="utf-8") as file:
                    yaml.dump(conf, file)
        except OSError:
            self.logger.error(f"Could not save config to {self.config_file}.")

    # Has to be Any class to prevent circular imports
    def get_regscale_license(self, api: Any) -> Optional[Response]:
        """
        Get RegScale license of provided application via provided API object

        :param Any api: API object
        :return: API response, if successful or None
        :rtype: Optional[Response]
        """
        config = self.config or api.config
        if config is None and self.running_in_airflow:
            config = self._get_airflow_config()
        elif config is None:
            config = self._gen_config()
        domain = config.get("domain") or self.retrieve_domain()
        if domain.endswith("/"):
            domain = domain[:-1]
        with contextlib.suppress(requests.RequestException):
            return api.get(
                url=f"{domain}/api/config/getLicense".lower(),
            )
        return None

    def load_config(self) -> dict:
        """
        Load Configuration file: init.yaml

        :return: Dict of config
        :rtype: dict
        """
        try:
            with self._config_lock:
                with open(self.config_file, "r", encoding="utf-8") as stream:
                    return yaml.safe_load(stream)
        except FileNotFoundError:
            return {}

    def retrieve_domain(self) -> str:
        """
        Retrieve the domain from the OS environment if it exists

        :return: The domain
        :rtype: str
        """
        self.logger.debug("Unable to determine domain, using retrieve_domain()...")
        # REGSCALE_DOMAIN is the default host
        for envar in ["REGSCALE_DOMAIN", "PLATFORM_HOST", "domain"]:
            if host := os.environ.get(envar):
                if host.startswith("http"):
                    self.logger.debug(f"Found {envar}={host} in environment.")
                    return host
        return "https://regscale.yourcompany.com/"

    def verify_config(self, template: dict, config: dict) -> dict:
        """
        Verify keys and value types in init.yaml while retaining keys in config that are not present in template

        :param dict template: Default template configuration
        :param dict config: Dictionary to compare against template
        :return: validated and/or updated config
        :rtype: dict
        """
        updated_config = config.copy()  # Start with a copy of the original config

        # Update or add template keys in config
        for key, template_value in template.items():
            config_value = config.get(key)

            # If key missing or empty, use template value
            if config_value is None or config_value == "":
                updated_config[key] = template_value
            # If value is a dict, recurse
            elif isinstance(template_value, dict):
                updated_config[key] = self.verify_config(template_value, config.get(key, {}))
            # If type mismatch, try to convert the value to the expected type
            elif not isinstance(config_value, type(template_value)):
                self.logger.debug(
                    f"Type mismatch for key '{key}': expected {type(template_value).__name__}, got {type(config_value).__name__} with value '{config_value}'"
                )
                try:
                    if isinstance(template_value, int):
                        updated_config[key] = int(config_value)
                        self.logger.debug(
                            f"Converted '{key}' from {type(config_value).__name__} to int: {config_value} -> {updated_config[key]}"
                        )
                    elif isinstance(template_value, float):
                        updated_config[key] = float(config_value)
                        self.logger.debug(
                            f"Converted '{key}' from {type(config_value).__name__} to float: {config_value} -> {updated_config[key]}"
                        )
                    elif isinstance(template_value, bool):
                        if isinstance(config_value, str):
                            updated_config[key] = config_value.lower() in ("true", "1", "yes", "on")
                        else:
                            updated_config[key] = bool(config_value)
                        self.logger.debug(
                            f"Converted '{key}' from {type(config_value).__name__} to bool: {config_value} -> {updated_config[key]}"
                        )
                    else:
                        # For other types, use template value as fallback
                        updated_config[key] = template_value
                        self.logger.debug(f"Using template value for '{key}': {template_value}")
                except (ValueError, TypeError) as e:
                    # If conversion fails, use template value
                    self.logger.warning(
                        f"Failed to convert '{key}' from '{config_value}' to {type(template_value).__name__}: {e}. Using template value: {template_value}"
                    )
                    updated_config[key] = template_value
            # Else, retain the config value
            else:
                updated_config[key] = config_value
        return updated_config
