from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from lxml import etree

from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models import Asset, Component, InterConnection, Link, PortsProtocol, Property, Reference

logger = create_logger()

namespaces = {
    "oscal": "http://csrc.nist.gov/ns/oscal/1.0",
    "fedramp": "https://fedramp.gov/ns/oscal",
}

COMP = "Component"
REMARKS_XPATH = "oscal:remarks/p/text()"


# Use a helper function to safely get the first item in a list or return None
def safe_first_item(lst):
    return lst[0] if lst else None


def parse_common_component_data(component):
    """Parse common data for all component types."""
    component_data = {
        "uuid": component.get("uuid"),
        "type": component.get("type"),
        "title": safe_first_item(component.xpath("oscal:title/text()", namespaces=namespaces)),
        "description": safe_first_item(component.xpath("oscal:description/oscal:p/text()", namespaces=namespaces)),
        "status": safe_first_item(component.xpath("oscal:status/@state", namespaces=namespaces)),
        "remarks": " ".join(component.xpath(REMARKS_XPATH, namespaces=namespaces)),
    }
    return component_data


def parse_interconnection_data(component: etree.Element) -> Dict:
    """
    Parse data specific to interconnection components.

    :param etree.Element component: The component XML element
    :return: A dictionary of interconnection data
    :rtype: Dict
    """
    interconnection_data = {
        "direction": safe_first_item(component.xpath('oscal:prop[@name="direction"]/@value', namespaces=namespaces)),
        "ipv4_address_local": safe_first_item(
            component.xpath(
                'oscal:prop[@name="ipv4-address"][@class="local"]/@value',
                namespaces=namespaces,
            )
        ),
        "ipv4_address_remote": safe_first_item(
            component.xpath(
                'oscal:prop[@name="ipv4-address"][@class="remote"]/@value',
                namespaces=namespaces,
            )
        ),
        "service_processor": safe_first_item(
            component.xpath(
                'oscal:prop[@name="service-processor"][@ns="https://fedramp.gov/ns/oscal"]/@value',
                namespaces=namespaces,
            )
        ),
        "information": safe_first_item(
            component.xpath(
                'oscal:prop[@name="information"][@ns="https://fedramp.gov/ns/oscal"]/@value',
                namespaces=namespaces,
            )
        ),
        "port_or_circuit_name": safe_first_item(
            component.xpath(
                'oscal:prop[@name="port" or @name="circuit"][@ns="https://fedramp.gov/ns/oscal"]/@name',
                namespaces=namespaces,
            )
        ),
        "port_or_circuit_value": safe_first_item(
            component.xpath(
                'oscal:prop[@name="port" or @name="circuit"][@ns="https://fedramp.gov/ns/oscal"]/@value',
                namespaces=namespaces,
            )
        ),
        "connection_security": safe_first_item(
            component.xpath(
                'oscal:prop[@name="connection-security"][@ns="https://fedramp.gov/ns/oscal"]/@value',
                namespaces=namespaces,
            )
        ),
        "connection_security_remarks": safe_first_item(
            component.xpath(
                'oscal:prop[@name="connection-security"][@ns="https://fedramp.gov/ns/oscal"]/oscal:remarks/oscal:p/text()',
                namespaces=namespaces,
            )
        ),
    }
    return interconnection_data


def parse_roles(component: etree.Element, component_data: Dict) -> list:
    """Parse responsible roles for a component.

    :param etree.Element component: The component XML element
    :param Dict component_data: The component data dictionary
    :return: A list of responsible roles
    :rtype: list
    """
    roles = []
    for role in component.xpath("oscal:responsible-role", namespaces=namespaces):
        role_data = dict()
        role_data["role_id"] = role.get("role-id")
        role_data["party_uuid"] = safe_first_item(role.xpath("oscal:party-uuid/text()", namespaces=namespaces))
        if role_data["role_id"] == "asset-owner":
            component_data["asset_owner"] = role_data["party_uuid"]
        role_data["job_title"] = safe_first_item(
            role.xpath('oscal:prop[@name="job-title"]/@value', namespaces=namespaces)
        )
        roles.append(role_data)
    return roles


