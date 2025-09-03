from __future__ import annotations

import json
import logging
import random
import time
from functools import wraps
from typing import Optional, List, Union, Dict, Any, Type, TypeVar
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError

logger = logging.getLogger("regscale")
API_DEVICES = "/api/devices"
API_GROUPS = "/api/groups"


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


class DuroSuiteModel(BaseModel):
    """Base model for DuroSuite API responses."""

    class Config:
        populate_by_name = True


class AuditResponse(DuroSuiteModel):
    """Model for audit response."""

    device_id: int
    group_id: int
    template_id: int
    audit_id: int
    job_id: str
    status: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"


class Group(DuroSuiteModel):
    """Model for group information."""

    id: Optional[int] = Field(None, alias="group_id")
    name: Optional[str] = Field(None, alias="name")
    os_id: Optional[int] = None
    host_group_vars: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    children: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "allow"


class Var(DuroSuiteModel):
    """Model for variable information."""

    id: int = Field(default=None, alias="var_id")
    device_id: Optional[int] = None
    name: str = Field(..., alias="var_name")
    value: str = Field(..., alias="var_value")


class Device(DuroSuiteModel):
    """DuroSuite Device model."""

    id: Optional[int] = Field(None, alias="device_id")
    name: str = Field(..., alias="name")
    os_id: int = Field(..., alias="os_id")
    group_id: Optional[int] = Field(None, alias="group_id")
    device_vars: Optional[List[Var]] = Field(default_factory=list, alias="device_vars")
    groups: Optional[List[Group]] = Field(default_factory=list, alias="groups")


class STIG(DuroSuiteModel):
    """Model for STIG information."""

    id: int
    file_name: str
    version: str
    os_id: int
    releaseinfo: str
    playbook: str


class Template(DuroSuiteModel):
    """Template model."""

    id: Optional[int] = Field(None)
    name: str
    os_id: int
    playbook_id: Optional[int] = None
    group_id: Optional[int] = None
    template_vars: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "allow"


DuroSuiteModelType = TypeVar("DuroSuiteModelType", bound=DuroSuiteModel)


