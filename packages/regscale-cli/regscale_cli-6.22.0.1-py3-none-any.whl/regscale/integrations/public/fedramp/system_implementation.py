# flake8: noqa
"""
System Implementation is a Model Layer in the OSCAL SSP implementation model. The
model is documented at https://pages.nist.gov/OSCAL/concepts/layer/implementation/ssp/
Note that the RegScale SSP Data model collapses several NIST OSCAL model layers together
including Metadata, System Characteristics, and System Implementation.
"""
from typing import Dict, List

from lxml import etree

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.components import parse_ssp_components
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.integrations.public.fedramp.inventory_items import parse_inventory_items
from regscale.integrations.public.fedramp.mappings.user import handle_user
from regscale.integrations.public.fedramp.xml_utils import update_ssp

logger = create_logger()

sc_events = []  # returned after tracking import events
SYSTEM_INFO = "System Information"
SYSTEM_IMP = "System Implementation"


def parse_user_extra_datas(trv: FedrampTraversal):
    root = trv.root

    ssp_updates_dict = {}
    # USERS NOW
    users = []
    users = root.xpath(
        "/ns1:system-security-plan/ns1:system-implementation/ns1:prop[@name='users-internal']/@value",
        namespaces=trv.namespaces,
    )

    if len(users) > 0:
        ssp_updates_dict["internalUsers"] = users[0]
        trv.log_info(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "event_msg": f"Recorded number of internal system users: {ssp_updates_dict['internalUsers']}",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "missing_element": "Number of Internal Users",
            }
        )

    # USERS EXTERNAL
    users = []
    users = root.xpath(
        "/ns1:system-security-plan/ns1:system-implementation/ns1:prop[@name='users-external']/@value",
        namespaces=trv.namespaces,
    )

    if len(users) > 0:
        ssp_updates_dict["externalUsers"] = users[0]
        trv.log_info(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "event_msg": f"Recorded number of external system users: {ssp_updates_dict['externalUsers']}",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "missing_element": "Number of External Users",
            }
        )

    # USERS FUTURE
    users = []
    users = root.xpath(
        "/ns1:system-security-plan/ns1:system-implementation/ns1:prop[@name='users-internal-future']/@value",
        namespaces=trv.namespaces,
    )

    if len(users) > 0:
        ssp_updates_dict["internalUsersFuture"] = users[0]
        trv.log_info(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "event_msg": f"Recorded number of future internal system users: {ssp_updates_dict['internalUsersFuture']}",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "missing_element": "Number of Internal Users (Future)",
            }
        )

    # Users External
    users = []
    users = root.xpath(
        "/ns1:system-security-plan/ns1:system-implementation/ns1:prop[@name='users-external']/@value",
        namespaces=trv.namespaces,
    )

    if len(users) > 0:
        ssp_updates_dict["externalUsersFuture"] = users[0]
        trv.log_info(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "event_msg": f"Recorded number of future external system users: {ssp_updates_dict['externalUsersFuture']}",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "missing_element": "Number of External Users (Future)",
            }
        )

    if len(ssp_updates_dict) > 0:
        update_ssp(ssp_updates_dict, trv.ssp_id)
    else:
        trv.log_error(
            {
                "record_type": SYSTEM_INFO,
                "model_layer": SYSTEM_IMP,
                "missing_element": "Number of Users",
            }
        )


def parse_system_implementation(trv: FedrampTraversal) -> List[Dict[str, str]]:
    """Parse system implementation from OSCAL SSP XML to RegScale SSP JSON

    :param FedrampTraversal trv: FedrampTraversal instance
    :return: List of events
    :rtype: List[Dict[str, str]]
    """

    # Handle:
    # <system-implementation>
    #    <user>
    handle_user(trv)

    # parses Components
    components_dict = parse_ssp_components(trv)
    inventory_items = parse_inventory_items(trv, components_dict)

    # Handle:
    # <system-implementation>
    #    <users-internal>
    #    <users-external>
    #    <users-internal-future>
    parse_user_extra_datas(trv)

    # Handle:
    # <system-implementation>
    #    <leveraged-authorization>
    # parse_leveraged_auth_new(trv)

    return [{"event": "System Implementation parsed successfully"}]


if __name__ == "__main__":
    # Example usage
    app = Application()
    api = Api()
    tree = etree.parse("./artifacts/AwesomeCloudSSP.xml")
    root = tree.getroot()

    ssp_id = 2037
    namespaces = {
        "oscal": "http://csrc.nist.gov/ns/oscal/1.0",
        "fedramp": "https://fedramp.gov/ns/oscal",
        "ns1": "http://csrc.nist.gov/ns/oscal/1.0",
    }
    trv = FedrampTraversal(api=api, root=root, ssp_id=ssp_id, namespaces=namespaces)
    parse_system_implementation(trv)