def parse_links(component, component_data):
    links = component.xpath("oscal:link/@href", namespaces=namespaces)
    rels = component.xpath("oscal:link/@rel", namespaces=namespaces)
    component_data["links"] = [
        {"rel": rel, "component_uuid": component_data["uuid"], "href": href} for rel, href in zip(rels, links)
    ]


def parse_properties(component, component_data):
    properties = []
    for prop in component.xpath("oscal:prop", namespaces=namespaces):
        name = prop.get("name")
        value = prop.get("value")
        remarks = safe_first_item(prop.xpath("oscal:remarks/oscal:p/text()", namespaces=namespaces))
        properties.append({"key": name, "value": value, "remarks": remarks})
    logger.debug(f"Parsed {len(properties)} properties")
    if "properties" in component_data:
        component_data["properties"].extend(properties)
    else:
        component_data["properties"] = properties
    return component_data


def parse_component(component):
    component_data: dict()
    component_data = parse_common_component_data(component)
    parse_links(component, component_data)
    component_data["responsible_roles"] = parse_roles(component, component_data)
    component_data = parse_properties(component, component_data)
    # this is a seperate module interconnections in regscale
    if component_data["type"] == "interconnection":
        # Parse properties using specific XPath queries and the safe_first_item function
        interconnection_data = parse_interconnection_data(component)
        component_data = {**component_data, **interconnection_data}

        properties = [
            {
                "key": "service-processor",
                "value": component_data.get("service_processor"),
            },
            {
                "key": "ipv4_address_local",
                "value": component_data.get("ipv4_address_local"),
            },
            {
                "key": "ipv4_address_remote",
                "value": component_data.get("ipv4_address_remote"),
            },
            {"key": "direction", "value": component_data.get("direction")},
            {"key": "information", "value": component_data.get("information")},
            {
                "key": "connection_security",
                "value": component_data.get("connection_security"),
            },
            {
                "key": "connection_security_remarks",
                "value": component_data.get("connection_security_remarks"),
            },
        ]

        component_data["properties"] = properties
        # Parse responsible roles
        component_data["aoid_remote"] = safe_first_item(
            component.xpath(
                'oscal:responsible-role[@role-id="isa-authorizing-official-remote"]/oscal:party-uuid/text()',
                namespaces=namespaces,
            )
        )
        component_data["aoid_local"] = safe_first_item(
            component.xpath(
                'oscal:responsible-role[@role-id="isa-authorizing-official-local"]/oscal:party-uuid/text()',
                namespaces=namespaces,
            )
        )
        component_data["isa_remote"] = safe_first_item(
            component.xpath(
                'oscal:responsible-role[@role-id="isa-poc-remote"]/oscal:party-uuid/text()',
                namespaces=namespaces,
            )
        )
        component_data["isa_local"] = safe_first_item(
            component.xpath(
                'oscal:responsible-role[@role-id="isa-poc-local"]/oscal:party-uuid/text()',
                namespaces=namespaces,
            )
        )
        roles = []
        for role in component.xpath("oscal:responsible-role", namespaces=namespaces):
            role_data = dict()
            role_data["party_uuid"] = role.text
            role_data["job_title"] = safe_first_item(
                role.xpath('oscal:prop[@name="job-title"]/@value', namespaces=namespaces)
            )
            roles.append(role_data)
        component_data["responsible_roles"] = roles

    elif component_data["type"] == "service":
        # Parsing logic for service type
        component_data["purpose"] = " ".join(component.xpath("oscal:purpose/text()", namespaces=namespaces))
        component_data["used_by"] = safe_first_item(
            component.xpath('oscal:prop[@name="used-by"]/@value', namespaces=namespaces)
        )

        protocols = []
        for protocol in component.xpath("oscal:protocol", namespaces=namespaces):
            protocol_data = dict()
            protocol_data["used_by"] = safe_first_item(
                component.xpath(
                    'oscal:prop[@name="used-by"][@ns="https://fedramp.gov/ns/oscal"]/@value',
                    namespaces=namespaces,
                )
            )
            protocol_data["name"] = protocol.get("name")
            protocol_data["port_range_start"] = safe_first_item(
                protocol.xpath("oscal:port-range/@start", namespaces=namespaces)
            )
            protocol_data["port_range_end"] = safe_first_item(
                protocol.xpath("oscal:port-range/@end", namespaces=namespaces)
            )
            protocol_data["transport"] = safe_first_item(
                protocol.xpath("oscal:port-range/@transport", namespaces=namespaces)
            )
            protocols.append(protocol_data)

        component_data["protocols"] = protocols
        component_data["remarks"] = (
            " ".join(component.xpath(REMARKS_XPATH, namespaces=namespaces))
            if component.xpath(REMARKS_XPATH, namespaces=namespaces)
            else None
        )

    elif component_data["type"] == "subnet":
        # Parsing logic for subnet type
        component_data["asset_id"] = safe_first_item(
            component.xpath('oscal:prop[@name="asset-id"]/@value', namespaces=namespaces)
        )
        component_data["ipv4_subnet"] = safe_first_item(
            component.xpath('oscal:prop[@name="ipv4-subnet"]/@value', namespaces=namespaces)
        )
        component_data["is_scanned"] = safe_first_item(
            component.xpath('oscal:prop[@name="is-scanned"]/@value', namespaces=namespaces)
        )

    elif component_data["type"] == "hardware":
        # Parsing logic for hardware type
        component_data["asset_type"] = safe_first_item(
            component.xpath('oscal:prop[@name="asset-type"]/@value', namespaces=namespaces)
        )
        component_data["vendor_name"] = safe_first_item(
            component.xpath('oscal:prop[@name="vendor-name"]/@value', namespaces=namespaces)
        )
        component_data["model"] = safe_first_item(
            component.xpath('oscal:prop[@name="model"]/@value', namespaces=namespaces)
        )
        component_data["version"] = safe_first_item(
            component.xpath('oscal:prop[@name="version"]/@value', namespaces=namespaces)
        )

    elif component_data["type"] == "software":
        # Parsing logic for software type
        component_data["asset_type"] = safe_first_item(
            component.xpath('oscal:prop[@name="asset-type"]/@value', namespaces=namespaces)
        )
        component_data["baseline_configuration_name"] = safe_first_item(
            component.xpath(
                'oscal:prop[@name="baseline-configuration-name"]/@value',
                namespaces=namespaces,
            )
        )
        component_data["allows_authenticated_scan"] = safe_first_item(
            component.xpath(
                'oscal:prop[@name="allows-authenticated-scan"]/@value',
                namespaces=namespaces,
            )
        )

    return component_data


