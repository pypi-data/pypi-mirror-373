from __future__ import annotations

import datetime
import enum
import json
import logging
import random
import time
from functools import wraps
from typing import Optional, Dict, Any, Type, TypeVar, List, Union
from urllib.parse import urljoin, urlencode

import requests
from pydantic import BaseModel, Field, RootModel
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from regscale.integrations.commercial.sicura.variables import SicuraVariables

logger = logging.getLogger("regscale")


class SicuraProfile(str, enum.Enum):
    """Enum for Sicura scan profiles."""

    I_MISSION_CRITICAL_CLASSIFIED = "I - Mission Critical Classified"
    I_MISSION_CRITICAL_PUBLIC = "I - Mission Critical Public"
    I_MISSION_CRITICAL_SENSITIVE = "I - Mission Critical Sensitive"
    II_HIGH_IMPORTANCE_CLASSIFIED = "II - High Importance Classified"
    II_HIGH_IMPORTANCE_PUBLIC = "II - High Importance Public"
    II_HIGH_IMPORTANCE_SENSITIVE = "II - High Importance Sensitive"
    III_ADMINISTRATIVE_CLASSIFIED = "III - Administrative Classified"
    III_ADMINISTRATIVE_PUBLIC = "III - Administrative Public"
    III_ADMINISTRATIVE_SENSITIVE = "III - Administrative Sensitive"
    LEVEL_1_SERVER = "Level 1 - Server"


class SicuraModel(BaseModel):
    """Base model for Sicura API responses."""

    class Config:
        populate_by_name = True


class Device(SicuraModel):
    """Model for Sicura device information."""

    id: int = Field(None, alias="id")
    name: str = Field(..., alias="name")
    fqdn: str = Field(..., alias="fqdn")
    ip_address: Optional[str] = None
    platforms: str = ""
    scannable_profiles: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
    most_recent_scan: Optional[str] = None
    type: Optional[str] = None
    last_updated_time: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"


class PendingDevice(SicuraModel):
    """Model for a pending device waiting to be accepted."""

    id: int
    fqdn: str
    signature: str
    platform: str
    platform_title: str
    last_update: str
    ip_address: str
    rejected: bool

    class Config:
        populate_by_name = True
        extra = "allow"