class DuroSuite:
    """Methods to interact with DuroSuite API"""

    # API Endpoints
    TEMPLATE_VAR_ENDPOINT = "/api/stigs/templates/var"
    TEMPLATES_ENDPOINT = "/api/stigs/templates"
    DEVICE_VARS_ENDPOINT = "/api/devices/vars"

    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize DuroSuite API client.

        :param str base_url: Base URL for the API
        :param Optional[str] username: Username for authentication
        :param Optional[str] password: Password for authentication
        """
        self.base_url = base_url
        self.api_key = None
        if username and password:
            self.username = username
            self.password = password
            self.login(username, password)

    def login(self, username: str, password: str) -> None:
        """
        Log in to the DuroSuite API.

        :param str username: Username for authentication
        :param str password: Password for authentication
        :raises ValueError: If login fails
        """
        self.username = username
        self.password = password
        data = {"username": username, "password": password}
        response_data = self._make_request("POST", "/api/login", data=data)
        if response_data:
            self.api_key = response_data.get("access_token")
            if not self.api_key:
                raise ValueError("Login failed: No access token received")

    def _handle_403_error(self) -> bool:
        """
        Handle 403 error by attempting to refresh token or log in again.

        :return: True if handled successfully, False otherwise
        :rtype: bool
        """
        if hasattr(self, "username") and hasattr(self, "password"):
            self.login(self.username, self.password)
            return True
        return False

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
        Make a request to the DuroSuite API.

        :param str method: HTTP method
        :param str endpoint: API endpoint
        :param Optional[Dict[str, Any]] data: Request data
        :param Optional[Dict[str, Any]] params: Query parameters
        :param Optional[Dict[str, Any]] files: Files to upload
        :return: Response data or None if request failed
        :rtype: Optional[Union[dict, str]]
        """
        from regscale.integrations.variables import ScannerVariables

        url = urljoin(self.base_url, endpoint)
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            logger.warning("No API key provided, proceeding without authentication")

        if data:
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=data,
                params=params,
                verify=ScannerVariables.sslVerify,
                timeout=60,
                files=files,
            )

            if response.status_code == 403:
                if self._handle_403_error():
                    # Retry the request with the new token
                    return self._make_request(method, endpoint, data, params, files)
                else:
                    logger.error("Authentication failed and no credentials provided for retry")
                    raise requests.exceptions.HTTPError("Authentication failed after retry", response=response)

            # Special handling for 404 with JSON response
            if response.status_code == 404:
                logger.error(f"Resource not found: {url}")
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:  # noqa: E722
                    response.raise_for_status()
            else:
                response.raise_for_status()

            # Try to parse as JSON, if it fails, return the text content
            try:
                r = response.json()
                return r
            except requests.exceptions.JSONDecodeError:
                return response.text

        except Exception as e:
            logger.error(f"Method: {method}, Endpoint: {endpoint}, Data: {data}, Params: {params}, Files: {files}")
            logger.error(f"Request failed: {e}", exc_info=True)
            raise

    @staticmethod
    def handle_response(
        response: Optional[Dict[str, Any]], model: Type[DuroSuiteModelType]
    ) -> Optional[DuroSuiteModelType]:
        """
        Handle API response and convert to appropriate DuroSuite model.

        :param Optional[Dict[str, Any]] response: API response
        :param Type[DuroSuiteModelType] model: DuroSuite model to validate response against
        :return: Validated DuroSuite model instance or None if validation fails
        :rtype: Optional[DuroSuiteModelType]
        """
        if response is None:
            return None
        logger.debug(f"Handling Response: {response}")
        try:
            return model.model_validate(response)
        except ValueError as e:
            logging.error(f"Error validating response: {e}", exc_info=True)
            return None

    def _handle_list_response(
        self, response: Optional[List[Dict[str, Any]]], model: Type[DuroSuiteModelType]
    ) -> List[DuroSuiteModelType]:
        """
        Handle API list response and convert to a list of appropriate DuroSuite models.

        :param Optional[List[Dict[str, Any]]] response: API response
        :param Type[DuroSuiteModelType] model: DuroSuite model to validate response against
        :return: List of validated DuroSuite model instances
        :rtype: List[DuroSuiteModelType]
        """
        if response is None:
            return []
        return [
            item
            for item in (self.handle_response(item, model) for item in response if item is not None)
            if item is not None
        ]

    def revoke_access_token(self) -> Optional[Dict[str, Any]]:
        """
        Revoke Access Token.

        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", "/api/access-revoke")

    def revoke_refresh_token(self) -> Optional[Dict[str, Any]]:
        """
        Revoke Refresh Token.

        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", "/api/refresh-revoke")

    def refresh_token(self) -> Optional[Dict[str, Any]]:
        """
        Refresh Token.

        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/refresh-token")

    def change_current_user_password(self, old_password: str, new_password: str) -> Optional[Dict[str, Any]]:
        """
        Change Current User Password.

        :param str old_password: Current password
        :param str new_password: New password
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"old_password": old_password, "new_password": new_password}
        return self._make_request("POST", "/api/users/change_password", data=json.dumps(data))

    def reset_user_password(self, admin_password: str, user_id: int, new_password: str) -> Optional[Dict[str, Any]]:
        """
        Reset User Password.

        :param str admin_password: Admin password
        :param int user_id: ID of the user whose password is being reset
        :param str new_password: New password
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"admin_password": admin_password, "user_id": user_id, "new_password": new_password}
        return self._make_request("POST", "/api/users/reset_password", data=json.dumps(data))

    # 2. Audit Records
    def get_all_audits(self, skip: int = 0, limit: int = 10, **params) -> Optional[Dict[str, Any]]:
        """
        Get All Audits.

        :param int skip: Number of records to skip
        :param int limit: Number of records to return
        :param params: Additional query parameters
        :return: List of audits
        :rtype: Optional[Dict[str, Any]]
        """
        params.update({"skip": skip, "limit": limit})
        return self._make_request("GET", "/api/audits", params=params)

    def get_audit_record(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Get audit record.

        :param int audit_id: ID of the audit
        :return: Audit record
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/audits/{audit_id}")

    def delete_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Audit.

        :param int audit_id: ID of the audit to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/audits/{audit_id}")

    def get_checklist_file_by_audit_id(self, audit_id: int) -> Optional[str]:
        """
        Get checklist file by audit ID.

        :param int audit_id: The ID of the audit
        :return: Checklist file content or None if not found
        :rtype: Optional[str]
        """
        return self._make_request("GET", f"/api/audits/checklist/{audit_id}")

    def combine_checklist_files(self, audit_ids: List[int]) -> Optional[Dict[str, Any]]:
        """
        Combine Checklist Files.

        :param List[int] audit_ids: List of audit IDs to combine
        :return: Combined checklist file
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/combine-ckl", params={"audit_ids": audit_ids})

    def get_vulnerabilities_for_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Vulnerabilities For Audit.

        :param int audit_id: ID of the audit
        :return: List of vulnerabilities
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/vulnerabilities", params={"audit_id": audit_id})

    def get_single_vulnerability(self, vuln_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get Single Vulnerability.

        :param Dict[str, Any] vuln_data: Vulnerability data
        :return: Vulnerability details
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/single-vuln", data=json.dumps(vuln_data))

    # 3. Remediate Records
    def get_all_remediations(self, skip: int = 0, limit: int = 10, **params) -> Optional[Dict[str, Any]]:
        """
        Get All Remediations.

        :param int skip: Number of records to skip
        :param int limit: Number of records to return
        :param params: Additional query parameters
        :return: List of remediations
        :rtype: Optional[Dict[str, Any]]
        """
        params.update({"skip": skip, "limit": limit})
        return self._make_request("GET", "/api/remediations", params=params)

    def get_remediation_record(self, remediation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Remediation Record.

        :param int remediation_id: ID of the remediation
        :return: Remediation record
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/remediations/{remediation_id}")

    def delete_remediation(self, remediation_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Remediation.

        :param int remediation_id: ID of the remediation to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/remediations/{remediation_id}")

    # 4. Devices
    def get_devices(self) -> List[Device]:
        """
        Get all devices.

        :return: List of all devices
        :rtype: List[Device]
        """
        try:
            response = self._make_request("GET", API_DEVICES)
            # Handle 404 "No devices available" response
            if not response or (isinstance(response, dict) and "detail" in response):
                logger.debug(f"No devices found: {response}")
                return []
            return self._handle_list_response(response, Device)
        except Exception as e:
            logger.error(f"Failed to get devices: {e}", exc_info=True)
            return []

    def update_device(self, device_data: Device) -> Optional[Dict[str, Any]]:
        """
        Update Device.

        :param Device device_data: Updated device data
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", API_DEVICES, params=device_data.model_dump())

    def add_new_device(self, device_data: Dict[str, Any]) -> Optional[Device]:
        """
        Add a new device.

        :param Dict[str, Any] device_data: Device data to add
        :return: Added device
        :rtype: Optional[Device]
        """
        try:
            # Format device data according to API spec
            request_data = {
                "device_name": device_data["name"],  # API expects device_name
                "os_id": int(device_data["os_id"]),
                "group_id": int(device_data["group_id"]),
            }

            logger.debug(f"Creating device with data: {request_data}")

            # Create device first
            response = self._make_request("POST", API_DEVICES, data=request_data)

            if not response:
                logger.error("Failed to create device - empty response")
                return None

            logger.debug(f"Device creation response: {response}")

            device_id = response.get("device_id")
            if not device_id:
                logger.error("Failed to get device ID from response")
                return None

            # Add device variables if provided
            if "device_vars" in device_data:
                for var in device_data["device_vars"]:
                    var_data = {"device_id": device_id, "var_name": var["var_name"], "var_value": var["var_value"]}

                    logger.debug(f"Adding device variable: {var_data}")
                    self._make_request("POST", "/api/devices/vars", data=var_data)

            # Get all devices and find our newly created one
            all_devices = self._make_request("GET", API_DEVICES)
            if not all_devices:
                logger.error("Failed to get devices list")
                return None

            # Find our device in the list
            device_response = next((d for d in all_devices if d.get("device_id") == device_id), None)

            if not device_response:
                logger.error(f"Could not find device {device_id} in devices list")
                # Return a basic device object with what we know
                device_response = {
                    "device_id": device_id,
                    "name": device_data["name"],
                    "os_id": device_data["os_id"],
                    "group_id": device_data["group_id"],
                    "device_vars": device_data.get("device_vars", []),
                    "groups": [{"id": device_data["group_id"]}],
                }

            return Device(**device_response)
        except Exception as e:
            logger.error(f"Failed to create device: {e}", exc_info=True)
            return None

    def get_csv_for_batch_upload(self, os_id: int) -> Optional[str]:
        """
        Get CSV For Batch Upload.

        :param int os_id: Operating system ID
        :return: CSV content
        :rtype: Optional[str]
        """
        return self._make_request("GET", "/api/devices/batch-upload", params={"os_id": os_id})

    def batch_upload_devices(self, os_id: int, csv_file: Any) -> Optional[Dict[str, Any]]:
        """
        Batch Upload Devices.

        :param int os_id: Operating system ID
        :param Any csv_file: CSV file containing device information
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        files = {"devices_file": csv_file}
        return self._make_request("POST", f"/api/devices/batch-upload?os_id={os_id}", files=files)

    def get_devices_by_group_id(self, group_id: int) -> Optional[List[Device]]:
        """
        Get Devices By Group ID.

        :param int group_id: Group ID
        :return: List of devices in the group
        :rtype: Optional[List[Device]]
        """
        return self._make_request("GET", f"/api/devices/{group_id}")

    def delete_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Device.

        :param int device_id: Device ID to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/devices/{device_id}")

    def update_device_variable(self, var_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update Device Variable.

        :param Dict[str, Any] var_data: Variable data to update
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", self.DEVICE_VARS_ENDPOINT, params=var_data)

    def add_new_device_variable(self, var: Var) -> Optional[Var]:
        """
        Add New Device Variable.

        :param Var var: New variable data
        :return: Added variable
        :rtype: Optional[Var]
        """
        data = var.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request("POST", self.DEVICE_VARS_ENDPOINT, data=json.dumps(data))
        return self.handle_response(response, Var)

    def delete_device_variable(self, var_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Device Variable.

        :param int var_id: Variable ID to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"{self.DEVICE_VARS_ENDPOINT}/{var_id}")

    def test_connection(self, device_id: int, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Test Connection.

        :param int device_id: Device ID
        :param int group_id: Group ID
        :return: Connection test results
        :rtype: Optional[Dict[str, Any]]
        """
        params = {"device_id": device_id, "group_id": group_id}
        return self._make_request("GET", "/api/connection-test", params=params)

    # 5. Groups
    def get_groups(self) -> List[Group]:
        """
        Get all groups.

        :return: List of all groups
        :rtype: List[Group]
        """
        try:
            response = self._make_request("GET", API_GROUPS)
            if not response:
                return []

            # Log response for debugging
            logger.debug(f"Get groups response: {response}")

            # Handle both single group and list responses
            if isinstance(response, dict):
                response = [response]

            groups = []
            for group_data in response:
                try:
                    # Ensure group_id is properly set
                    if "group_id" not in group_data and "id" in group_data:
                        group_data["group_id"] = group_data["id"]
                    groups.append(Group(**group_data))
                except Exception as e:
                    logger.error(f"Failed to parse group data: {e}", exc_info=True)

            return groups
        except Exception as e:
            logger.error(f"Failed to get groups: {e}", exc_info=True)
            return []

    def update_group(self, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update Group.

        :param Dict[str, Any] group_data: Updated group data
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", API_GROUPS, params=group_data)

    def add_new_group(self, group_data: Dict[str, Any]) -> Optional[Group]:
        """
        Add a new group.

        :param Dict[str, Any] group_data: Group data to add
        :return: Added group
        :rtype: Optional[Group]
        """
        try:
            # Format group data according to API spec
            request_data = {
                "group_name": group_data["group_name"],  # API expects group_name
                "os_id": int(group_data["os_id"]),
            }

            logger.debug(f"Creating group with data: {request_data}")

            response = self._make_request("POST", API_GROUPS, data=request_data)

            if not response:
                logger.error("Failed to create group - empty response")
                return None

            logger.debug(f"Group creation response: {response}")

            # Map response fields to Group model fields
            group_data = {
                "group_id": response.get("group_id"),
                "name": response.get("group_name"),
                "os_id": response.get("group_os_id"),  # Changed from os_id to group_os_id
                "host_group_vars": [],
                "children": [],
            }

            # Create the group first
            group = Group(**group_data)
            if not group.id:
                logger.error("Failed to parse group response - missing id")
                return None

            # Step 2: Create template for the group
            template_data = {"name": "Baseline", "os_id": int(group_data["os_id"]), "group_id": group.id}

            template_response = self._make_request("POST", "/api/stigs/templates", data=template_data)

            if not template_response:
                logger.error("Failed to create template")
                return None

            template_id = template_response.get("id")

            # Step 3: Add template variables
            if "variables" in group_data and template_id:
                for var_name, var_value in group_data["variables"].items():
                    var_data = {"template_id": template_id, "var_name": var_name, "var_value": str(var_value)}

                    logger.debug(f"Adding template variable: {var_data}")
                    self._make_request("POST", "/api/stigs/templates/var", data=var_data)

            return group
        except Exception as e:
            logger.error(f"Failed to create group: {e}", exc_info=True)
            return None

    def get_groups_by_device_id(self, device_id: int) -> Optional[List[Group]]:
        """
        Get Groups By Device ID.

        :param int device_id: Device ID
        :return: List of groups associated with the device
        :rtype: Optional[List[Group]]
        """
        return self._make_request("GET", f"/api/groups/{device_id}")

    def delete_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Group.

        :param int group_id: Group ID to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/groups/{group_id}")

    def add_device_to_group(self, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add Device To Group.

        :param Dict[str, Any] group_data: Data for adding device to group
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/groups/device", data=json.dumps(group_data))

    def remove_device_from_group(self, group_id: int, device_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove Device From Group.

        :param int group_id: Group ID
        :param int device_id: Device ID to remove
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/groups/device/{group_id}/{device_id}")

    def add_child_to_group(self, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add Child To Group.

        :param Dict[str, Any] group_data: Data for adding child to group
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/groups/child", data=json.dumps(group_data))

    def remove_child_from_group(self, parent_id: int, child_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove Child From Group.

        :param int parent_id: Parent group ID
        :param int child_id: Child group ID to remove
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/groups/child/{parent_id}/{child_id}")

    def get_roles_by_group_id(self, group_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get Roles By Group ID.

        :param int group_id: Group ID
        :return: List of roles associated with the group
        :rtype: Optional[List[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/groups/roles/{group_id}")

    def add_user_to_group(self, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add User To Group.

        :param Dict[str, Any] group_data: Data for adding user to group
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/groups/user", data=json.dumps(group_data))

    def remove_user_from_group(self, user_id: int, perm_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove User From Group.

        :param int user_id: User ID to remove
        :param int perm_id: Permission ID
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/groups/user/{user_id}/{perm_id}")

    def get_current_users_group_perms(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Current Users Group Permissions.

        :param int group_id: The ID of the group
        :return: Group permissions for the current user
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/groups/perms/{group_id}")

    # 6. Settings
    def get_ansible_cfg_settings(self) -> Optional[Dict[str, Any]]:
        """
        Get Ansible Configuration Settings.

        :return: Ansible configuration settings
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/ansible-cfg")

    def update_ansible_cfg(self, ansible_cfg_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update Ansible Configuration.

        :param Dict[str, Any] ansible_cfg_data: Updated Ansible configuration data
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", "/api/ansible-cfg", data=json.dumps(ansible_cfg_data))

    def get_site_theme(self) -> Optional[Dict[str, Any]]:
        """
        Get Site Theme.

        :return: Site theme information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/theme")

    def update_site_theme(self, theme_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update Site Theme.

        :param Dict[str, Any] theme_data: Updated theme data
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", "/api/settings/theme", data=json.dumps(theme_data))

    def get_database_backup(self) -> Optional[Dict[str, Any]]:
        """
        Get Database Backup.

        :return: Database backup information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/backup")

    def get_dns_conf(self) -> Optional[Dict[str, Any]]:
        """
        Get DNS Configuration.

        :return: DNS configuration information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/dns")

    def set_dns_conf(self, dns_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Set DNS Configuration.

        :param Dict[str, Any] dns_data: DNS configuration data
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/settings/dns", data=json.dumps(dns_data))

    def get_license_info(self) -> Optional[Dict[str, Any]]:
        """
        Get License Info.

        :return: License information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/license")

    def license_key_ingest(self, license_file: Any) -> Optional[Dict[str, Any]]:
        """
        License Key Ingest.

        :param Any license_file: License file to ingest
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        files = {"license_file": license_file}
        return self._make_request("POST", "/api/settings/license", files=files)

    def get_version_info(self) -> Optional[Dict[str, Any]]:
        """
        Get Version Info.

        :return: Version information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/version")

    def get_license_status(self) -> Optional[Dict[str, Any]]:
        """
        Get License Status.

        :return: License status information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/settings/license/status")

    # 7. Supported Systems
    def get_supported_operating_systems(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get Supported Operating Systems.

        :return: List of supported operating systems
        :rtype: Optional[List[Dict[str, Any]]]
        """
        return self._make_request("GET", "/api/operating-systems")

    def get_operating_system_default_variables(self, os_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Operating System Default Variables.

        :param int os_id: Operating system ID
        :return: Default variables for the specified operating system
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/operating-systems/defaults/{os_id}")

    def get_os_connection_vars(self, os_id: int) -> Optional[Dict[str, Any]]:
        """
        Get OS Connection Variables.

        :param int os_id: Operating system ID
        :return: Connection variables for the specified operating system
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", f"/api/operating-systems/connection-vars/{os_id}")

    def get_available_stigs(self) -> List[STIG]:
        """
        Get Available STIGs.

        :return: List of available STIGs
        :rtype: List[STIG]
        """
        response = self._make_request("GET", "/api/stigs")
        return self._handle_list_response(response, STIG)

    def get_stigs_by_os_id(self, os_id: int) -> List[STIG]:
        """
        Get STIGs By OS ID.

        :param int os_id: Operating system ID
        :return: List of STIGs for the specified operating system
        :rtype: List[STIG]
        """
        response = self._make_request("GET", f"/api/stigs/{os_id}")
        return self._handle_list_response(response, STIG)

    def get_stig_defaults_by_stig_id(self, stig_id: int) -> Optional[STIG]:
        """
        Get STIG Defaults By STIG ID.

        :param int stig_id: STIG ID
        :return: Default STIG information
        :rtype: Optional[STIG]
        """
        response = self._make_request("GET", f"/api/stigs/defaults/{stig_id}")
        return self.handle_response(response, STIG)

    def create_template(self, name: str, os_id: int, playbook_id: int, group_id: int) -> Template:
        """
        Create a new template.

        :param str name: The name of the template.
        :param int os_id: The ID of the operating system.
        :param int playbook_id: The ID of the playbook.
        :param int group_id: The ID of the group.

        :return: The created template.
        :rtype: Template
        """
        try:
            # Log input parameters
            logger.debug(
                f"Creating template with params: name={name}, os_id={os_id}, playbook_id={playbook_id}, group_id={group_id}"
            )

            # Create request data according to swagger spec for TemplateRequest
            template_request = {
                "name": name,
                "os_id": int(os_id),  # Ensure integer type
                "group_id": int(group_id),  # Ensure integer type
                "playbook_id": int(playbook_id),  # Ensure integer type
                "template_vars": [],  # Added empty template_vars array
            }

            # Log request data
            logger.debug(f"Template request data: {template_request}")

            # No need to set headers here as _make_request handles authorization
            response = self._make_request(
                "POST", self.TEMPLATES_ENDPOINT, data=template_request  # _make_request will handle JSON serialization
            )

            if not response:
                error_msg = "Failed to create template - empty response"
                logger.error(error_msg)
                raise ValueError(error_msg)

            response_data = response

            # Log the response for debugging
            logger.debug(f"Template creation response: {response_data}")

            # Ensure the response has all required fields
            response_data.update({"os_id": os_id, "playbook_id": playbook_id, "group_id": group_id})

            # Log the final template data
            logger.debug(f"Final template data: {response_data}")

            return Template(**response_data)
        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}", exc_info=True)  # Added full stack trace
            raise ValueError(f"Failed to create template: {str(e)}")

    def update_template(self, template: Template) -> Optional[Template]:
        """
        Update Template.

        :param Template template: Template to update
        :return: Updated template
        :rtype: Optional[Template]
        """
        data = template.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request("PUT", self.TEMPLATES_ENDPOINT, data=json.dumps(data))
        return self.handle_response(response, Template)

    def add_new_template(self, template: Template) -> Optional[Template]:
        """
        Add New Template.

        :param Template template: New template to add
        :return: Added template
        :rtype: Optional[Template]
        """
        data = template.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request("POST", self.TEMPLATES_ENDPOINT, data=json.dumps(data))
        return self.handle_response(response, Template)

    def update_template_variable(self, var_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update Template Variable.

        :param Dict[str, Any] var_data: Variable data to update
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", self.TEMPLATE_VAR_ENDPOINT, data=json.dumps(var_data))

    def add_template_var(self, var_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add Template Variable.

        :param Dict[str, Any] var_data: Variable data to add
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", self.TEMPLATE_VAR_ENDPOINT, data=json.dumps(var_data))

    def get_available_stig_templates(self, stig_id: int) -> List[Template]:
        """
        Get Available STIG Templates.

        :param int stig_id: STIG ID
        :return: List of available templates for the specified STIG
        :rtype: List[Template]
        """
        response = self._make_request("GET", f"/api/stigs/templates/stig/{stig_id}")
        return self._handle_list_response(response, Template)

    def get_template(self, template_id: int) -> Optional[Template]:
        """
        Get Template.

        :param int template_id: Template ID
        :return: Template information
        :rtype: Optional[Template]
        """
        response = self._make_request("GET", f"{self.TEMPLATES_ENDPOINT}/{template_id}")
        return self.handle_response(response, Template)

    def delete_template(self, template_id: int) -> bool:
        """
        Delete Template.

        :param int template_id: Template ID to delete
        :return: True if deletion was successful, False otherwise
        :rtype: bool
        """
        response = self._make_request("DELETE", f"{self.TEMPLATES_ENDPOINT}/{template_id}")
        return response is not None

    def get_template_ids_by_group(self, group_id: int) -> List[Template]:
        """
        Get Template IDs By Group.

        :param int group_id: The ID of the group
        :return: List of templates associated with the group
        :rtype: List[Template]
        """
        try:
            response = self._make_request("GET", f"/api/stigs/templates/group/{group_id}")
            if not response:
                return []

            # Add group_id to each template response
            if isinstance(response, list):
                for template_data in response:
                    template_data.update(
                        {
                            "group_id": group_id,
                            "playbook_id": template_data.get("playbook_id", None),  # Handle missing playbook_id
                        }
                    )

            templates = []
            for template_data in response:
                try:
                    templates.append(Template(**template_data))
                except Exception as e:
                    logger.error(f"Failed to parse template data: {e}", exc_info=True)

            return templates
        except Exception as e:
            logger.error(f"Failed to get templates for group {group_id}: {e}", exc_info=True)
            return []

    def delete_template_variable(self, var_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Template Variable.

        :param int var_id: The ID of the variable to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"{self.TEMPLATE_VAR_ENDPOINT}/{var_id}")

    # 8. Perform Audit/Remediate
    def audit_device(self, device_id: int, group_id: int, playbook_id: int, template_id: int) -> AuditResponse:
        """
        Audit Device.

        :param int device_id: The ID of the device to audit
        :param int group_id: The ID of the group
        :param int playbook_id: The ID of the playbook
        :param int template_id: The ID of the template
        :return: Audit response
        :rtype: AuditResponse
        :raises ValueError: If the API response cannot be parsed into an AuditResponse
        """
        params = {"device_id": device_id, "group_id": group_id, "playbook_id": playbook_id, "template_id": template_id}
        response = self._make_request("GET", "/api/audit/device", params=params)
        audit_response = self.handle_response(response, AuditResponse)
        if audit_response is None:
            raise ValueError("Failed to parse API response into AuditResponse")
        return audit_response

    def audit_group(self, group_id: int, playbook_id: int, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Audit Group.

        :param int group_id: The ID of the group to audit
        :param int playbook_id: The ID of the playbook
        :param int template_id: The ID of the template
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        params = {"group_id": group_id, "playbook_id": playbook_id, "template_id": template_id}
        return self._make_request("GET", "/api/audit/group", params=params)

    def cancel_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Cancel Audit.

        :param int audit_id: The ID of the audit to cancel
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/audit/cancel", params={"audit_id": audit_id})

    def remediate_device(
        self, device_id: int, group_id: int, playbook_id: int, template_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Remediate Device.

        :param int device_id: The ID of the device to remediate
        :param int group_id: The ID of the group
        :param int playbook_id: The ID of the playbook
        :param int template_id: The ID of the template
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        params = {"device_id": device_id, "group_id": group_id, "playbook_id": playbook_id, "template_id": template_id}
        return self._make_request("GET", "/api/remediate/device", params=params)

    def remediate_group(self, group_id: int, playbook_id: int, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Remediate Group.

        :param int group_id: The ID of the group to remediate
        :param int playbook_id: The ID of the playbook
        :param int template_id: The ID of the template
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        params = {"group_id": group_id, "playbook_id": playbook_id, "template_id": template_id}
        return self._make_request("GET", "/api/remediate/group", params=params)

    def cancel_remediation(self, rem_id: int) -> Optional[Dict[str, Any]]:
        """
        Cancel Remediation.

        :param int rem_id: The ID of the remediation to cancel
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/remediate/cancel", params={"rem_id": rem_id})

    def stream_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Stream Audit.

        :param int audit_id: The ID of the audit to stream
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/stream-audit", params={"audit_id": audit_id})

    def get_scheduled_tasks(
        self, group_id: Optional[int] = None, device_id: Optional[int] = None, repeat_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get Scheduled Tasks.

        :param Optional[int] group_id: The ID of the group (default: None)
        :param Optional[int] device_id: The ID of the device (default: None)
        :param Optional[str] repeat_type: The type of repeat for the task (default: None)
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        params = {}
        if group_id is not None:
            params["group_id"] = str(group_id)
        if device_id is not None:
            params["device_id"] = str(device_id)
        if repeat_type:
            params["repeat_type"] = repeat_type
        return self._make_request("GET", "/api/schedule", params=params)

    def delete_scheduled_task(self, scheduled_task_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Scheduled Task.

        :param int scheduled_task_id: The ID of the scheduled task to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/schedule/{scheduled_task_id}")

    def schedule_single(self, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Schedule Single Task.

        :param Dict[str, Any] schedule_data: The data for scheduling the task
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/schedule/single", data=json.dumps(schedule_data))

    def schedule_repeat(self, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Schedule Repeat Task.

        :param Dict[str, Any] schedule_data: The data for scheduling the repeating task
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("POST", "/api/schedule/repeat", data=json.dumps(schedule_data))

    # 9. User Actions
    def read_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Read Current User.

        :return: Current user information
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/users/me")

    def read_all_users(self) -> Optional[List[Dict[str, Any]]]:
        """
        Read All Users.

        :return: List of all users
        :rtype: Optional[List[Dict[str, Any]]]
        """
        return self._make_request("GET", "/api/users/all")

    def view_all_roles(self) -> Optional[List[Dict[str, Any]]]:
        """
        View All Roles.

        :return: List of all roles
        :rtype: Optional[List[Dict[str, Any]]]
        """
        return self._make_request("GET", "/api/users/roles/all")

    def create_new_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Create New User.

        :param str email: The email of the new user
        :param str password: The password for the new user
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"email": email, "password": password}
        return self._make_request("POST", "/api/users", data=json.dumps(data))

    def delete_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete User.

        :param int user_id: The ID of the user to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", f"/api/users/{user_id}")

    def enable_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Enable User.

        :param int user_id: The ID of the user to enable
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", "/api/users/enable", params={"user_id": user_id})

    def disable_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Disable User.

        :param int user_id: The ID of the user to disable
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", "/api/users/disable", params={"user_id": user_id})

    def add_role_to_user(self, user_id: int, role_id: int) -> Optional[Dict[str, Any]]:
        """
        Add Role To User.

        :param int user_id: The ID of the user
        :param int role_id: The ID of the role to add
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"user_id": user_id, "role_id": role_id}
        return self._make_request("PUT", "/api/users/roles/add", data=json.dumps(data))

    def remove_role_from_user(self, user_id: int, role_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove Role From User.

        :param int user_id: The ID of the user
        :param int role_id: The ID of the role to remove
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"user_id": user_id, "role_id": role_id}
        return self._make_request("PUT", "/api/users/roles/remove", data=json.dumps(data))

    def edit_user_settings(self, user_id: int, dark_mode: bool) -> Optional[Dict[str, Any]]:
        """
        Edit User Settings.

        :param int user_id: The ID of the user
        :param bool dark_mode: Whether to enable dark mode
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        data = {"user_id": user_id, "dark_mode": dark_mode}
        return self._make_request("PUT", "/api/users/settings", data=json.dumps(data))

    # 10. Logs
    def get_all_logs(self, skip: int = 0, limit: int = 10, **params) -> Optional[Dict[str, Any]]:
        """
        Get All Logs.

        :param int skip: Number of logs to skip (default: 0)
        :param int limit: Maximum number of logs to return (default: 10)
        :param params: Additional parameters for filtering logs
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/logs", params={"skip": skip, "limit": limit, **params})

    # 11. Notifications
    def get_notification(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Get Notification.

        :param int id: The ID of the notification
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("GET", "/api/notification", params={"id": id})

    def delete_notification(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Delete Notification.

        :param int id: The ID of the notification to delete
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("DELETE", "/api/notification", params={"id": id})

    def acknowledge_notification(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Acknowledge Notification.

        :param int id: The ID of the notification to acknowledge
        :return: API response
        :rtype: Optional[Dict[str, Any]]
        """
        return self._make_request("PUT", "/api/notification/acknowledge", params={"id": id})

    def get_audit_status(self, audit_id: int) -> Optional[AuditResponse]:
        """
        Get audit status.

        :param int audit_id: The ID of the audit
        :return: Audit status response
        :rtype: Optional[AuditResponse]
        """
        try:
            # According to swagger spec, the endpoint is /api/audits/{audit_id}
            response = self._make_request("GET", f"/api/audits/{audit_id}")

            if not response:
                logger.error(f"Failed to get audit status for audit {audit_id} - empty response")
                return None

            # Log the full response for debugging
            logger.debug(f"Audit status response: {response}")

            # Add required fields if missing
            response.update(
                {
                    "audit_id": audit_id,
                    "status": response.get("status", "unknown"),
                    "error_message": response.get("error_message", response.get("detail", "Unknown error")),
                    "device_id": response.get("device_id"),
                    "group_id": response.get("group_id"),
                    "template_id": response.get("template_id"),
                    "job_id": response.get("job_id"),
                }
            )

            # Create AuditResponse object
            audit_response = AuditResponse(**response)

            # Log status for debugging
            logger.debug(f"Audit {audit_id} status: {audit_response.status}")

            return audit_response
        except Exception as e:
            logger.error(f"Failed to get audit status for audit {audit_id}: {e}", exc_info=True)
            return None

    def update_device_vars(self, device_id: int, vars_data: List[Dict[str, str]]) -> bool:
        """
        Update device variables.

        :param int device_id: Device ID
        :param List[Dict[str, str]] vars_data: List of variable data to update
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            for var in vars_data:
                var_data = {"device_id": device_id, "var_name": var["var_name"], "var_value": var["var_value"]}

                logger.debug(f"Updating device variable: {var_data}")
                response = self._make_request("POST", self.DEVICE_VARS_ENDPOINT, data=var_data)

                if not response:
                    logger.error(f"Failed to update variable {var['var_name']}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Failed to update device variables: {e}", exc_info=True)
            return False