def map_asset_status(status) -> str:
    """Map asset status from OSCAL to internal representation."""
    status_mapping = {
        "operational": "Active (On Network)",
        "disposition": "Decommissioned",
        "under-development": "Off-Network",
    }
    return status_mapping.get(status, "Active (On Network)")


# Asset Creation Functions
def create_asset(component_data: Dict, user_id: str, spp_id: int) -> Optional[Dict]:
    """
    Creates an asset record in the database
    :param Dict component_data:
    :param str user_id:
    :param int spp_id:
    :return: Dict of the created asset, if successful
    :rtype: Optional[Dict]
    """
    if asset := Asset(
        name=component_data["title"],
        description=component_data["description"],
        status=map_asset_status(component_data["status"]),
        assetType="Other",
        assetOwnerId=user_id,
        parentId=spp_id,
        parentModule="securityplans",
        ram=0,
        diskStorage=0,
        cpu=0,
        assetCategory=("software" if component_data["type"] == "software" else "hardware"),
        createdById=user_id,
        lastUpdatedById=user_id,
    ).create():
        return asset.dict()
    return None


def create_links(*args, **kwargs) -> list:
    """
    Creates links for a component in RegScale.

    :param args: list of links
    :param kwargs: component, parent_id, parent_module, user_id, etc.
    :return: list of created links responses
    :rtype: list
    """
    links = args[0]
    component = kwargs.get("component")
    parent_id = kwargs.get("parent_id")
    parent_module = kwargs.get("parent_module")
    user_id = kwargs.get("user_id")
    api_handler = kwargs.get("api_handler")
    link_responses = []
    for link in links:
        if not link["href"].startswith("#"):
            if link["component_uuid"] == component["uuid"]:
                obj = Link(
                    title=link["rel"],
                    url=link["href"],
                    parentID=parent_id,
                    parentModule=parent_module,
                    createdById=user_id,
                    lastUpdatedById=user_id,
                )
                resp = api_handler.post("/api/links", data=obj.dict())
                link_responses.append(resp)
        else:
            obj = Reference(
                title=link["rel"],
                identificationNumber=link["href"],
                link=link["href"],
                referenceType="Other",
                parentId=parent_id,
                parentModule=parent_module,
                createdById=user_id,
            )
            obj.create()
    return link_responses


