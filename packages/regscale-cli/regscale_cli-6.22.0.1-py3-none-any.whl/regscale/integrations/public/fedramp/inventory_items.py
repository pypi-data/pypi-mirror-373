"""
Parse an OSCAL inventory-item element and return its data as a dictionary.
"""

from typing import Any, Dict, Optional

from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.models.regscale_models import Asset, Property

logger = create_logger()


def parse_inventory_item(inventory_item, namespaces):
    """Parse an OSCAL inventory-item element and return its data as a dictionary."""
    inventory_data = {
        "uuid": inventory_item.get("uuid"),
        "description": safe_first_item(inventory_item.xpath("oscal:description/oscal:p/text()", namespaces=namespaces)),
        "props": {},
    }
    oscal_remarks = "oscal:remarks/oscal:p/text()"

    # Parse properties
    for prop in inventory_item.xpath("oscal:prop", namespaces=namespaces):
        name = prop.get("name")
        value = prop.get("value")
        _ = safe_first_item(prop.xpath(oscal_remarks, namespaces=namespaces))
        inventory_data["props"][name] = value

    # Parse responsible parties
    inventory_data["responsible_parties"] = []
    for rp in inventory_item.xpath("oscal:responsible-party", namespaces=namespaces):
        role_id = rp.get("role-id")
        party_uuid = safe_first_item(rp.xpath("oscal:party-uuid/text()", namespaces=namespaces))
        inventory_data["responsible_parties"].append({"role_id": role_id, "party_uuid": party_uuid})

    # Parse implemented components
    inventory_data["implemented_components"] = []
    for ic in inventory_item.xpath("oscal:implemented-component", namespaces=namespaces):
        component_uuid = ic.get("component-uuid")
        remarks = safe_first_item(ic.xpath(oscal_remarks, namespaces=namespaces))
        inventory_data["implemented_components"].append({"component_uuid": component_uuid, "remarks": remarks})

    # Parse remarks
    inventory_data["remarks"] = safe_first_item(inventory_item.xpath(oscal_remarks, namespaces=namespaces))

    return inventory_data


# Utility function to safely get the first item in a list or return None
def safe_first_item(lst):
    return lst[0] if lst else None


def get_dict_value(outer_key: str, inner_key: str, source_dict: Dict) -> Optional[Any]:
    """Get the value of a nested dictionary key."""
    # logger.info(f"Getting value for key {outer_key} and subkey {inner_key} from source dict. {source_dict}")

    outer_dict = source_dict.get(outer_key, None)
    if outer_dict is not None and isinstance(outer_dict, dict):
        val = outer_dict.get(inner_key, None)
        logger.debug(f"{val=}")
        return val
    return None


def map_asset_status(status) -> str:
    """Map asset status from OSCAL to internal representation."""
    status_mapping = {
        "operational": "Active (On Network)",
        "disposition": "Decommissioned",
        "under-development": "Off-Network",
    }
    return status_mapping.get(status, "Active (On Network)")


def parse_inventory_item_to_asset(
    parsed_inventory_item: Dict, parent_id: int, parent_module: str, user_id: str
) -> dict:
    """
    Convert parsed OSCAL inventory-item XML data to a RegScale Asset object.
    """
    props = parsed_inventory_item.get("props")
    # Initialize asset fields with default or None values
    asset = Asset(
        parentId=parent_id,
        parentModule=parent_module,
        uuid=parsed_inventory_item.get("uuid", None),
        name=parsed_inventory_item.get("description", "Asset")[:420],  # Need to truncate name when using description
        description=parsed_inventory_item.get("description", None),
        ipAddress=props.get("ipv4-address", None),
        macAddress=props.get("mac-address", None),
        manufacturer=props.get("vendor-name", None),
        model=props.get("model", None),
        serialNumber=props.get("serial-number", None),
        assetCategory="Hardware",
        assetType=props.get("asset-type", "Other"),
        fqdn=props.get("fqdn", None),
        notes=props.get("remarks", None),
        operatingSystem=props.get("os-name", None),
        oSVersion=props.get("os-version", None),
        netBIOS=props.get("netbios-name", None),
        iPv6Address=props.get("ipv6-address", None),
        ram=0,
        diskStorage=0,
        cpu=0,
        assetOwnerId=user_id,
        status=map_asset_status(parsed_inventory_item.get("status", None)),
        isPublic=True if props.get("public", "no") == "yes" else False,
    ).create()

    return asset.dict()


