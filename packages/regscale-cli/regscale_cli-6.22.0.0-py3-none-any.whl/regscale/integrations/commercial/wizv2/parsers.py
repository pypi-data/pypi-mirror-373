import json
import logging
from typing import Dict, Optional, Tuple, Union, List, Any

from regscale.integrations.commercial.cpe import extract_product_name_and_version
from regscale.integrations.commercial.wizv2.constants import CONTENT_TYPE
from regscale.integrations.commercial.wizv2.variables import WizVariables
from regscale.models import regscale_models
from regscale.utils import PaginatedGraphQLClient

logger = logging.getLogger("regscale")


def collect_components_to_create(data: List[Dict[str, Any]], components_to_create: List[str]) -> List[str]:
    """
    Collect unique component titles to create from the data.

    :param List[Dict[str, Any]] data: List of Wiz data.
    :param List[str] components_to_create: List of component titles to create.
    :return: List of unique component titles to create.
    :rtype: List[str]
    """
    for row in data:
        component_title = row.get("type", "").title().replace("_", " ")
        if component_title and component_title not in components_to_create:
            components_to_create.append(component_title)
    return list(set(components_to_create))


def handle_container_image_version(image_tags: list, name: str) -> str:
    """
    Handle container image version

    :param list image_tags: image tags for container image
    :param str name: Name
    :return: Container image version
    :rtype: Optional[str]
    """
    result = ""

    # Check if `image_tags` has any items
    if any(image_tags):
        result = image_tags[0]

    # If `image_tags` is empty, then check the next condition
    elif name and len(name.split(":")) > 1:
        result = name.split(":")[1]

    # Return the final result
    return result


def handle_software_version(wiz_entity_properties: Dict, asset_category: str) -> Optional[str]:
    """
    Handle software version

    :param Dict wiz_entity_properties: Wiz entity properties
    :param str asset_category: Asset category
    :return: Software version
    :rtype: Optional[str]
    """
    return (
        wiz_entity_properties.get("version")
        if wiz_entity_properties.get("version") and asset_category == regscale_models.AssetCategory.Software
        else None
    )


def get_software_name_from_cpe(wiz_entity_properties: Dict, name: str) -> Dict:
    """
    Get software name from wiz CPE
    :param Dict wiz_entity_properties: Wiz entity properties
    :param str name: Name
    :return: Software name
    :rtype: Dict
    """
    cpe_info_dict = {
        "name": name,
        "part": None,
        "software_name": None,
        "software_version": None,
        "software_vendor": None,
    }
    if "cpe" in wiz_entity_properties and wiz_entity_properties.get("cpe"):
        cpe_info_dict = extract_product_name_and_version(wiz_entity_properties.get("cpe", ""))
        cpe_info_dict["name"] = name
    return cpe_info_dict


def get_latest_version(wiz_entity_properties: Dict) -> Optional[str]:
    """
    Get the latest version from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Latest version
    :rtype: Optional[str]
    """
    # Retrieve the latest version and current version
    latest_version = wiz_entity_properties.get("latestVersion")
    current_version = wiz_entity_properties.get("version")

    # Return the latest version if it exists, otherwise return the current version
    return latest_version if latest_version is not None else current_version


