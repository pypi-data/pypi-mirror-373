# flake8: noqa
import json
from typing import List, Optional

from lxml import etree
from lxml.etree import tostring

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.fedramp_traversal import (
    FedrampTraversal,
)
from regscale.models import Property

logger = create_logger()


def parse_and_post_property(
    trv: FedrampTraversal,
    prop_element: etree._Element,
    parent_id: Optional[int] = None,
    parent_module: Optional[str] = None,
):
    try:
        prop_attrib = prop_element.attrib

        # If the parent has a uuid, use it, otherwise use the parent tag
        parent_uuid = prop_element.xpath("parent::*[@uuid]/@uuid")

        if "name" not in prop_attrib or "value" not in prop_attrib:
            trv.log_error(
                {
                    "record_type": "property",
                    "event_msg": f"Failed to create property '{prop_attrib['name']}' with value '{prop_attrib['value']}'",
                }
            )
            return

        xpath = prop_element.getroottree().getpath(prop_element)

        has_parent_module = parent_module is not None and parent_id is not None

        new_property = Property(
            key=parent_uuid or prop_element.getparent().tag,
            value=prop_attrib["value"],
            label=prop_attrib["name"],
            otherAttributes=json.dumps(
                {
                    "xpath": xpath,
                    "element": tostring(prop_element).decode(),
                }
            ),
            # Defaulting to making the parent module security plans.
            parentId=parent_id if has_parent_module else trv.ssp_id,
            parentModule=parent_module if has_parent_module else "securityplans",
        )

        # Run api call to create property
        ret = new_property.create()

        if not ret:
            trv.log_error(
                {
                    "record_type": "property",
                    "event_msg": f"Failed to create property {prop_attrib['name']} with value {prop_attrib['value']}",
                }
            )

        trv.log_info(
            {
                "record_type": "property",
                "event_msg": f"Created property '{prop_attrib['name']}' with value '{prop_attrib['value']}'",
            }
        )
    except Exception as e:
        trv.log_error(
            {
                "record_type": "property",
                "event_msg": f"Unknown issue: Failed to create property '{prop_attrib['name'] if 'name' in prop_attrib else '<UNKNOWN>'}' with value '{prop_attrib['value'] if 'value' in prop_attrib else '<UNKNOWN>'}'",
            }
        )


def post_unmapped_properties(
    trv: FedrampTraversal,
    parent_el: etree._Element,
    mapped_property_names: List[str],
    parent_id: Optional[int] = None,
    parent_module: Optional[str] = None,
):
    """
    Post any unmapped properties on parent_el as properties on the ssp.

    trv: FedrampTraversal # The traversal object.
    parent_el: etree._Element # The element to search for properties in.
    mapped_properties: str # A list of <prop> tags that have already been mapped.
    """

    if not mapped_property_names:
        return

    # Get all <prop> tags in the parent element.
    properties = parent_el.xpath(".//prop")

    # Filter out properties whose names are in mapped_property_names.
    unmapped_properties = [prop for prop in properties if prop.attrib["name"] not in mapped_property_names]

    # Post the unmapped properties.
    for prop in unmapped_properties:
        parse_and_post_property(trv, prop, parent_id=parent_id, parent_module=parent_module)


if __name__ == "__main__":
    app = Application()
    api = Api()
    # This is just an example SSP,
    # the real SSP should be created before this in some pipeline.
    ARG_SSP_ID = 360

    def test_parse_and_post_property():
        # Mock-up XML data for demonstration
        xml_data = """
        <root>
            <system-security-plan uuid="8c000726-ba93-480d-a221-8cb60df10c24">
                <metadata>
                    <prop name="marking" value="Controlled Unclassified Information"/>
                </metadata>
            </system-security-plan>
        </root>
        """

        root = etree.fromstring(xml_data)

        trv = FedrampTraversal(api=api, root=root, ssp_id=ARG_SSP_ID)

        # Find all <prop> elements in the document tree
        for prop_element in root.xpath("//prop"):
            parse_and_post_property(trv, prop_element)

        assert trv.infos[0]["event"] == "Created property 'marking' with value 'Controlled Unclassified Information'"

        return True

    def test_bad_property():
        xml_data = """
        <root>
            <system-security-plan uuid="8c000726-ba93-480d-a221-8cb60df10c24">
                <metadata>
                    <prop name="marking" novalue="Controlled Unclassified Information"/>
                    <prop name="marking" notvalue="Controlled Unclassified Information"/>
                </metadata>
            </system-security-plan>
        </root>
        """
        root = etree.fromstring(xml_data)
        trv = FedrampTraversal(api=api, root=root, ssp_id=ARG_SSP_ID)

        # Find all <prop> elements in the document tree
        for prop_element in root.xpath("//prop"):
            parse_and_post_property(trv, prop_element)

        assert trv.errors[0]["event"] == "Unknown issue: Failed to create property 'marking' with value '<UNKNOWN>'"

        return True

    def test_all_unmapped():
        xml_data = """
        <root>
            <system-security-plan uuid="8c000726-ba93-480d-a221-8cb60df10c24">
                <foo>
                    <prop name="marking" novalue="marking-value"/>
                    <prop name="another" value="another-value"/>
                    <prop name="yet-another" value="yet-another-value"/>
                </foo>
            </system-security-plan>
        </root>
        """
        root = etree.fromstring(xml_data)
        trv = FedrampTraversal(api=api, root=root, ssp_id=ARG_SSP_ID)

        # IN A REAL SITUATION, WE'D HANDLE MARKING HERE.

        # Get the <foo> element (should only be one) and
        # Post all properties that we didn't handle -- in this case,
        # we pretend we handled 'marking', so we post 'another' and 'yet-another'.
        for prop_element in root.xpath("//foo"):
            post_unmapped_properties(trv, prop_element, ["marking"])

        assert trv.infos[0]["event"] == "Created property 'another' with value 'another-value'"
        assert trv.infos[1]["event"] == "Created property 'yet-another' with value 'yet-another-value'"

        return True

    # Run tests.
    test_parse_and_post_property()
    test_bad_property()
    test_all_unmapped()

    print("📝 NOTE: Some errors above were expected.")
    print("✅ All tests passed!")