def retry_with_backoff(retries=3, backoff_in_seconds=1):
    """
    Decorator for retrying a function with exponential backoff.

    :param int retries: Number of retries
    :param int backoff_in_seconds: Initial backoff time in seconds
    :return: Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (Timeout, RequestsConnectionError) as e:
                    if x == retries:
                        raise e
                    sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
                    time.sleep(sleep)
                    x += 1

        return wrapper

    return decorator


class AuthResponse(SicuraModel):
    """Model for authentication response."""

    token: str
    expires_at: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"


class ScanJob(SicuraModel):
    """Model for a Sicura scan job."""

    id: int = Field(..., alias="id")
    node_id: int = Field(..., alias="node_id")
    timestamp: str = Field(..., alias="timestamp")
    name: str = Field(..., alias="name")
    status_id: int = Field(..., alias="status_id")
    attributes: Dict[str, Any] = Field(default_factory=dict, alias="attributes")
    task_id: int = Field(..., alias="task_id")

    class Config:
        populate_by_name = True
        extra = "allow"


class ScanControl(RootModel):
    """Model for scan control data."""

    # Control fields are dynamic, allowing any key with boolean values
    root: Dict[str, bool] = Field(default_factory=dict)

    # RootModel doesn't support the extra option in Config
    # class Config:
    #     populate_by_name = True
    #     extra = "allow"


class ScanResult(SicuraModel):
    """Model for an individual scan result."""

    title: str
    ce_name: str
    result: str  # 'pass' or 'fail'
    description: str
    controls: Dict[str, bool]
    state: str
    state_reason: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "allow"


class ScanSummary(SicuraModel):
    """Model for scan summary statistics."""

    total: int
    pass_count: int = Field(alias="pass")
    fail: int
    pass_percentage: float

    class Config:
        populate_by_name = True
        extra = "allow"


class ScanReport(SicuraModel):
    """Model for a complete scan report."""

    device_id: int
    fqdn: str
    ip_address: Optional[str] = None
    scans: List[ScanResult]
    summary: ScanSummary

    class Config:
        populate_by_name = True
        extra = "allow"


SicuraModelType = TypeVar("SicuraModelType", bound=SicuraModel)


class SicuraAPI:
    """Methods to interact with Sicura API"""

    # Status ID mapping
    JOB_STATUS = {1: "QUEUED", 2: "RUNNING", 3: "COMPLETE", 4: "ERROR", 5: "CANCELLED", 6: "TIMEOUT"}

    # Filter parameter constants
    FILTER_FQDN = "filter[fqdn]"
    FILTER_IP_ADDRESS = "filter[ip_address]"
    FILTER_TYPE = "filter[type]"
    FILTER_REJECTED = "filter[rejected]"
    FILTER_TASK_ID = "filter[task_id]"
    csrf_token: Optional[str] = None

    def __init__(self):
        """
        Initialize Sicura API client.

        """
        from regscale.integrations.variables import ScannerVariables

        self.base_url = SicuraVariables.sicuraURL.rstrip("/")
        self.session = requests.Session()
        self.verify = ScannerVariables.sslVerify
        if not self.verify:
            logger.warning("SSL Verification has been disabled for Sicura API requests.")
            self.session.verify = False
            disable_warnings(InsecureRequestWarning)

    @retry_with_backoff(retries=3, backoff_in_seconds=1)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Optional[Union[dict, str]]:
        """
        Make a request to the Sicura API.

        :param str method: HTTP method
        :param str endpoint: API endpoint
        :param Optional[Dict[str, Any]] data: Request data
        :param Optional[Dict[str, Any]] params: Query parameters
        :param Optional[Dict[str, Any]] files: Files to upload
        :return: Response data or None if request failed
        :rtype: Optional[Union[dict, str]]
        """
        url = urljoin(self.base_url, endpoint)
        logger.debug(f"Making request with params: {url}?{urlencode(params) if params else ''}")
        logger.debug(f"Current session cookies: {json.dumps(dict(self.session.cookies), indent=2)}")

        if data:
            self.session.headers["Content-Type"] = "application/json"
        if not endpoint.endswith("/auth/token"):
            if not self.csrf_token:
                self.csrf_token = self.get_csrf_token()
            if self.csrf_token:
                self.session.headers["X-CSRF-TOKEN"] = str(self.csrf_token)
            self.session.headers["auth-token-signature"] = SicuraVariables.sicuraToken

        try:
            # Use the session object to maintain cookies between requests
            logger.debug(f"Current session headers: {dict(self.session.headers)}")
            response = self.session.request(
                method,
                url,
                headers=self.session.headers,
                json=data,
                params=params,
                verify=True,
                timeout=60,
                files=files,
            )

            logger.debug(f"Response cookies: {dict(response.cookies)}")

            if response.status_code == 403:
                logger.error("Authentication failed")
                raise requests.exceptions.HTTPError("Authentication failed", response=response)

            if response.status_code == 404:
                logger.error(f"Resource not found: {url}")
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    response.raise_for_status()
            else:
                response.raise_for_status()

            try:
                logger.debug(f"Response JSON: {json.dumps(response.json(), indent=2)}")
                return response.json()
            except requests.exceptions.JSONDecodeError:
                logger.debug(f"Response Text: {response.text}")
                return response.text

        except Exception as e:
            logger.error(f"Method: {method}, Endpoint: {endpoint}, Data: {data}, Params: {params}, Files: {files}")
            logger.error(f"Request failed: {e}", exc_info=True)
            raise

    @staticmethod
    def handle_response(response: Optional[Dict[str, Any]], model: Type[SicuraModelType]) -> Optional[SicuraModelType]:
        """
        Handle API response and convert to appropriate Sicura model.

        :param Optional[Dict[str, Any]] response: API response
        :param Type[SicuraModelType] model: Sicura model to validate response against
        :return: Validated Sicura model instance or None if validation fails
        :rtype: Optional[SicuraModelType]
        """
        if response is None:
            return None
        logger.debug(f"Handling Response: {response}")
        try:
            return model.model_validate(response)
        except ValueError as e:
            logging.error(f"Error validating response: {e}", exc_info=True)
            return None

    def get_csrf_token(self) -> Optional[AuthResponse]:
        """
        Get authentication token from Sicura API.

        :return: Authentication response
        :rtype: Optional[AuthResponse]
        :raises requests.exceptions.RequestException: If the request fails
        """
        try:
            response = self._make_request("GET", "/auth/token")
            self.csrf_token = response
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting authentication token: {e}", exc_info=True)
            raise

    class Device(SicuraModel):
        """Model for Sicura device information."""

        id: int = Field(None, alias="id")
        name: str = Field(..., alias="name")
        fqdn: Optional[str] = None
        ip_address: Optional[str] = None
        platforms: str = ""
        scannable_profiles: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
        most_recent_scan: Optional[str] = None

        class Config:
            populate_by_name = True
            extra = "allow"

    def get_devices(self, ip_address: Optional[str] = None, fqdn: Optional[str] = None) -> List[SicuraAPI.Device]:
        """
        Get devices from Sicura API.

        :param Optional[str] ip_address: IP address to filter devices by
        :param Optional[str] fqdn: FQDN to filter devices by
        :return: List of devices
        :rtype: List[SicuraAPI.Device]
        """
        try:
            response = self._make_request(
                "GET",
                "/backend/api/jaeger/v1/nodes",
                params={
                    "verbose": "true",
                    "attributes": "platforms,scannable_profiles,most_recent_scan",
                    self.FILTER_FQDN: fqdn,
                    self.FILTER_IP_ADDRESS: ip_address,
                    self.FILTER_TYPE: "endpoint",
                },
            )

            # Handle 404 or empty response
            if not response or (isinstance(response, dict) and "detail" in response):
                logger.debug(f"No devices found: {response}")
                return []

            # Convert response to list if it's a single device
            if isinstance(response, dict):
                response = [response]

            return [
                item
                for item in (self.handle_response(item, SicuraAPI.Device) for item in response if item is not None)
                if item is not None
            ]
        except Exception as e:
            logger.error(f"Failed to get devices: {e}", exc_info=True)
            return []

    def create_scan_task(
        self,
        device_id: int,
        platform: str,
        profile: SicuraProfile,
        task_name: Optional[str] = None,
        scheduled_time: Optional[datetime.datetime] = None,
    ) -> Optional[str]:
        """
        Create a scanning task for a specific device.

        :param int device_id: ID of the device to scan
        :param str platform: Platform name (e.g., 'Red Hat Enterprise Linux 9')
        :param SicuraProfile profile: Scan profile name (e.g., 'I - Mission Critical Classified')
        :param Optional[str] task_name: Name for the scan task (default: auto-generated)
        :param Optional[datetime.datetime] scheduled_time: When to run the scan (default: now)
        :return: Task ID if successful, None otherwise
        :rtype: Optional[str]
        """
        try:
            # Generate default task name if not provided
            if not task_name:
                task_name = f"Scan {platform} - {profile} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"

            # Default to current time if not specified
            if not scheduled_time:
                scheduled_time = datetime.datetime.now()

            # Format timestamp for API
            timestamp = scheduled_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            payload = {
                "name": task_name,
                "type": "Scanning",
                "scope": device_id,
                "cron": "",
                "timestamp": timestamp,
                "repeating": False,
                "scanAttributes": {"platform": platform, "profile": profile},
            }

            result = self._make_request("POST", "/backend/api/jaeger/v1/tasks/", data=payload)

            if result:
                logger.info(f"Successfully created scan task with ID: {result}")
                return result
            else:
                logger.error(f"Failed to create scan task. Response: {result}")
                return None

        except Exception as e:
            logger.error(f"Error creating scan task: {e}", exc_info=True)
            return None

    def get_task_status(self, task_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task by its ID.

        :param Union[int, str] task_id: ID of the task to check
        :return: Dictionary with job information including status, or None if not found
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            response = self._make_request(
                "GET", "/backend/api/jaeger/v1/jobs", params={"verbose": "true", self.FILTER_TASK_ID: task_id}
            )

            # Handle 404 or empty response
            if not response or (isinstance(response, list) and not response):
                logger.debug(f"No jobs found for task ID {task_id}")
                return None

            # Convert response to list if it's a single job
            if isinstance(response, dict):
                response = [response]

            # Process the jobs
            jobs = []
            for job_data in response:
                job = self.handle_response(job_data, ScanJob)
                if job:
                    # Add human-readable status
                    job_dict = job.model_dump()
                    job_dict["status"] = self.JOB_STATUS.get(job.status_id, "UNKNOWN")
                    jobs.append(job_dict)

            if not jobs:
                return None

            return {"task_id": task_id, "jobs": jobs, "latest_status": jobs[-1]["status"] if jobs else "UNKNOWN"}

        except Exception as e:
            logger.error(f"Error getting task status: {e}", exc_info=True)
            return None

    def get_scan_results(
        self,
        fqdn: str,
        platform: Optional[str] = None,
        profile: SicuraProfile = SicuraProfile.I_MISSION_CRITICAL_CLASSIFIED,
    ) -> Optional[ScanReport]:
        """
        Get scan results for a specific device.

        :param str fqdn: Fully qualified domain name of the device
        :param Optional[str] platform: Platform name to filter results (e.g., 'Red Hat Enterprise Linux 9')
        :param SicuraProfile profile: Profile name to filter results (e.g., 'I - Mission Critical Classified')
        :return: Scan report containing device info and scan results, or None if not found
        :rtype: Optional[ScanReport]
        """
        try:
            params = {"verbose": "true", "attributes": "scans", self.FILTER_FQDN: fqdn}

            if platform:
                params["platform"] = platform

            if profile:
                params["profile"] = profile

            response = self._make_request("GET", "/backend/api/jaeger/v1/nodes", params=params)

            # Handle 404 or empty response
            if not response or (isinstance(response, list) and not response):
                logger.debug(f"No scan results found for FQDN {fqdn}")
                return None

            # If we got a single device (dict), convert to a list
            if isinstance(response, dict):
                response = [response]

            # Process only the first device that matches
            if response and isinstance(response[0], dict):
                device = response[0]

                # Check if scans are present
                if not device.get("scans"):
                    logger.debug(f"No scan results found in device data for {fqdn}")
                    return None  # Return None if no scans available

                # Calculate summary stats
                pass_count = sum(1 for scan in device.get("scans", []) if scan.get("result") == "pass")
                fail_count = sum(1 for scan in device.get("scans", []) if scan.get("result") == "fail")
                total_count = len(device.get("scans", []))

                # Create the raw result data
                result_data = {
                    "device_id": device.get("id"),
                    "fqdn": device.get("fqdn"),
                    "ip_address": device.get("ip_address"),
                    "scans": device.get("scans", []),
                    "summary": {
                        "total": total_count,
                        "pass": pass_count,
                        "fail": fail_count,
                        "pass_percentage": (pass_count / total_count * 100) if total_count > 0 else 0,
                    },
                }

                # Convert to ScanReport model
                try:
                    return ScanReport.model_validate(result_data)
                except Exception as e:
                    logger.error(f"Error creating scan report model: {e}, result_data: {result_data}")

            return None

        except Exception as e:
            logger.error(f"Error getting scan results: {e}", exc_info=True)
            return None

    def wait_for_scan_results(
        self,
        task_id: Union[int, str],
        fqdn: str,
        platform: Optional[str] = None,
        profile: SicuraProfile = SicuraProfile.I_MISSION_CRITICAL_CLASSIFIED,
        max_wait_time: int = 600,
        poll_interval: int = 10,
    ) -> Optional[Union[ScanReport, Dict[str, Any]]]:
        """
        Wait for a scan task to complete and then return the scan results.

        :param Union[int, str] task_id: ID of the scan task to monitor
        :param str fqdn: Fully qualified domain name of the device
        :param Optional[str] platform: Platform name to filter results
        :param SicuraProfile profile: Profile name to filter results
        :param int max_wait_time: Maximum time to wait in seconds (default: 10 minutes)
        :param int poll_interval: Time between status checks in seconds (default: 10 seconds)
        :return: Scan results once the task is complete, or None if timeout or error
        :rtype: Optional[Union[ScanReport, Dict[str, Any]]]
        """
        start_time = time.time()
        elapsed_time = 0.0

        logger.info(f"Waiting for scan task {task_id} to complete...")

        # Poll until we get a non-QUEUED status or hit timeout
        while elapsed_time < max_wait_time:
            task_status = self.get_task_status(task_id)

            if not task_status:
                logger.warning(f"Could not retrieve status for task {task_id}")
                time.sleep(poll_interval)
                elapsed_time = time.time() - start_time
                continue

            latest_status = task_status.get("latest_status")
            logger.info(f"Current task status: {latest_status} (elapsed: {elapsed_time:.1f}s)")

            # If we have a status and it's not QUEUED, we can proceed
            if latest_status and latest_status != "QUEUED":
                # If we've reached a terminal state
                if latest_status in ["COMPLETE", "ERROR", "CANCELLED", "TIMEOUT"]:
                    if latest_status == "COMPLETE":
                        logger.info(f"Scan task {task_id} completed successfully, fetching results...")
                        # Wait a moment for results to be processed
                        time.sleep(2)
                        return self.get_scan_results(fqdn, platform, profile)
                    else:
                        logger.error(f"Scan task {task_id} ended with status {latest_status}")
                        return None

            # Wait before polling again
            time.sleep(poll_interval)
            elapsed_time = time.time() - start_time

        logger.error(f"Timed out waiting for scan task {task_id} to complete after {max_wait_time} seconds")
        return None

    def get_pending_devices(
        self, fqdn: Optional[str] = None, ip_address: Optional[str] = None, rejected: bool = False
    ) -> List[PendingDevice]:
        """
        Get pending devices waiting to be accepted.

        :param Optional[str] fqdn: FQDN to filter devices by
        :param Optional[str] ip_address: IP address to filter devices by
        :param bool rejected: Whether to include rejected devices (default: False)
        :return: List of pending devices
        :rtype: List[PendingDevice]
        """
        try:
            params = {
                "verbose": "true",
                "attributes": "id,fqdn,signature,platform,platform_title,last_update,ip_address,rejected",
                self.FILTER_REJECTED: str(rejected).lower(),
            }

            if fqdn:
                params[self.FILTER_FQDN] = fqdn

            if ip_address:
                params[self.FILTER_IP_ADDRESS] = ip_address

            response = self._make_request("GET", "/backend/api/jaeger/v1/node_templates/", params=params)

            # Handle 404 or empty response
            if not response or (isinstance(response, dict) and "detail" in response):
                logger.debug(f"No pending devices found: {response}")
                return []

            # Convert response to list if it's a single device
            if isinstance(response, dict):
                response = [response]

            return [
                item
                for item in (self.handle_response(item, PendingDevice) for item in response if item is not None)
                if item is not None
            ]
        except Exception as e:
            logger.error(f"Failed to get pending devices: {e}", exc_info=True)
            return []

    def accept_pending_device(self, device_id: int) -> bool:
        """
        Accept a pending device.

        :param int device_id: ID of the pending device to accept
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Use PUT method with the correct endpoint and payload
            result = self._make_request(
                "PUT",
                f"/backend/api/jaeger/v1/node_templates/{device_id}",
                params={"verbose": "true", "include_controls": "true", "action": "promote"},
            )

            if result:
                logger.info(f"Successfully accepted pending device with ID: {device_id}")
                return True
            else:
                logger.error(f"Failed to accept pending device. Response: {result}")
                return False

        except Exception as e:
            logger.error(f"Error accepting pending device: {e}", exc_info=True)
            return False

    def reject_pending_device(self, device_id: int) -> bool:
        """
        Reject a pending device.

        :param int device_id: ID of the pending device to reject
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Use PUT method with the correct endpoint and payload
            result = self._make_request(
                "PUT",
                f"/backend/api/jaeger/v1/node_templates/{device_id}",
                params={"verbose": "true", "include_controls": "true", "action": "reject"},
            )

            if result:
                logger.info(f"Successfully rejected pending device with ID: {device_id}")
                return True
            else:
                logger.error(f"Failed to reject pending device. Response: {result}")
                return False

        except Exception as e:
            logger.error(f"Error rejecting pending device: {e}", exc_info=True)
            return False

    def delete_device(self, device_id: int) -> bool:
        """
        Delete a device from Sicura.

        :param int device_id: ID of the device to delete
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            result = self._make_request("DELETE", f"/backend/api/jaeger/v1/nodes/{device_id}")

            # For DELETE operations, an empty result typically indicates success
            if result is None or result == "" or (isinstance(result, dict) and not result):
                logger.info(f"Successfully deleted device with ID: {device_id}")
                return True
            else:
                logger.error(f"Failed to delete device. Response: {result}")
                return False

        except Exception as e:
            logger.error(f"Error deleting device: {e}", exc_info=True)
            return False

    def create_enforcement_task(
        self,
        device_id: int,
        profile: Optional[SicuraProfile] = None,
        ce_names: Optional[List[str]] = None,
        task_name: Optional[str] = None,
        scheduled_time: Optional[datetime.datetime] = None,
        no_op: bool = False,
    ) -> Optional[str]:
        """
        Create an enforcement task for a specific device based on scan results or provided ce_names.

        :param int device_id: ID of the device to enforce
        :param Optional[SicuraProfile] profile: Profile to use for fetching scan results if ce_names not provided
        :param Optional[List[str]] ce_names: List of CE names to enforce. If None, will fetch from scan results
        :param Optional[str] task_name: Name for the enforcement task (default: auto-generated)
        :param Optional[datetime.datetime] scheduled_time: When to run the task (default: now)
        :param bool no_op: If True, will create a "dry run" enforcement that doesn't make changes
        :return: Task ID if successful, None otherwise
        :rtype: Optional[str]
        """
        try:
            # Get CE names if not provided
            if ce_names is None:
                ce_names = self._get_failed_ce_names(device_id, profile)
                if not ce_names:
                    return None

            # Create and submit task
            return self._submit_enforcement_task(device_id, profile, ce_names, task_name, scheduled_time, no_op)

        except Exception as e:
            logger.error(f"Error creating enforcement task: {e}", exc_info=True)
            return None

    def _get_failed_ce_names(self, device_id: int, profile: Optional[SicuraProfile]) -> Optional[List[str]]:
        """
        Get the CE names of failed checks for a device.

        :param int device_id: ID of the device to get CE names for
        :param Optional[SicuraProfile] profile: Profile to use for fetching scan results
        :return: List of CE names for failed checks, or None if not found
        :rtype: Optional[List[str]]
        """
        if profile is None:
            logger.error("Either ce_names or profile must be provided")
            return None

        # Get device info to get FQDN
        devices = self.get_devices(fqdn=None, ip_address=None)
        target_device = next((device for device in devices if device.id == device_id), None)

        if not target_device or not target_device.fqdn:
            logger.error(f"Could not find device with ID {device_id} or device has no FQDN")
            return None

        # Get scan results for the device
        scan_results = self.get_scan_results(fqdn=target_device.fqdn, platform=target_device.platforms, profile=profile)

        if not scan_results:
            logger.error(f"No scan results found for device {device_id} with profile {profile}")
            return None

        # Extract ce_names from failed checks
        ce_names = [
            scan.ce_name
            for scan in scan_results.scans
            if scan.result == "fail" and hasattr(scan, "ce_name") and scan.ce_name
        ]

        if not ce_names:
            logger.warning(f"No failed checks found for device {device_id} with profile {profile}")
            return None

        return ce_names

    def _submit_enforcement_task(
        self,
        device_id: int,
        profile: Optional[SicuraProfile],
        ce_names: List[str],
        task_name: Optional[str] = None,
        scheduled_time: Optional[datetime.datetime] = None,
        no_op: bool = False,
    ) -> Optional[str]:
        """
        Submit an enforcement task to the API.

        :param int device_id: ID of the device to enforce
        :param Optional[SicuraProfile] profile: Profile to use for the task name
        :param List[str] ce_names: List of CE names to enforce
        :param Optional[str] task_name: Name for the enforcement task
        :param Optional[datetime.datetime] scheduled_time: When to run the task
        :param bool no_op: If True, will create a "dry run" enforcement
        :return: Task ID if successful, None otherwise
        :rtype: Optional[str]
        """
        # Generate default task name if not provided
        if not task_name:
            task_name = f"Enforce {profile} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"

        # Default to current time if not specified
        if not scheduled_time:
            scheduled_time = datetime.datetime.now()

        # Format timestamp for API
        timestamp = scheduled_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        payload = {
            "name": task_name,
            "type": "Enforcement",
            "scope": device_id,
            "cron": "",
            "timestamp": timestamp,
            "repeating": False,
            "enforcementAttributes": {"platform": profile, "ce_names": ce_names, "no_op": no_op},
        }

        logger.info(f"Creating enforcement task for device {device_id} with {len(ce_names)} CE names")
        result = self._make_request("POST", "/backend/api/jaeger/v1/tasks/", data=payload)

        if result:
            logger.info(f"Successfully created enforcement task with ID: {result}")
            return result
        else:
            logger.error(f"Failed to create enforcement task. Response: {result}")
            return None
