"""Tenant model for Synqly Integration"""

from typing import Optional

from synqly.engine.client import SynqlyEngine
from synqly.management.client import SynqlyManagement


class Tenant:
    """
    Represents a tenant within the application. A tenant could be a user,
    organization, or any other entity for which it would make sense to create
    an Integration.

    :param str tenant_name: The name of the tenant
    :param str account_id: The Account ID for the tenant
    :param Any management_client: The Management API client
    :param Any engine_client: The Engine API client
    """

    def __init__(
        self,
        tenant_name: str,
        account_id: str,
        management_client: Optional[SynqlyManagement],
        engine_client: Optional[SynqlyEngine],
    ):
        self.tenant_name = tenant_name
        self.account_id = account_id
        self.management_client = management_client
        self.engine_client = engine_client


class TenantNotFoundException(Exception):
    """
    Exception raised when a tenant is not found
    """

    pass