def create_component_based_on_type(
    component_data: Dict, user_id: str, ssp_id: int, api_handler: APIHandler
) -> Tuple[int, str]:
    """
    Create a component based on its type and return the component ID and module.

    :param Dict component_data: The data for the component.
    :param str user_id: User ID.
    :param int ssp_id: SSP ID.
    :param APIHandler api_handler: API handler instance.
    :return: Tuple of component ID and module.
    :rtype: Tuple[int, str]
    """
    if component_data["type"] == "interconnection":
        logger.info(f"Creating interconnection for component {component_data['uuid']}")
        if response := create_interconnection(component_data, user_id, ssp_id):
            return getattr(response, "id", 0), "interconnects"
        return 0, "interconnects"

    elif component_data["type"] in ["subnet", "hardware", "software"]:
        logger.info(f"Creating asset for component {component_data['uuid']}")
        if response := create_asset(component_data, user_id, ssp_id):
            return response.get("id", 0), "assets"
        return 0, "assets"

    elif component_data["type"] == "this-system":
        return 0, "this-system"

    else:
        logger.info(f"Creating component for component {component_data['uuid']}")
        if response := create_component(component_data, ssp_id, user_id, api_handler):
            return response.get("id", 0), "components"
        return 0, "components"


def create_related_items(
    component_data: Dict,
    comp_id: int,
    regcomp_module: str,
    trv: FedrampTraversal,
    api_handler: APIHandler,
    user_id: str,
) -> None:
    """
    Create related items for a component (properties, protocols, links).

    :param Dict component_data: The data for the component.
    :param int comp_id: Component ID.
    :param str regcomp_module: The module name for the component.
    :param FedrampTraversal trv: FedRAMP Traversal object.
    :param APIHandler api_handler: API handler instance.
    :param str user_id: User ID.
    :rtype: None
    """
    for item_type in ["properties", "protocols", "links"]:
        if item_type in component_data and component_data[item_type]:
            logger.info(f"Creating {item_type} for component {component_data['uuid']}")
            create_func = globals()[f"create_{item_type}"]
            if response := create_func(
                component_data[item_type],
                component=component_data,
                parent_id=comp_id,
                parent_module=regcomp_module,
                api_handler=api_handler,
                user_id=user_id,
            ):
                if isinstance(response, list):
                    trv.log_info(
                        {
                            "record_type": item_type.capitalize(),
                            "event_msg": f"Created {len(response)} {item_type} for component {component_data['uuid']}.",
                            "model_layer": COMP,
                        }
                    )
                else:
                    trv.log_info(
                        {
                            "record_type": item_type.capitalize(),
                            "event_msg": f"Created {item_type} for component {component_data['uuid']}.",
                            "model_layer": COMP,
                        }
                    )
            else:
                trv.log_error(
                    {
                        "record_type": item_type.capitalize(),
                        "event_msg": f"Failed to create {item_type} for component {component_data['uuid']}.",
                        "missing_element": item_type.capitalize(),
                        "model_layer": COMP,
                    }
                )


