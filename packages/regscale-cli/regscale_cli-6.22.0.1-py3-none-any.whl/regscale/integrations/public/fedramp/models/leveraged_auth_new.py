from typing import List

from lxml import etree

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.core.app.utils.XMLIR import XMLIR, XMLIRTraversal
from regscale.models.regscale_models.leveraged_authorization import (
    LeveragedAuthorization,
)


# Example XML for Leveraged Authorization
# <leveraged-authorization uuid="uuid-value" >
#     <title>Name of Underlying System</title>
#     <prop
#         name="leveraged-system-identifier"ns="https://fedramp.gov/ns/oscal"
#         value="Package_ID value"
#     />
#     <link href="//path/to/leveraged_system_legacy_crm.xslt" />
#     <link href="//path/to/leveraged_system_responsibility_and_inheritance.xml" />
#     <party-uuid>uuid-of-leveraged-system-poc</party-uuid>
#     <date-authorized>2015-01-01</date-authorized>
# </leveraged-authorization>


class LeveragedAuthIR(XMLIR):
    @XMLIR.from_el(".")
    def uuid(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The uuid of the leveraged authorization"""
        return vlist[0].get("uuid") if vlist else None

    @XMLIR.from_el(".//oscal:title")
    def title(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:prop[@name='leveraged-system-identifier']")
    def leveraged_system_identifier(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].get("value") if v else None

    @XMLIR.from_el(".//oscal:link")
    def links(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        return [{"href": link.get("href")} for link in vlist] if vlist else None

    @XMLIR.from_el(".//oscal:party-uuid")
    def party_uuid(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:date-authorized")
    def date_authorized(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        return vlist[0].text if vlist else None


def parse_leveraged_auth_new(trv: FedrampTraversal):
    root = trv.root
    api = trv.api

    # Get all leveraged authorizations
    # <system-implementation><leveraged-authorization>

    # Extract leveraged_auth nodes
    leveraged_auths = root.xpath(
        ".//oscal:system-implementation/oscal:leveraged-authorization",
        namespaces=trv.namespaces,
    )

    if len(leveraged_auths) == 0:
        trv.log_info(
            {
                "model_layer": "system-implementation",
                "record_type": "leveraged-authorization",
                "event_msg": "No Leveraged Authorizations detected.",
            }
        )

    for i, elem in enumerate(leveraged_auths):
        try:
            # Part 1: Extract the IR from the XML
            parsed = LeveragedAuthIR().parse(
                XMLIRTraversal(xpathToThis="...", root=trv.root, namespaces=trv.namespaces, el=elem)
            )

            # Leave this for later debugging.
            # print("parsed IR", json.dumps(parsed, indent=2))

            # IR object:
            # {
            #     # TODO: is this fedrampId?
            #     "uuid": "087da60c-3838-469f-a76c-b547800bfa7d",
            #     "title": "GovCloud",
            #     "leveraged_system_identifier": "Package_ID value",
            #     "links": [
            #         {
            #         "href": "https://dev.regscale.io/securityplans/form/360"
            #         }
            #     ],
            #     "party_uuid": "8d8d5468-74f8-499d-976c-bca671e19b14",
            #     "date_authorized": "2022-03-09"
            # }

            def safe_list_get(data_list, idx, default_value):
                try:
                    return data_list[idx]
                except IndexError:
                    return default_value

            links = parsed.get("links", [])
            # TODO-FUTURE: these are only assigned by their position in the list, which is not ideal.
            # Ideally, fedramp would have a specific TAG for each type of link...
            # But this is infeasible, because they don't seem to care?
            security_plan_link = safe_list_get(links, 0, "")
            crm_link = safe_list_get(links, 1, "")
            responsibility_and_inheritance_link = safe_list_get(links, 2, "")
            # Part 2: Send the IR to the API
            api_obj = LeveragedAuthorization(
                title=parsed.get("title"),
                fedrampId=parsed.get("uuid"),
                securityPlanId=trv.ssp_id,
                dateAuthorized=parsed.get("date_authorized"),
                securityPlanLink=(security_plan_link["href"] if "href" in security_plan_link else security_plan_link),
                crmLink=crm_link["href"] if "href" in crm_link else crm_link,
                responsibilityAndInheritanceLink=(
                    responsibility_and_inheritance_link["href"]
                    if "href" in responsibility_and_inheritance_link
                    else responsibility_and_inheritance_link
                ),
                # TODO-FUTURE: We will soon want to set this based by getting the
                # ID of the regscale user corresponding to the `party_uuid`
                ownerId=api.app.config["userId"],
                createdById="",
                lastUpdatedById="",
            )
            api_obj.insert_leveraged_authorizations(app=api.app, leveraged_auth=api_obj)

            trv.log_info(
                {
                    "model_layer": "system-implementation",
                    "record_type": "leveraged-authorization",
                    "event_msg": f"Leveraged Authorization '{parsed.get('title') if parsed.get('title') else '<UNKNKOWN_TITLE>'}' parsed successfully.",
                }
            )

        except Exception as e:
            trv.log_error(
                {
                    "model_layer": "system-implementation",
                    "record_type": "leveraged-authorization",
                    "event_msg": f"Failed to parse Leveraged Authorization ({str(e)})",
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
        ns = {"oscal": "http://csrc.nist.gov/ns/oscal/1.0"}

        parse_leveraged_auth_new(FedrampTraversal(api=__api, root=root, ssp_id=ARG_SSP_ID, namespaces=ns))

    # Run tests
    basic_test()