def get_cloud_identifier(
    wiz_entity_properties: Dict,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Get cloud identifier
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Cloud identifier
    :rtype: Tuple[Optional[str], Optional[str]]
    """
    # Define common keywords for each provider
    aws_keywords = ["aws", "amazon", "ec2"]
    azure_keywords = ["azure", "microsoft"]
    google_keywords = ["google", "gcp", "google cloud"]

    provider_unique_id = (
        wiz_entity_properties.get("providerUniqueId").lower() if wiz_entity_properties.get("providerUniqueId") else ""
    )

    # Check for AWS identifiers
    if any(keyword in provider_unique_id for keyword in aws_keywords):
        return "aws", provider_unique_id

    # Check for Azure identifiers
    if any(keyword in provider_unique_id for keyword in azure_keywords):
        return "azure", provider_unique_id

    # Check for Google identifiers
    if any(keyword in provider_unique_id for keyword in google_keywords):
        return "google", provider_unique_id

    # If none of the above, check if there is any providerUniqueId
    if provider_unique_id:
        return "other", provider_unique_id

    # Return None if no identifier is found
    return None, None


def handle_provider(wiz_entity_properties: Dict) -> Dict:
    """
    Handle provider
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Provider
    :rtype: Dict
    """
    provider, identifier = get_cloud_identifier(wiz_entity_properties)
    return {
        "awsIdentifier": identifier if provider == "aws" else None,
        "azureIdentifier": identifier if provider == "azure" else None,
        "googleIdentifier": identifier if provider == "google" else None,
        "otherCloudIdentifier": identifier if provider == "other" else None,
    }


def parse_memory(memory_str: str) -> int:
    """
    Parse memory string to integer (GiB to MiB conversion if needed)

    :param str memory_str: Memory string (e.g., '2Gi', '512Mi', '1.5Gi')
    :return: Memory in MiB
    :rtype: int
    """
    if not memory_str or memory_str == "0":
        return 0
    try:
        value = float(memory_str[:-2])
        return int(value * (1024 if memory_str.endswith("Gi") else 1))
    except ValueError:
        logger.warning("Failed to parse memory string: %s", memory_str)
        return 0


def parse_cpu(cpu_str: Union[str, int]) -> int:
    """
    Parse CPU string to integer
    :param Union[str, int] cpu_str: CPU string
    :return: CPU as integer
    :rtype: int
    """
    try:
        return int(float(cpu_str))
    except ValueError:
        return 0


def get_resources(wiz_entity_properties: Dict) -> Dict:
    """
    Extract resources from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Resources dictionary
    :rtype: Dict
    """
    if "resources" in wiz_entity_properties:
        resources_str = wiz_entity_properties.get("resources", "{}")
        try:
            resources = json.loads(resources_str)
            return resources.get("requests", {})
        except json.JSONDecodeError:
            pass
    return {}


def pull_resource_info_from_props(wiz_entity_properties: Dict) -> Tuple[int, int]:
    """
    Pull memory, cpu from properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Memory, CPU
    :rtype: Tuple[int, int]
    """
    resources = get_resources(wiz_entity_properties)
    memory = parse_memory(resources.get("memory", ""))
    cpu = parse_cpu(resources.get("cpu", 0))
    cpu = parse_cpu(wiz_entity_properties.get("vCPUs", cpu))
    return memory, cpu


def get_disk_storage(wiz_entity_properties: Dict) -> int:
    """
    Extract disk storage information.
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Disk storage
    :rtype: int
    """
    try:
        return int(wiz_entity_properties.get("totalDisks", 0))
    except ValueError:
        return 0


def get_network_info(wiz_entity_properties: Dict) -> Dict:
    """
    Extract network information.
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Network information
    :rtype: Dict
    """
    region = wiz_entity_properties.get("region")
    ip4_address, ip6_address, dns, url = get_ip_address(wiz_entity_properties)
    return {
        "region": region,
        "ip4_address": ip4_address,
        "ip6_address": ip6_address,
        "dns": dns,
        "url": url,
    }


def get_product_ids(wiz_entity_properties: Dict) -> Optional[str]:
    """
    Get product IDs from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Product IDs
    :rtype: Optional[str]
    """
    product_ids = wiz_entity_properties.get("_productIDs")
    if product_ids and isinstance(product_ids, list):
        return ", ".join(product_ids)
    return product_ids


def get_ip_address_from_props(network_dict: Dict) -> Optional[str]:
    """
    Get IP address from properties
    :param Dict network_dict: Network dictionary
    :return: IP address if it can be parsed from the network dictionary
    :rtype: Optional[str]
    """
    return network_dict.get("ip4_address") or network_dict.get("ip6_address")


def get_ip_v4_from_props(network_dict: Dict) -> Optional[str]:
    """
    Get IPv4 address from properties
    :param Dict network_dict: Network dictionary
    :return: IPv4 address if it can be parsed from the network dictionary
    :rtype: Optional[str]
    """
    ip = network_dict.get("address")
    if ip:
        logger.info("get_ip_v4_from_props: %s", ip)
    return network_dict.get("address")


def get_ip_v6_from_props(network_dict: Dict) -> Optional[str]:
    """
    Get IPv6 address from properties
    :param Dict network_dict: Network dictionary
    :return: IPv6 address if it can be parsed from the network dictionary
    :rtype: Optional[str]
    """
    return network_dict.get("ip6_address")


def fetch_wiz_data(
    query: str,
    variables: dict,
    topic_key: str,
    token: str,
    api_endpoint_url: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Sends a paginated GraphQL request to Wiz.

    :param str query: The GraphQL query to send.
    :param dict variables: The variables to use in the GraphQL request.
    :param str topic_key: The topic key to use in the paginated request.
    :param str token: The Wiz access token to use in the request.
    :param Optional[str] api_endpoint_url: The API endpoint URL to use in the request.
    :return: Response from the paginated GraphQL request.
    :rtype: List[Dict[str, Any]]
    """

    logger.debug("Sending a paginated request to Wiz API")
    api_endpoint_url = WizVariables.wizUrl if api_endpoint_url is None else api_endpoint_url

    logger.debug("Wiz QUERY: %s" % query)
    client = PaginatedGraphQLClient(
        endpoint=api_endpoint_url,
        query=query,
        headers={
            "Content-Type": CONTENT_TYPE,
            "Authorization": "Bearer " + token,
        },
    )

    # Fetch all results using the client's pagination logic
    logger.debug(f"{variables}, {topic_key}")
    data = client.fetch_all(
        variables=variables,
        topic_key=topic_key,
    )

    return data


def get_ip_address(
    wiz_entity_properties: Dict,
) -> Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]:
    """
    Get ip address from wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: IP4 address, IP6 address, DNS, URL
    :rtype: Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]
    """
    ip4_address = None
    ip6_address = None
    dns = None
    url = None
    if "address" in wiz_entity_properties:
        if wiz_entity_properties.get("addressType") == "IPV4":
            ip4_address = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "IPV6":
            ip6_address = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "DNS":
            dns = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "URL":
            url = wiz_entity_properties.get("address")

    return ip4_address, ip6_address, dns, url