def parse_ssp_components(trv: FedrampTraversal) -> Dict:
    """
    Parses the OSCAL XML file and extracts the component data.

    :param FedrampTraversal trv: FedRAMP Traversal object
    :return: Dictionary containing the component data
    :rtype: Dict
    """
    try:
        ssp_id = trv.ssp_id
        api_handler = APIHandler()
        user_id = trv.api.config.get("userId")
        components = trv.root.xpath("//oscal:component", namespaces=namespaces)
        logger.info(f"Found {len(components)} components for parsing.")
        trv.log_info(
            {
                "model_layer": "System Implementation",
                "record_type": "Component",
                "event_msg": f"Found {len(components)} components for parsing.",
            }
        )

        components_dict = {}

        for component in components:
            component_data = parse_component(component)
            comp_id, regcomp_module = create_component_based_on_type(component_data, user_id, ssp_id, api_handler)

            if comp_id == 0:
                continue

            component_data["id"] = comp_id
            component_data["module"] = regcomp_module
            components_dict[component_data["uuid"]] = component_data

            logger.info(f"Component {component_data['uuid']} created.")
            create_related_items(component_data, comp_id, regcomp_module, trv, api_handler, user_id)

        return components_dict

    except Exception as e:
        trv.log_error(
            {
                "record_type": "Component",
                "event_msg": f"Unable to create component {component_data['uuid']}.",
                "missing_element": "Component",
                "model_layer": COMP,
            }
        )
        logger.error(f"Error parsing components item: {str(e)}")


def create_properties(
    *args: Tuple,
    **kwargs: Dict,
) -> list:
    """
    Creates a new property in the Regscale.
    :param Tuple *args: list of properties
    :param Dict **kwargs: parent_id, parent_module, api_handler, user_id, etc.
    :return: list of created properties
    :rtype: list
    """
    properties = args[0]
    parent_id = kwargs.get("parent_id")
    parent_module = kwargs.get("parent_module")
    user_id = kwargs.get("user_id")

    created_properties = []
    for prop in properties:
        prop_obj = Property(
            parentId=parent_id,
            parentModule=parent_module,
            key=prop["key"],
            value=prop["value"],
            createdById=user_id,
        )
        new_prop = prop_obj.create().model_dump()
        logger.info(f"Created property {new_prop['key']} with ID of {new_prop['id']}")
        if new_prop:
            created_properties.append(new_prop)
        else:
            continue
    return created_properties


def create_component(component_data: Dict, ssp_id: int, user_id: str, api_handler: APIHandler) -> Optional[Any]:
    """
    Creates a new component in the OSCAL database.

    :param Dict component_data: The component data
    :param int ssp_id: The ID of the SSP
    :param str user_id: The ID of the user creating the component
    :param APIHandler api_handler: The API handler
    :return: The response object of the newly created component
    :rtype: Optional[Any]
    """
    comp = Component(
        uuid=component_data["uuid"],
        title=component_data["title"],
        description=component_data["description"],
        purpose=component_data["purpose"] if "purpose" in component_data else "",
        componentType=component_data["type"],
        componentOwnerId=(
            component_data["asset_owner"]
            if "asset_owner" in component_data and component_data["asset_owner"] is not None
            else user_id
        ),
        securityPlansId=ssp_id,
        status=(
            "Active" if "status" in component_data and component_data["status"] == "operational" else "Draft/Pending"
        ),
        cmmcAssetType=(component_data["asset_type"] if "asset_type" in component_data else None),
    )
    # insert component
    resp_json = api_handler.post("/api/components", data=comp.model_dump()).json()
    if resp_json:
        create_component_mapping(resp_json, ssp_id=ssp_id)
        return resp_json
    else:
        logger.error(f"failed to insert comp {comp.dict()}")
        return None


