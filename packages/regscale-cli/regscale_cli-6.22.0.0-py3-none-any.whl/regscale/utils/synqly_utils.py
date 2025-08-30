"""Utility functions for interacting with the Synqly API"""

import signal

import httpx

# Synqly Python SDK imports
from synqly import management as mgmt
from synqly.engine.client import SynqlyEngine
from synqly.management.client import SynqlyManagement
from regscale.core.app.utils.app_utils import create_logger

logger = create_logger()


# This class is an example of a multi-tenant application, meant
# to represent your application or product. It contains a pool of tenants, each
# of which might represent a user or organization within your application.
#
# This example omits application specific logic, focusing instead on the
# steps required to configure a Synqly Integration for each tenant.
class App:
    """
    This class is an example of a multi-tenant application, meant
    to represent your application or product. It contains a pool of tenants, each
    of which might represent a user or organization within your application.

    This example omits application specific logic, focusing instead on the
    steps required to configure a Synqly Integration for each tenant.

    Parameters:
        connector_type - The target Connector. Example: "ticketing"

    Attributes:
        connector_type - The target Connector. Example: "ticketing"
        tenants - A dictionary of Tenant objects, keyed by tenant name.
    """

    def __init__(self, connector_type):
        self.tenants = {}
        self.connector_type = connector_type
        # Initialize signal handlers to intercept Ctrl-C and perform cleanup
        signal.signal(signal.SIGINT, lambda signal, frame: self._cleanup_handler())
        signal.signal(signal.SIGTERM, lambda signal, frame: self._cleanup_handler())
        self.terminated = False

    def _cleanup_handler(self):
        """
        Deletes Synqly resources created by the example program.
        """
        if len(self.tenants) != 0:
            logger.info("\nCleaning up Synqly Resources:")
            for tenant in self.tenants.values():
                # Delete the Synqly Account
                tenant.synqly_management_client.accounts.delete(tenant.synqly_account_id)
                logger.debug("Cleaned up Account " + tenant.synqly_account_id)
            self.tenants = {}
            self.terminated = True
            logger.info("Cleanup complete.")

    def new_tenant(self, synqly_org_token: str, new_tenant_name: str):
        """
        Adds a new "tenant" to the App. A tenant represents a user or
        organization within your application.

        :param str synqly_org_token: The Synqly Organization token
        :param str new_tenant_name: The name of the new tenant
        :raises ValueError: If the tenant already exists
        """
        # Make sure the tenant doesn't already exist
        for tenant in self.tenants.values():
            if tenant.synqly_account_id == new_tenant_name:
                raise ValueError("Duplicate tenant id: " + id)

        """
        Create a Synqly Management API client. The client stores a token,
        allowing us to make calls to the Synqly Management API. The Management
        API is used to create Synqly Accounts and Integrations.
        """
        # (Optional) configure a custom httpx_client so that all errors are retried
        transport = httpx.HTTPTransport(retries=3)
        management_client = SynqlyManagement(
            token=synqly_org_token,
            httpx_client=httpx.Client(transport=transport),
        )

        """
        Each tenant needs an associated Account in Synqly, so we create that now.
        """
        account_request = mgmt.CreateAccountRequest(fullname=new_tenant_name)
        account_response = management_client.accounts.create(request=account_request)
        account_id = account_response.result.account.id

        self.tenants[new_tenant_name] = Tenant(
            tenant_name=new_tenant_name,
            synqly_account_id=account_id,
            synqly_management_client=management_client,
            # The Synqly Engine client will be initialized in configure_integration,
            # so we leave it as None for now.
            synqly_engine_client=None,
        )

    def configure_integration(self, tenant_name: str, provider_config: mgmt.ProviderConfig):
        """
        Configures a Synqly Integration for a simulated tenant

        :param str tenant_name: The name of the tenant
        :param mgmt.ProviderConfig provider_config: The provider configuration
        :raises TenantNotFoundException: If the tenant name is not found
        """

        # Locate the tenant in the App's tenant pool
        if tenant_name not in self.tenants.keys():
            raise TenantNotFoundException(tenant_name + " not found")

        tenant = self.tenants[tenant_name]

        # Use the Management API to create a Synqly Integration
        integration_req = mgmt.CreateIntegrationRequest(
            fullname="Python SDK Integration",
            provider_config=provider_config,
        )
        integration_resp = tenant.synqly_management_client.integrations.create(
            account_id=tenant.synqly_account_id, request=integration_req
        )
        logger.debug(
            "Created {} Integration '{}' for {}".format(
                integration_resp.result.integration.category,
                integration_resp.result.integration.id,
                tenant_name,
            )
        )

        # Add Synqly Engine client to the Tenant for use in the background job
        self.tenants[tenant_name].synqly_engine_client = SynqlyEngine(
            token=integration_resp.result.token.access.secret,
        )


class Tenant:
    """
    Represents a tenant within the application. A tenant could be a user,
    organization, or any other entity for which it would make sense to create
    an Integration.
    """

    def __init__(
        self,
        tenant_name,
        synqly_account_id,
        synqly_management_client,
        synqly_engine_client,
    ):
        self.tenant_name = tenant_name
        self.synqly_account_id = synqly_account_id
        self.synqly_management_client = synqly_management_client
        self.synqly_engine_client = synqly_engine_client


class TenantNotFoundException(Exception):
    """
    Exception raised when a tenant is not found
    """

    pass