def parse_inventory_items(trv: FedrampTraversal, components_dict: Dict):
    """Parse an OSCAL inventory-item element and return its data as a dictionary."""
    try:
        ssp_id = trv.ssp_id
        # logger.info(f"ssp_id: {ssp_id}")
        root = trv.root
        app = trv.api.app
        user_id = app.config.get("userId", None)
        namespaces = trv.namespaces
        # logger.info(f"userid: {app.config.get('userId')}")
        if not namespaces:
            namespaces = {"oscal": "http://csrc.nist.gov/ns/oscal/1.0"}
        inventory_items = root.xpath("//oscal:inventory-item", namespaces=namespaces)

        trv.log_info(
            {
                "model_layer": "system-implementation",
                "record_type": "inventory-item",
                "event_msg": f"Found {len(inventory_items)} inventory items.",
            }
        )

        for inventory_item in inventory_items:
            item = parse_inventory_item(inventory_item, namespaces)
            new_parent_asset = parse_inventory_item_to_asset(
                item,
                parent_id=ssp_id,
                parent_module="securityplans",
                user_id=app.config.get("userId"),
            )

            if new_parent_asset is not None:
                trv.log_info(
                    {
                        "model_layer": "system-implementation",
                        "record_type": "inventory-item",
                        "event_msg": f"Asset {new_parent_asset['name']} created.",
                    }
                )

                properties_results = []
                for key in item.get("props").keys():
                    value = item.get("props").get(key)
                    prop_obj = Property(
                        parentId=new_parent_asset["id"],
                        parentModule="assets",
                        key=key,
                        value=value,
                        createdById=user_id,
                    ).create()
                    properties_results.append(prop_obj.dict())

                if property_failure_results := [r for r in properties_results if not r]:
                    trv.log_error(
                        {
                            "model_layer": "system-implementation",
                            "record_type": "inventory-item",
                            "event_msg": f"Some properties failed to create. ({len(properties_results) - len(property_failure_results)}/{len(properties_results)} were created.)",
                        }
                    )

            else:
                trv.log_error(
                    {
                        "model_layer": "system-implementation",
                        "record_type": "inventory-item",
                        "event_msg": f"Asset {new_parent_asset['name']} failed to create.",
                    }
                )

            trv.log_info(
                {
                    "model_layer": "system-implementation",
                    "record_type": "inventory-item",
                    "event_msg": f"Asset {new_parent_asset['name']} created.",
                }
            )

            implemented_components = item.get("implemented_components")

            trv.log_info(
                {
                    "model_layer": "system-implementation",
                    "record_type": "inventory-item",
                    "event_msg": f"Found {len(implemented_components)} implemented components within inventory-item '{item.get('uuid')}'.",
                }
            )

            if implemented_components:
                item["components"] = []

                for imp_component in implemented_components:
                    if not isinstance(components_dict, dict):
                        logger.debug(components_dict)
                        logger.info("Components do not exist yet.")
                        continue
                    comp = components_dict.get(imp_component.get("component_uuid"))
                    comp_id = comp.get("id") if comp else None
                    item["components"].append(comp)
                    # logger.info(f"Found implemented component: {json.dumps(comp,indent=4)}")
                    if asset := Asset.get_object(comp_id):
                        logger.info("Fetched Linked Asset")

                        asset.parentId = new_parent_asset["name"]
                        asset.parentModule = "assets"
                        response = asset.save()

                        if response.ok:
                            logger.info("Asset Updated!")
                            trv.log_info(
                                {
                                    "model_layer": "system-implementation",
                                    "record_type": "inventory-item",
                                    "event_msg": f"Asset {asset['name']} updated.",
                                }
                            )
                            continue
                        else:
                            trv.log_error(
                                {
                                    "model_layer": "system-implementation",
                                    "record_type": "inventory-item",
                                    "event_msg": (f"Asset {asset['name']}" "failed to update.",),
                                }
                            )

    except Exception as e:
        logger.error(f"Error parsing inventory item: {str(e)}")

        # logger.info(f"Parsed inventory item: {json.dumps(item)}")
