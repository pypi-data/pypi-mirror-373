# flake8: noqa
"""LeveragedAuthMapping classes for FedRAMP."""

from typing import List, Optional

from lxml import etree

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.core.app.utils.XMLIR import XMLIR2, XMLIRTraversal
from regscale.models.regscale_models.system_role import SystemRole

logger = create_logger()


class UserMappingIRAuthorizedPrivilegesIR(XMLIR2):
    title: Optional[str] = None

    def get_title(self, trv: XMLIRTraversal) -> Optional[str]:
        """The title of the authorized privilege."""
        vlist = trv.el_xpath(".//oscal:title")
        return vlist[0].text if vlist else None

    description: Optional[str] = None

    def get_description(self, trv: XMLIRTraversal) -> Optional[str]:
        """The description of the authorized privilege."""
        vlist = trv.el_xpath(".//oscal:description")
        return vlist[0].text if vlist else None


class UserMappingIR(XMLIR2):
    title: Optional[str] = None

    def get_title(self, trv: XMLIRTraversal) -> Optional[str]:
        """The user's title"""
        vlist = trv.el_xpath(".//oscal:title")
        return vlist[0].text if vlist else None

    type: Optional[str] = None

    def get_type(self, trv: XMLIRTraversal) -> Optional[str]:
        """The type of the user."""
        vlist = trv.el_xpath('.//oscal:prop[@name="type"]')
        return vlist[0].get("value") if vlist else None

    sensitivity: Optional[str] = None

    def get_sensitivity(self, trv: XMLIRTraversal) -> Optional[str]:
        """The sensitivity of the user."""
        vlist = trv.el_xpath('.//oscal:prop[@name="sensitivity"]')

        return vlist[0].get("value") if vlist else None

    privilege_level: Optional[str] = None

    def get_privilege_level(self, trv: XMLIRTraversal) -> Optional[str]:
        """The privilege level of the user."""
        vlist = trv.el_xpath('.//oscal:prop[@name="privilege-level"]')

        return vlist[0].get("value") if vlist else None

    role_id: Optional[str] = None

    def get_role_id(self, trv: XMLIRTraversal) -> Optional[str]:
        """The role id of the user."""
        vlist = trv.el_xpath(".//oscal:role-id")

        return vlist[0].text if vlist else None

    authorized_privileges: List[UserMappingIRAuthorizedPrivilegesIR] = []

    def get_authorized_privileges(self, trv: XMLIRTraversal) -> List[UserMappingIRAuthorizedPrivilegesIR]:
        """The authorized privileges of the user."""
        vlist = trv.el_xpath(".//oscal:authorized-privilege")

        return [
            UserMappingIRAuthorizedPrivilegesIR(
                XMLIRTraversal(xpathToThis="....", el=el, root=trv.root, namespaces=trv.namespaces)
            )
            for el in vlist
        ]


def handle_user(trv: FedrampTraversal):
    """
    Extract user nodes from the SSP and send them to the RegScale API.
    """
    try:
        api = trv.api
        root = trv.root

        namespaces = {
            "oscal": "http://csrc.nist.gov/ns/oscal/1.0",
            "fedramp": "https://fedramp.gov/ns/oscal",
        }

        # Extract user nodes
        users = root.xpath(".//oscal:system-implementation/oscal:user", namespaces=namespaces)

        if len(users) == 0:
            trv.log_info(
                {
                    "model_layer": "system-implementation",
                    "record_type": "user",
                    "event_msg": "No users / System Roles detected.",
                }
            )

        for elem in users:
            res = UserMappingIR(XMLIRTraversal(xpathToThis="....", el=elem, root=root, namespaces=namespaces))

            logger.debug("parsed object", res)

            sending = {
                "id": 0,
                # Title
                "roleName": res.title,
                "fedrampRoleId": res.role_id,
                "roleType": res.type,
                "assignedUserId": None,
                "accessLevel": res.privilege_level,
                "sensitivityLevel": res.sensitivity,
                "privilegeDescription": res.privilege_level,
                "functions": ", ".join([str(dict(r)) for r in res.authorized_privileges]),
                "securityPlanId": trv.ssp_id,
                "createdById": api.config["userId"],
                "isPublic": True,
            }

            system_roles = SystemRole(**sending)
            if system_roles.insert_systemrole(api.app):
                trv.log_info(
                    {
                        "model_layer": "system-implementation",
                        "record_type": "user",
                        "event_msg": f"Created user '{res.title}' with role id '{res.role_id}'",
                    }
                )

                logger.info("System role was created successfully in RegScale.")
            else:
                trv.log_error(
                    {
                        "model_layer": "system-implementation",
                        "record_type": "user",
                        "event_msg": "Failed to create user",
                    }
                )
    except Exception as e:
        trv.log_error(
            {
                "model_layer": "system-implementation",
                "record_type": "user",
                "event_msg": f"Unknown issue: Failed to create user (ERROR: {str(e)})",
            }
        )


if __name__ == "__main__":
    # If data is incomplete This fails w/ 500 error ( which means the json string being received by the server is either malformed or missing something
    __app = Application()
    __api = Api()

    def basic_test():
        tree = etree.parse("fr_ssp_gold_v1.1.xml")
        root = tree.getroot()
        ARG_SSP_ID = 360

        handle_user(FedrampTraversal(api=__api, root=root, ssp_id=ARG_SSP_ID))

    # Run tests
    basic_test()
