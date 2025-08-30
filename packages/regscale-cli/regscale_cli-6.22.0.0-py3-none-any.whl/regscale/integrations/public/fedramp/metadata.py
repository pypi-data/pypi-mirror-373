# flake8: noqa
import json
from typing import List

from lxml import etree

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.XMLIR import XMLIR, XMLIRTraversal
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.integrations.public.fedramp.xml_utils import extract_markup_content
from regscale.models.regscale_models import StakeHolder, SystemRole, SystemRoleExternalAssignment
from regscale.models.regscale_models.data_center import DataCenter
from regscale.models.regscale_models.facility import Facility

logger = create_logger()


class MetadataRoleIR(XMLIR):
    @XMLIR.from_el(".")
    def id(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's role"""
        return v[0].get("id")

    @XMLIR.from_el(".//oscal:title")
    def title(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".//oscal:desc")
    def description(self, v: List[etree._Element], traversal: XMLIRTraversal):
        text_inside = extract_markup_content(v[0]) if v else None

        return text_inside


class MetadataLocationAddressIR(XMLIR):
    @XMLIR.from_el(".//oscal:addr-line")
    def addr_line(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".//oscal:city")
    def city(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".//oscal:state")
    def state(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".//oscal:postal-code")
    def postal_code(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".")
    def type(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].get("type") if v else None


class MetadataLocationIR(XMLIR):
    @XMLIR.from_el(".")
    def uuid(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].get("uuid") if v else None

    @XMLIR.from_el(".//oscal:title")
    def title(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return v[0].text if v else None

    @XMLIR.from_el(".//oscal:address")
    def address(self, v: List[etree._Element], traversal: XMLIRTraversal):
        return MetadataLocationAddressIR().parse(
            XMLIRTraversal(
                namespaces=traversal.namespaces,
                root=traversal.root,
                el=v[0],
                xpathToThis="...",
            )
        )

    # Pass on remarks
    @XMLIR.from_el(".//oscal:remarks")
    def remarks(self, v: List[etree._Element], traversal: XMLIRTraversal):
        text_inside = extract_markup_content(v[0]) if v else None

        return text_inside


# TODO
"""
----
EXAMPLE 1:
----

<party uuid="6b286b5d-8f07-4fa7-8847-1dd0d88f73fb" type="organization">
    <name>Cloud Service Provider (CSP) Name</name>
    <short-name>CSP Acronym/Short Name</short-name>
    <link href="#31a46c4f-2959-4287-bc1c-67297d7da60b" rel="logo"/>
    <location-uuid>27b78960-59ef-4619-82b0-ae20b9c709ac</location-uuid>
    <remarks>
    <p>Replace sample CSP information.</p>
    <p>CSP informaton must be present and associated with the "cloud-service-provider" role
        via <code>responsible-party</code>.</p>
    </remarks>
</party>

----
EXAMPLE 2:
----

<party uuid="77e0e2c8-2560-4fe9-ac78-c3ff4ffc9f6d" type="organization">
         <name>Federal Risk and Authorization Management Program: Program Management Office</name>
         <short-name>FedRAMP PMO</short-name>
         <link href="https://fedramp.gov" rel="homepage"/>
         <link href="#a2381e87-3d04-4108-a30b-b4d2f36d001f" rel="logo"/>
         <link href="#985475ee-d4d6-4581-8fdf-d84d3d8caa48" rel="reference"/>
         <link href="#1a23a771-d481-4594-9a1a-71d584fa4123" rel="reference"/>
         <email-address>info@fedramp.gov</email-address>
         <address type="work">
            <addr-line>1800 F St. NW</addr-line>
            <city>Washington</city>
            <state>DC</state>
            <postal-code>20006</postal-code>
            <country>US</country>
         </address>
         <remarks>
            <p>This party entry must be present in a FedRAMP SSP.</p>
            <p>The uuid may be different; however, the uuid must be associated with the
               "fedramp-pmo" role in the responsible-party assemblies.</p>
         </remarks>
      </party>

"""


class MetadataOrgPartyIR(XMLIR):
    @XMLIR.from_el(".")
    def uuid(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's uuid"""
        return v[0].get("uuid") if v else None

    @XMLIR.from_el(".")
    def type(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's type"""
        return v[0].get("type") if v else None

    @XMLIR.from_el(".//oscal:link")
    def links(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's links"""
        return [
            {
                "href": v.get("href"),
                "rel": v.get("rel"),
            }
            for v in vlist
        ]

    @XMLIR.from_el(".//oscal:location-uuid")
    def location_uuids(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's location uuid"""
        return [v.text for v in vlist]

    @XMLIR.from_el(".//oscal:name")
    def name(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's name"""
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:short-name")
    def short_name(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's short name"""
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:email-address")
    def email_address(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's email address"""
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:remarks")
    def remarks(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The text of the remark"""
        text_inside = extract_markup_content(vlist[0]) if vlist else None

        return text_inside


"""
<party uuid="uuid-of-person-1" type="person">
    <name>[SAMPLE]Person Name 1</name>
    <prop name="job-title" value="Individual's Title"/>
    NIST Allowed Value
    Required role ID:
     system-owner
    <prop name="mail-stop" value="A-1"/> 
    <email-address>name@example.com</email-address> 
    <telephone-number>202-000-0000</telephone-number> 
    <location-uuid>uuid-of-hq-location</location-uuid> 
    <member-of-organization>uuid-of-csp</member-of-organization>
</party>

"""


class MetadataPersonPartyIR(XMLIR):
    @XMLIR.from_el(".")
    def uuid(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's uuid"""
        return v[0].get("uuid") if v else None

    @XMLIR.from_el(".")
    def type(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's type"""
        return v[0].get("type") if v else None

    @XMLIR.from_el(".//oscal:location-uuid")
    def location_uuids(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's location uuid"""
        return [v.text for v in vlist]

    @XMLIR.from_el(".//oscal:member-of-organization")
    def member_of_organization_uuids(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's location uuid"""
        return [v.text for v in vlist]

    @XMLIR.from_el(".//oscal:name")
    def name(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's name"""
        return vlist[0].text if vlist else None

    @XMLIR.from_el('.//oscal:prop[@name="job-title"]')
    def job_title(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's role"""
        return vlist[0].get("value") if vlist else None

    @XMLIR.from_el('.//oscal:prop[@name="mail-stop"]')
    def mail_stop(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's role"""
        return vlist[0].get("value") if vlist else None

    @XMLIR.from_el(".//oscal:email-address")
    def email_address(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's email address"""
        return vlist[0].text if vlist else None

    @XMLIR.from_el(".//oscal:telephone-number")
    def telephone_number(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's telephone number"""
        return vlist[0].text if vlist else None


"""
<responsible-party role-id="system-poc-management">
     <party-uuid>0cec09d9-20c6-470b-9ffc-85763375880b</party-uuid>
     <remarks>
        <p>Exactly one</p>
     </remarks>
  </responsible-party>
"""


class MetadataResponsiblePartyIR(XMLIR):
    @XMLIR.from_el(".")
    def role_id(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's role id"""
        return v[0].get("role-id") if v else None

    @XMLIR.from_el(".//oscal:party-uuid")
    def party_uuids(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's party uuid"""
        return [v.text for v in vlist]

    @XMLIR.from_el(".//oscal:remarks")
    def remarks(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The text of the remark"""
        text_inside = extract_markup_content(vlist[0]) if vlist else None

        return text_inside


class MetadataMappingIR(XMLIR):
    # ./ implies current element
    @XMLIR.from_el(".//oscal:role")
    def roles(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's role"""
        return [
            MetadataRoleIR().parse(
                XMLIRTraversal(
                    namespaces=traversal.namespaces,
                    root=traversal.root,
                    el=v,
                    xpathToThis="...",
                )
            )
            for v in vlist
        ]

    @XMLIR.from_el(".//oscal:location")
    def locations(self, v: List[etree._Element], traversal: XMLIRTraversal):
        """The user's location"""
        return [
            MetadataLocationIR().parse(
                XMLIRTraversal(
                    namespaces=traversal.namespaces,
                    root=traversal.root,
                    el=v,
                    xpathToThis="...",
                )
            )
            for v in v
        ]

    @XMLIR.from_el(".//oscal:party")
    def parties(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's party"""
        return [
            (
                MetadataOrgPartyIR().parse(
                    XMLIRTraversal(
                        namespaces=traversal.namespaces,
                        root=traversal.root,
                        el=v,
                        xpathToThis="...",
                    )
                )
                if v.get("type") == "organization"
                else MetadataPersonPartyIR().parse(
                    XMLIRTraversal(
                        namespaces=traversal.namespaces,
                        root=traversal.root,
                        el=v,
                        xpathToThis="...",
                    )
                )
            )
            for v in vlist
        ]

    @XMLIR.from_el(".//oscal:responsible-party")
    def responsible_parties(self, vlist: List[etree._Element], traversal: XMLIRTraversal):
        """The user's responsible party"""
        return [
            MetadataResponsiblePartyIR().parse(
                XMLIRTraversal(
                    namespaces=traversal.namespaces,
                    root=traversal.root,
                    el=v,
                    xpathToThis="...",
                )
            )
            for v in vlist
        ]


def parse_metadata(trv: FedrampTraversal, app: Application) -> None:
    """This function parses role, location, and party information from metadata. This

    :param FedrampTraversal trv: The traversal object
    :param Application app: The RegScale CLI application object
    :rtype: None
    """
    api = trv.api
    root = trv.root
    namespaces = trv.namespaces

    # Extract user nodes
    metadatas = root.xpath(".//oscal:metadata", namespaces=namespaces)

    if len(metadatas) == 0:
        trv.log_error(
            {
                "model_layer": "system-implementation",
                "record_type": "metadata",
                "event_msg": "No metadata detected.",
            }
        )

    elif len(metadatas) > 1:
        trv.log_error(
            {
                "model_layer": "system-implementation",
                "record_type": "metadata",
                "event_msg": "Multiple metadatas detected.",
            }
        )

    else:
        # 1. Get IR
        metadata = metadatas[0]
        metadata_mapping = MetadataMappingIR().parse(
            XMLIRTraversal(
                xpathToThis=".//oscal:metadata",
                el=metadata,
                root=root,
                namespaces=namespaces,
            )
        )

        #################################
        # 2. Post to API Endpoints
        # roles: list of roles, id, title, description
        # locations: list of locations, uuid, title, address
        # parties: list of parties, uuid, type, name, short-name, links, location-uuids, member-of-organization-uuids, email-address, remarks
        # responsible-parties: list of responsible-parties, role-id, party-uuids, remarks
        #################################
        # 2.1 roles
        roles = metadata_mapping["roles"]
        for role in roles:
            logger.debug(f"role: {role=}")
            try:
                system_role = SystemRole(
                    id=0,
                    fedrampRoleId=role["id"],
                    roleName=role["title"],
                    roleType="Internal",
                    accessLevel="Non-Privileged",
                    sensitivityLevel="Not Applicable",
                    privilegeDescription=(
                        role["description"]
                        if role["description"]
                        else "Not Found -imported by CLI-defaulting to Non-Privileged"
                    ),
                    functions="Not Found",
                    securityPlanId=trv.ssp_id,
                    isPublic=True,
                    assignedUserId=app.config["userId"],
                )

                server_res = system_role.insert_systemrole(api.app)
                # what do we want to do with the responses?

                if (server_res is None) or (not server_res):
                    trv.log_error(
                        {
                            "model_layer": "metadata",
                            "record_type": "role",
                            "event_msg": f"Failed to create role '{role['title'] if 'title' in role else '<UNKNOWN>'}' with role id '{role['id'] if 'id' in role else '<UNKNOWN>'}'",
                        }
                    )
                else:
                    trv.log_info(
                        {
                            "model_layer": "metadata",
                            "record_type": "role",
                            "event_msg": f"Created role '{role['title']}' with role id '{role['id']}'",
                        }
                    )

            except Exception as e:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "role",
                        "event_msg": f"Failed to create role '{role['title'] if 'title' in role else '<UNKNOWN>'}' with role id '{role['id'] if 'id' in role else '<UNKNOWN>'}' (ERROR: {str(e)})",
                    }
                )
        # 2.2 locations
        locations = metadata_mapping["locations"]
        for location in locations:
            """
            Facility object (Regscale Object)
            {
                "id": 0,
                "name": "string",
                "description": "string",
                "address": "string",
                "city": "string",
                "state": "string",
                "zipCode": "string",
                "status": "string",
                "latitude": 0,
                "longitude": 0,
                "createdBy": "string",
                "createdById": "string",
                "dateCreated": "2023-08-30T04:02:03.937Z",
                "lastUpdatedBy": "string",
                "lastUpdatedById": "string",
                "dateLastUpdated": "2023-08-30T04:02:03.937Z"
            }
            """
            try:
                facility = Facility(
                    name=location.get("name", ""),
                    description=location.get("description", ""),
                    address=location.get("address", {}).get("addr_line", ""),
                    city=location.get("address", {}).get("city", ""),
                    state=location.get("address", {}).get("state", ""),
                    zipCode=location.get("address", {}).get("postal_code", ""),
                    status=location.get("status", ""),
                    latitude=location.get("address", {}).get("latitude", 0),
                    longitude=location.get("address", {}).get("longitude", 0),
                    createdById=api.config["userId"],
                )
                facility_res = facility.post(api.app)
                trv.log_info(
                    {
                        "model_layer": "metadata",
                        "record_type": "Location",
                        "event_msg": f"Created facility '{facility_res['id']}' with description '{facility_res['description']}'",
                    }
                )
            except Exception as e:
                trv.log_error(
                    {
                        "missing_element": location.get("name", ""),
                        "model_layer": "metadata",
                        "record_type": "Location",
                        "event_msg": f"Failed to create facility '{location['title'] if 'title' in location else '<UNKNOWN>'}'"
                        f" (ERROR: {str(e)})",
                    }
                )
            if facility_res:
                try:
                    data_center = DataCenter(
                        id=0,
                        # uuid=party.get('uuid', ''),  # TODO - this should go to FedRAMP ID once exists
                        facilityId=facility_res.get("id", ""),
                        parentId=trv.ssp_id,
                        parentModule="securityplans",
                        facility=facility_res.get("name", ""),
                    )
                    logger.debug(f"{data_center=}")
                    data_center_res = data_center.post(api.app)
                    logger.debug(f"{data_center_res=}")

                    trv.log_info(
                        {
                            "model_layer": "metadata",
                            "record_type": "Location",
                            "event_msg": f"Created DataCenter '{data_center_res['id']}'",
                        }
                    )
                except Exception as e:
                    trv.log_error(
                        {
                            "model_layer": "metadata",
                            "record_type": "Location",
                            "event_msg": f"Failed to create DataCenter: (ERROR: {str(e)})",
                        }
                    )
            else:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "Location",
                        "event_msg": f"Failed to create DataCenter: (ERROR: {str(e)})",
                    }
                )

        # 2.3 parties
        parties = metadata_mapping["parties"]
        for party in parties:
            """
            StakeHolders (Regscale Object)
            {
                "id": 0,
                "type": "string",
                "name": "string",
                "shortname": "string",
                "title": "string",
                "phone": "string",
                "email": "string",
                "address": "string",
                "otherID": "string",
                "notes": "string",
                "parentId": 0,
                "parentModule": "string"
            }
            """
            try:
                stakeholders = StakeHolder(
                    id=0,
                    type=party.get("type", ""),
                    name=party.get("name", ""),
                    shortname=party.get("short_name", ""),
                    title=party.get("title", ""),
                    phone=party.get("phone", ""),
                    email=party.get("email_address", ""),
                    address=party.get("address", ""),
                    # otherID is fedrampId in this case.
                    otherID=party.get("uuid", ""),
                    notes=party.get("remarks", ""),
                    parentId=trv.ssp_id,
                    parentModule="securityplans",
                )
                # FIXME how do we handle links and location_uuids?
                stakeholders_res = stakeholders.post(api.app)
                trv.log_info(
                    {
                        "model_layer": "metadata",
                        "record_type": "party",
                        "event_msg": f"Created stakeholder '{stakeholders_res['id']}' with name '{stakeholders_res['name']} and otherID: '{stakeholders_res['otherID']}'",
                    }
                )
            except Exception as e:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "party",
                        "event_msg": f"Failed to create party: {party.get('shortname', '')} (ERROR: {str(e)})",
                    }
                )

        #########################################################################
        # 2.4 responsible-parties
        responsible_parties = metadata_mapping["responsible_parties"]

        # For debugging.
        logger.debug(f"stakeholders: {stakeholders=}")

        for responsible_party in responsible_parties:
            party_uuid = (
                responsible_party["party_uuids"][0]
                if "party_uuids" in responsible_party and len(responsible_party["party_uuids"]) > 0
                else None
            )

            if (party_uuid is None) or (len(party_uuid) == 0):
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Failed to create responsible-party: '{responsible_party.get('role_id', '')}', could not find correspnding party-uuid",
                    }
                )
                continue

            # 1. Stakeholder
            resp_party_stakeholder_id = trv.fedramp_party_to_regscale_stakeholder_id(party_uuid)

            if resp_party_stakeholder_id is None:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Failed to create responsible-party: '{responsible_party.get('role_id', '')}', could not find corresponding stakeholder in Regscale (did you forget to create a corresponding <party> tag in metadata?).",
                    }
                )
                continue

            # TODO 2. get SystemRole
            fedramp_role_id = responsible_party.get("role_id", "")

            if fedramp_role_id is None:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Failed to create responsible-party: '{responsible_party.get('role_id', '')}', could not find correspnding role_id in metadata (did you forget to create a corresponding <role> tag in metadata?).",
                    }
                )
                continue

            system_role_id = trv.fedramp_role_id_to_regscale_system_role_id(fedramp_role_id=fedramp_role_id)

            # For debugging only.
            logger.debug("system_role_id: ", system_role_id)

            if system_role_id is None:
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Failed to create responsible-party: '{responsible_party.get('role_id', '')}', could not find corresponding system role in Regscale (did you forget to create a corresponding <role> tag in metadata?).",
                    }
                )
                continue

            # 3. Create SystemRoleExternalAssignment, joining SystemRole & Stakeholder
            system_role_resp = SystemRoleExternalAssignment(
                roleId=system_role_id,
                stakeholderId=resp_party_stakeholder_id,
            ).post(api.app)

            # For debugging only.
            logger.debug("system_role_resp: ", system_role_resp)

            if (system_role_resp is None) or (not system_role_resp):
                trv.log_error(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Failed to create responsible-party: '{responsible_party.get('role_id', '')}' with stakeholder id '{resp_party_stakeholder_id}' and system role id '{system_role_id}'",
                    }
                )

            else:
                trv.log_info(
                    {
                        "model_layer": "metadata",
                        "record_type": "responsible-party",
                        "event_msg": f"Created responsible-party: '{responsible_party.get('role_id', '')}' with stakeholder id '{resp_party_stakeholder_id}' and system role id '{system_role_id}'",
                    }
                )
