"""
Microsoft Defender for Cloud Scanner Integration
"""

import logging
from typing import Iterator

from regscale.integrations.commercial.microsoft_defender.defender_api import DefenderApi
from regscale.integrations.commercial.microsoft_defender.defender_constants import RESOURCES_QUERY, AFD_ENDPOINTS
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models import IssueSeverity
from regscale.utils.string import generate_html_table_from_dict

logger = logging.getLogger("regscale")


class DefenderScanner(ScannerIntegration):
    title = "Microsoft Defender for Cloud"
    # Required fields from ScannerIntegration
    asset_identifier_field = "otherTrackingNumber"
    finding_severity_map = {
        "Critical": IssueSeverity.Critical,
        "High": IssueSeverity.High,
        "Medium": IssueSeverity.Moderate,
        "Low": IssueSeverity.Low,
    }

    def __init__(self, *args, **kwargs):
        self.system = kwargs.pop("system", "cloud")
        super().__init__(*args, **kwargs)
        self.api = DefenderApi(system=self.system)  # type: ignore

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from Synqly

        :yields: Iterator[IntegrationAsset]
        """
        cloud_resources = self.api.execute_resource_graph_query(
            query=RESOURCES_QUERY.format(SUBSCRIPTION_ID=self.api.config["azureCloudSubscriptionId"])
        )
        self.num_assets_to_process = len(cloud_resources)
        for asset in cloud_resources:
            yield self.parse_asset(asset)

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the Synqly

        :yields: Iterator[IntegrationFinding]
        """
        integration_findings = kwargs.get("integration_findings")
        for finding in integration_findings:
            yield finding

    def parse_asset(self, defender_asset: dict) -> IntegrationAsset:
        """
        Function to map data to an Asset object

        :param defender_asset: Data from Microsoft Defender for Cloud
        :return: IntegrationAsset object that is parsed from the defender_asset
        :rtype: IntegrationAsset
        """
        asset_id = defender_asset.get("resourceId")
        properties = defender_asset.get("properties", {})
        resource_type = defender_asset.get("resourceType", "").lower()
        try:
            ip_mapping = {
                "microsoft.network/networksecuritygroups": properties.get("securityRules", [{}])[0]
                .get("properties", {})
                .get("destinationAddressPrefix"),
                "microsoft.network/virtualnetworks": properties.get("addressSpace", {}).get("addressPrefixes"),
                "microsoft.app/managedenvironments": properties.get("staticIp"),
                "microsoft.network/networkinterfaces": properties.get("ipConfigurations", [{}])[0]
                .get("properties", {})
                .get("privateIPAddress"),
            }
        except IndexError:
            ip_mapping = {}
        try:
            fqdn_mapping = {
                "microsoft.keyvault/vaults": properties.get("vaultUri"),
                "microsoft.storage/storageaccounts": properties.get("primaryEndpoints", {}).get("blob"),
                "microsoft.appconfiguration/configurationstores": properties.get("endpoint"),
                "microsoft.dbforpostgresql/flexibleservers": properties.get("fullyQualifiedDomainName"),
                AFD_ENDPOINTS: properties.get("hostName"),
                "microsoft.containerregistry/registries": properties.get("loginServer"),
                "microsoft.app/containerapps": properties.get("configuration", {}).get("ingress", {}).get("fqdn"),
                "microsoft.network/privatednszones": defender_asset.get("name") or defender_asset.get("resourceName"),
                "microsoft.cognitiveservices/accounts": properties.get("endpoint"),
            }
        except IndexError:
            fqdn_mapping = {}
        # pylint: disable=line-too-long
        function_mapping = {
            "microsoft.network/privateendpoints": "Private endpoint that links the private link and the nic together",
            "microsoft.network/networkinterfaces": "Network Interface that connects to everything internal to the resource group",
            "microsoft.network/privatednszones": "Dns zone that will connect to the private endpoint and network interfaces",
            "microsoft.network/privatednszones/virtualnetworklinks": "Link for the Private DNS zone back to the vnet",
            "microsoft.app/containerapps": "Application runner that houses the running Docker Container",
            "microsoft.network/publicipaddresses": "Public ip address used for load balancing the container apps",
            "microsoft.storage/storageaccounts": "Storage blob to house unstructured files uploaded to the platform",
            "microsoft.network/networksecuritygroups": "Network protection for internal communications and load balancing",
            "microsoft.network/networkwatchers/flowlogs": "Logs that determine the flow of traffic",
            "microsoft.sql/servers/databases": "Database that houses application logs",
            "microsoft.network/virtualnetworks": "Network Interface that determines what the valid IP range is for all internal resources",
            "microsoft.portal/dashboards": "Dashboard that shows the status of the application and traffic",
            "microsoft.dataprotection/backupvaults": "Azure Blob Storage Account backup location",
            "microsoft.keyvault/vaults": "To securely store API keys, passwords, certificates, or cryptographic keys",
            "microsoft.managedidentity/userassignedidentities": "Identity that connects all internal resources in the resource group",
            "microsoft.app/managedenvironments": "Application environment to connect to the vnet",
            "microsoft.sql/servers": "Server that will house the database for the application logs",
            "microsoft.sql/servers/encryptionprotector": "Server encryption",
            "microsoft.appconfiguration/configurationstores": "Configure, store, and retrieve parameters and settings. Store configuration for all system components in the environment",
            "microsoft.insights/metricalerts": "Alerts that trigger when exceptions hit above 100",
            "microsoft.insights/webtests": "Test to ensure the integrity of the app and alert when availability drops",
            "microsoft.insights/components": "Insights and mapping for the data flow through the platform container application",
            "microsoft.dbforpostgresql/flexibleservers": "Application Database for OpenAI and Automation containers",
            "microsoft.network/loadbalancers": "Load Balancer that handles the load traffic for the containerapp",
            "microsoft.insights/activitylogalerts": "Alert rule to send an email to the Action Group when the trigger event happens",
            "microsoft.operationalinsights/workspaces": "Collection of Logs contained in a workspace",
            "microsoft.insights/actiongroups": "Action Group to send Emails to when alerts trigger",
            "microsoft.network/networkwatchers": "Monitor on the network to look for any suspecious activity",
            "microsoft.app/managedenvironments/certificates": "Tls cert for the application environment",
            "microsoft.authorization/roledefinitions": "Custom role definition",
            "microsoft.alertsmanagement/actionrules": "Alert Processing Rule to show when to trigger",
            "microsoft.network/frontdoorwebapplicationfirewallpolicies": "Waf protection policy that connects to the firewall and frontdoor",
            "microsoft.cdn/profiles": "Monitoring and controlling inbound and outbound traffic to the environment. Functions as a Web Application Firewall (WAF) and performs Network Address Translation (NAT) connecting public networks to a series of private tenant Virtual Networks (VNets)",
            "microsoft.resourcegraph/queries": "Query to return all resources in the SaaS subscription in the resource graph",
            "microsoft.network/firewallpolicies": "Firewall policy that connects to frontdoor and handles our traffic coming into the system",
            AFD_ENDPOINTS: "Endpoint that all of the routes attach to",
            "microsoft.containerregistry/registries": "House the Docker container image for ContainerApp pull",
            "microsoft.operationalinsights/querypacks": "Log analytics query that loads default queries for running",
            "microsoft.alertsmanagement/smartdetectoralertrules": "Failure Anomalies notifies you of an unusual rise in the rate of failed HTTP requests or dependency calls.",
        }
        # pylint: enable=line-too-long
        from regscale.models import regscale_models

        mapped_asset = IntegrationAsset(
            name=defender_asset.get("resourceName", asset_id),
            description=generate_html_table_from_dict(defender_asset),
            other_tracking_number=asset_id,
            azure_identifier=asset_id,
            external_id=asset_id,
            identifier=asset_id,
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Software,
            parent_id=self.plan_id,
            parent_module=(
                regscale_models.Component.get_module_slug()
                if self.is_component
                else regscale_models.SecurityPlan.get_module_slug()
            ),
            status=regscale_models.AssetStatus.Active,
            software_function=function_mapping.get(resource_type, properties.get("description")),
            ip_address=defender_asset.get("ipAddress") or ip_mapping.get(resource_type, properties.get("ipAddress")),
            is_public_facing=resource_type in ["microsoft.cdn/profiles", AFD_ENDPOINTS],
            is_authenticated_scan=resource_type
            not in ["microsoft.alertsmanagement/actionrules", "microsoft.alertsmanagement/smartdetectoralertrules"],
            is_virtual=True,
            baseline_configuration="Azure Hardening Guide",
            component_names=[resource_type],
            source_data=defender_asset,
        )
        if fqdn := fqdn_mapping.get(resource_type, properties.get("dnsSettings", {}).get("fqdn")):
            mapped_asset.fqdn = fqdn
            mapped_asset.description += f"<p>FQDN: {fqdn}</p>"
        return mapped_asset
