"""Provide base models for values in the FedRAMP SSP."""

from typing import Callable, List, Optional, Tuple, Type, Union

from lxml import etree
from pydantic import BaseModel

from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.xml_utils import extract_markup_content

logger = create_logger()


class SSPField(BaseModel):
    value: str
    xpath: str
    type_: Type = str
    namespace: Optional[dict] = None
    callable: Optional[Callable] = None

    def parse_from_element(
        self,
        element: etree._Element,
    ) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        """Parse an SSPField from an XML Element

        :param etree._Element element: The XML Element to parse
        :return: A tuple of the field name and value
        :rtype: Union[Tuple[str, str], List[Tuple[str, str]]]
        """
        result_list = element.xpath(self.xpath, namespaces=self.namespace)
        output = []

        def _helper(result):
            if self.callable and callable(self.callable):
                return self.value, self.type_(self.callable(result))
            return self.value, self.type_(result)

        if len(result_list) == 0:
            logger.warning(f"No results found for {self.value} in {element.tag}")
        if result_list and len(result_list) > 0:
            output = [_helper(result) for result in result_list]
        try:
            return output[0][1] if len(result_list) == 1 and output and len(output[0]) > 1 else output
        except IndexError:
            return output


UUID = SSPField(value="uuid", xpath="@uuid")
Link = SSPField(value="link", xpath="link/@href")
Title = SSPField(value="title", xpath="title/text()")
PartyUUID = SSPField(
    value="party_uuid",
    xpath="party-uuid/text()",
    namespace={"oscal": "http://csrc.nist.gov/ns/oscal/1.0"},
)
DateAuthorized = SSPField(
    value="date_authorized",
    xpath="date-authorized/text()",
    namespace={"oscal": "http://csrc.nist.gov/ns/oscal/1.0"},
)
Remarks = SSPField(value="remarks", xpath="remarks", callable=extract_markup_content)
Description = SSPField(value="description", xpath="description", callable=extract_markup_content)
RoleId = SSPField(value="role-id", xpath="role-id/text()")
PropName = SSPField(value="prop-name", xpath="prop/@name")
PropValue = SSPField(value="prop-value", xpath="prop/@value")
UserUUID = SSPField(value="user-uuid", xpath="user/@uuid")
FunctionPerformed = SSPField(value="function-performed", xpath="function-performed/text()")


if __name__ == "__main__":
    from regscale.models.regscale_models import (
        LeveragedAuthorization,
    )

    xml_string = """<leveraged-authorization uuid="5a9c98ab-8e5e-433d-a7bd-515c07cd1497">
       <title>AWS GovCloud</title>
       <prop ns="https://fedramp.gov/ns/oscal" name="leveraged-system-identifier" value="F1603047866"/>
       <link href="//path/to/leveraged_system_ssp.xml"/>
       <link href="//path/to/leveraged_system_legacy_crm.xslt"/>
       <link href="//path/to/leveraged_system_responsibility_and_inheritance.xml"/>
       <party-uuid>f0bc13a4-3303-47dd-80d3-380e159c8362</party-uuid>
       <date-authorized>2015-01-01</date-authorized>
       <remarks>
       <h1>Remarks</h1>
          <p>The leveraged-authorizaton assembly is supposed to have a required uuid flag instead
             of an optional id flag. This will be fixed in the syntax shortly.</p>
          <p>Use one leveraged-authorization assembly for each underlying system. (In the legacy
             world, these may be general support systems.</p>
          <p>The link fields are optional, but preferred where known. Often, a leveraging system's
             SSP author will not have access to the leveraged system's SSP, but should have access
             to the leveraged system's CRM.</p>
       </remarks>
       <description>
          <p>The description of the object contains the remarks.</p>
          <h2>Services Used</h2>
          <p>Services used by the leveraged system:</p>
          <ul>
                <li>EC2</li>
          </ul>
       </description>
    </leveraged-authorization>
    """
    root = etree.fromstring(xml_string)
    uuid = UUID.parse_from_element(root)
    print(uuid)
    date_authorized = DateAuthorized.parse_from_element(root)
    print(date_authorized)
    party_uuid = PartyUUID.parse_from_element(root)
    print(party_uuid)
    links = Link.parse_from_element(root)
    print(links)
    title = Title.parse_from_element(root)
    print(title)
    remarks = Remarks.parse_from_element(root)
    print(remarks)
    description = Description.parse_from_element(root)
    print(description)
    from regscale.core.app.application import Application
    from regscale.core.app.utils.app_utils import get_current_datetime

    app = Application()
    leveraged_authorizations = LeveragedAuthorization(
        uuid=uuid[1],
        title=title[1],
        fedrampId=None,
        ownerId=party_uuid[1],
        securityPlanId=1,
        dateAuthorized=date_authorized[1],
        description=remarks[1],
        servicesUsed=None,
        securityPlanLink=links[0][1],
        crmLink=links[1][1],
        responsibilityAndInheritanceLink=links[2][1],
        createdById=app.config["userId"],
        dateCreated=get_current_datetime(dt_format="%Y-%m-%dT%H:%M:%S.%fZ"),
        lastUpdatedById=app.config["userId"],
        dateLastUpdated=get_current_datetime(dt_format="%Y-%m-%dT%H:%M:%S.%fZ"),
        tenantsId=None,
    )
    print(leveraged_authorizations)