def create_component_mapping(component_data: Dict, ssp_id: int) -> None:
    """
    Creates a new component mapping record.

    :param Dict component_data: The component data
    :param int ssp_id: The ID of the SSP
    :rtype: None
    """
    from regscale.models.regscale_models.component_mapping import ComponentMapping

    logger.info(f"Creating component mapping for component {component_data['id']}")
    new_comp_mapping = ComponentMapping(
        componentId=component_data["id"],
        securityPlanId=ssp_id,
        isPublic=True,
    ).create()
    logger.info(f"Successfully created component mapping {new_comp_mapping.id}")
    return None


def create_protocols(
    *args,
    **kwargs,
) -> Optional[List[Any]]:
    """
    Creates a new ports and protocol record.

    :return: The response object of the newly created component or None
    :rtype: Optional[List[Any]]
    """
    protocols = args[0]
    parent_id = kwargs.get("parent_id")
    parent_module = kwargs.get("parent_module")
    user_id = kwargs.get("user_id")
    responses = []
    for protocol in protocols:
        protocol_obj = PortsProtocol(
            parentId=parent_id,
            parentModule=parent_module,
            startPort=protocol["port_range_start"],
            endPort=protocol["port_range_end"],
            protocol=protocol["transport"],
            service=protocol["name"],
            purpose=None,
            usedBy=protocol["used_by"],
            createdById=user_id,
            lastUpdatedById=user_id,
        )
        response = protocol_obj.create().model_dump()
        responses.append(response)
    return responses


def create_interconnection(component_data: Dict, user_id: str, ssp_id: int) -> Optional[Any]:
    """
    Creates a new interconnection record.

    :param Dict component_data: The component data
    :param str user_id: The ID of the user creating the component
    :param int ssp_id: The ID of the SSP
    :param APIHandler api_handler: The API handler
    :return: API response object
    :rtype: Optional[Any]
    """
    intercon = InterConnection(
        uuid=component_data["uuid"],
        description=component_data["description"],
        name=component_data["title"],
        dataDirection=component_data["direction"],
        status="Approved",
        authorizationType="Interconnect Security Agreement (ISA)",
        createdById=user_id,
        dateCreated=get_current_datetime(),
        dateLastUpdated=get_current_datetime(),
        lastUpdatedById=user_id,
        tenantsId=0,
        parentId=ssp_id,
        parentModule="securityplans",
        externalIpAddress=component_data["ipv4_address_remote"],
        sourceIpAddress=component_data["ipv4_address_local"],
        categorization="Moderate",
        connectionType="Internet or Firewall Rule",
        organization=(
            component_data["aoid_local"] if "aoid_local" in component_data else component_data["aoid_remote"]
        ),
        # component_data['aoid_local'] if 'aoid_local' in component_data else component_data['aoid_remote']
        aOId=user_id,
        # component_data['isa_local'] if 'isa_local' in component_data else component_data['isa_remote']
        interconnectOwnerId=user_id,
        expirationDate=get_expiration_date(),
        agreementDate=get_current_datetime(),
    )

    return intercon.create()


def get_expiration_date() -> str:
    """
    Get the expiration date for an interconnection.

    :return: The expiration date
    :rtype: str
    """
    # Get the current date and time in UTC + 30 days
    now = datetime.utcnow()

    # Add 30 days to the current date and time
    expiration_date = now + timedelta(days=30)

    # Convert to Zulu time format (ISO 8601)
    expiration_date_str = expiration_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return expiration_date_str
