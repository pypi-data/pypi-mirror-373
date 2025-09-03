"""
System Characteristics are a Model Layer in the OSCAL SSP implementation model. The
model is documented at https://pages.nist.gov/OSCAL/concepts/layer/implementation/ssp/
Note that the RegScale SSP Data model collapses several NIST OSCAL model layers together
including Metadata, System Characteristics, and System Implementation.
"""

import json
from json import JSONDecodeError
from typing import List, Optional, Union

from lxml.etree import Element
from pydantic import ValidationError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.reporting import log_error, log_event
from regscale.integrations.public.fedramp.resources import parse_backmatter
from regscale.integrations.public.fedramp.xml_utils import update_ssp

# flake8: noqa: C901
from regscale.models import SecurityPlan

logger = create_logger()
SYSTEM_CHARS = "System Characteristics"
SYSTEM_INFO = "System Information"

CAT_MAPPING = [
    ("fips-199-low", "Low"),
    ("fips-199-moderate", "Moderate"),
    ("fips-199-high", "High"),
]

LEVEL_MAPPING = [
    ("1", "Low"),
    ("2", "Moderate"),
    ("3", "High"),
]

FR_AUTH_MAPPING = [
    ("fedramp-jab", "Joint Authorization Board (JAB)"),
    ("fedramp-agency", "Agency Authorization"),
    ("fedramp-li-saas", "Low Impact SaaS"),
]

STATUS_MAPPING = [
    ("operational", "Operational"),
    ("under-development", "Under Development"),
    ("under-major-modification", "Undergoing a Major Modification"),
]


def get_compliance_settings_id() -> int:
    # TODO: Move to REG-13149
    """
    Return the Compliance Settings ID for FedRAMP

    :return: Compliance Setting ID
    :rtype: int
    """
    from regscale.models.regscale_models.compliance_settings import ComplianceSettings

    try:
        fedramp_comp = next(
            comp.id for comp in ComplianceSettings.get_by_current_tenant() if comp.title == "FedRAMP Compliance Setting"
        )
    except (StopIteration, JSONDecodeError):
        # Handle the case where the Compliance Setting ID is not found or the RegScale version is not compatible
        logger.warning("Unable to find Compliance Setting ID, defaulting to 1.")
        fedramp_comp = 1
    return fedramp_comp


def parse_minimum_ssp(
    api: Api,
    root: Element,
    events_list: Optional[list] = None,
    new_ssp: Optional[dict] = None,
    ns: Optional[dict] = None,
) -> Union[str, int]:
    """The objective of this function is to parse the elements needed for an initial POST to create and return a new
    SSP ID. The SSP ID can then be later used to update the SSP with additional information in a PUT operation, or to
    provide the necessary ParentID for database records that require the SSP ID as a foreign key.

    :param Api api: RegScale API object
    :param Element root: lxml root Element from SSP
    :param Optional[list] events_list: list to be populated with parsed data
    :param Optional[dict] new_ssp: dict to be populated with parsed data
    :param Optional[dict] ns: namespace dict
    :return: SSP ID
    :rtype: Union[str, int]
    """
    app = Application()
    properties_list = []  # track any properties collected during this time
    fedrampId = root.xpath(
        '/*/ns1:system-characteristics/ns1:system-id[@identifier-type="https://fedramp.gov"]',
        namespaces=ns,
    )
    if len(fedrampId) == 0:
        events_list.append(
            log_error(
                record_type="FedRAMP ID",
                missing_element="FedRAMP ID",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["fedrampId"] = fedrampId[0].text
        events_list.append(
            log_event(
                record_type="FedRAMP ID",
                model_layer=SYSTEM_CHARS,
                event_msg=f'Found FedRAMP-assigned identifier: {new_ssp["fedrampId"]}',
            )
        )
    #
    xpath_query = "/*/ns1:system-characteristics/ns1:system-id"
    additional_identifiers = root.xpath(xpath_query, namespaces=ns)
    for additional_identifier in additional_identifiers:
        try:
            if additional_identifier.attrib["identifier-type"] != "https://fedramp.gov":
                property_ = {
                    "key": "identifier-type=" + additional_identifier.attrib["identifier-type"],
                    "value": additional_identifier.text,
                    "label": "Other System ID",
                    "otherAttributes": xpath_query.replace("ns1:", "{http://csrc.nist.gov/ns/oscal/1.0}"),
                }
                properties_list.append(property_)
                events_list.append(
                    log_event(
                        record_type="System Identifier",
                        model_layer=SYSTEM_CHARS,
                        event_msg=f'Additional System ID detected & recorded as Property: {property_["value"]}',
                    )
                )
        except Exception as e:
            logger.error(e)
            events_list.append(
                log_error(
                    missing_element=additional_identifier.tag,
                    record_type="Property",
                    model_layer=SYSTEM_CHARS,
                    event_msg=f"Problem importing Additional System ID {additional_identifier.text}",
                )
            )

    #
    other_identifier = root.xpath("/*/ns1:system-characteristics/ns1:system-name-short", namespaces=ns)
    if len(other_identifier) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="System Short Name",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["otherIdentifier"] = other_identifier[0].text
        events_list.append(
            log_event(
                record_type="System Short Name",
                event_msg=f'System Short Name identified as {new_ssp["otherIdentifier"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    description = root.xpath("/*/ns1:system-characteristics/ns1:description", namespaces=ns)
    if len(description) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="System Description",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        # TODO: This needs the text collapsing function that Joshua is working on.
        # new_ssp["description"] = extract_markup_content(description[0])
        new_ssp["description"] = ""
        for p in description[0].findall("ns1:p", namespaces=ns):
            new_ssp["description"] = new_ssp["description"] + p.text + " "
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'System description recorded:  {new_ssp["description"][:30]}... ',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    fedrampAuthorizationType = root.xpath(
        '/*/ns1:system-characteristics/ns1:prop[@name="authorization-type"][@ns="https://fedramp.gov/ns/oscal"]',
        namespaces=ns,
    )
    if len(fedrampAuthorizationType) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="FedRAMP Authorization Type",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["fedrampAuthorizationType"] = apply_mapping(
            FR_AUTH_MAPPING, fedrampAuthorizationType[0].attrib["value"]
        )
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'FedRAMP Authorization Type: {new_ssp["fedrampAuthorizationType"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    authenticationLevel = root.xpath(
        '/*/ns1:system-characteristics/ns1:prop[@name="security-eauth-level"][@class="security-eauth"]',
        namespaces=ns,
    )
    if len(authenticationLevel) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="FedRAMP Authentication Level",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["authenticationLevel"] = apply_mapping(LEVEL_MAPPING, authenticationLevel[0].attrib["value"])
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'FedRAMP Authentication Level: {new_ssp["authenticationLevel"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    identityAssuranceLevel = root.xpath(
        '/*/ns1:system-characteristics/ns1:prop[@name="identity-assurance-level"]/@value',
        namespaces=ns,
    )
    if len(identityAssuranceLevel) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="FedRAMP Identity Assurance Level",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["identityAssuranceLevel"] = apply_mapping(LEVEL_MAPPING, identityAssuranceLevel[0])
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'FedRAMP Identity Assurance Level: {new_ssp["identityAssuranceLevel"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    authenticatorAssuranceLevel = root.xpath(
        '/*/ns1:system-characteristics/ns1:prop[@name="authenticator-assurance-level"]/@value',
        namespaces=ns,
    )
    if len(authenticatorAssuranceLevel) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="FedRAMP Authenticator Assurance Level",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["authenticatorAssuranceLevel"] = apply_mapping(LEVEL_MAPPING, identityAssuranceLevel[0])
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'FedRAMP Authenticator Assurance Level: {new_ssp["authenticatorAssuranceLevel"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    federationAssuranceLevel = root.xpath(
        '/*/ns1:system-characteristics/ns1:prop[@name="federation-assurance-level"]/@value',
        namespaces=ns,
    )
    if len(federationAssuranceLevel) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="FedRAMP Federation Assurance Level",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["federationAssuranceLevel"] = apply_mapping(LEVEL_MAPPING, federationAssuranceLevel[0])
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'FedRAMP Federation Assurance Level: {new_ssp["federationAssuranceLevel"]}',
                model_layer=SYSTEM_CHARS,
            )
        )

    #
    system_name = root.xpath("/*/ns1:system-characteristics/ns1:system-name", namespaces=ns)
    if len(system_name) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="System Name",
                model_layer=SYSTEM_CHARS,
            )
        )
        new_ssp["systemName"] = "Cloud Service Provider System"  # FAILSAFE W/ DUMMY DATA FOR REQUIRED VALUES
    else:
        new_ssp["systemName"] = system_name[0].text
        events_list.append(
            log_event(
                record_type="System Name",
                event_msg=f'System Name identified as {new_ssp["systemName"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    new_ssp["confidentiality"] = "Low"  # default value
    confidentiality = root.xpath(
        "/*/ns1:system-characteristics/ns1:security-impact-level/ns1:security-objective-confidentiality",
        namespaces=ns,
    )
    if len(confidentiality) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="Security Objective (Confidentiality) ",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["confidentiality"] = apply_mapping(CAT_MAPPING, confidentiality[0].text)
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'Recorded System Security Confidentiality: {new_ssp["confidentiality"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    new_ssp["integrity"] = "Low"  # default value
    integrity = root.xpath(
        "/*/ns1:system-characteristics/ns1:security-impact-level/ns1:security-objective-integrity",
        namespaces=ns,
    )
    if len(integrity) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="Security Objective (Integrity) ",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["integrity"] = apply_mapping(CAT_MAPPING, integrity[0].text)
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'Recorded System Security Integrity: {new_ssp["integrity"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    new_ssp["availability"] = "Low"  # default value
    availability = root.xpath(
        "/*/ns1:system-characteristics/ns1:security-impact-level/ns1:security-objective-availability",
        namespaces=ns,
    )
    if len(availability) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="Security Objective (Availability) ",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["availability"] = apply_mapping(CAT_MAPPING, availability[0].text)
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'Recorded System Security Availability: {new_ssp["availability"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    new_ssp["overallCategorization"] = "Low"  # default value
    overall_categorization = root.xpath("/*/ns1:system-characteristics/ns1:security-sensitivity-level", namespaces=ns)
    if len(overall_categorization) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="Security Objective (Overall Categorization) ",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["overallCategorization"] = apply_mapping(CAT_MAPPING, overall_categorization[0].text)
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'Recorded System Security Overall Categorization: {new_ssp["overallCategorization"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
    #
    new_ssp["status"] = "Operational"  # default value
    status = root.xpath("/*/ns1:system-characteristics/ns1:status", namespaces=ns)
    if len(status) == 0:
        events_list.append(
            log_error(
                record_type=SYSTEM_INFO,
                missing_element="System Operating Status",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        new_ssp["status"] = apply_mapping(STATUS_MAPPING, status[0].attrib["state"])
        events_list.append(
            log_event(
                record_type=SYSTEM_INFO,
                event_msg=f'System Operating status detected: {new_ssp["status"]}',
                model_layer=SYSTEM_CHARS,
            )
        )
        status_remarks = root.xpath("/*/ns1:system-characteristics/ns1:status/ns1:remarks", namespaces=ns)
        if len(status_remarks) > 0:
            new_ssp["explanationForNonOperational"] = ""
            for p in status_remarks[0].findall("ns1:p", namespaces=ns):
                new_ssp["explanationForNonOperational"] = new_ssp["explanationForNonOperational"] + p.text + " "
    #
    # CLOUD SERVICE MODELS
    new_ssp["bModelSaaS"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='saas']",
        namespaces=ns,
    )
    if len(new_ssp["bModelSaaS"]) == 0:
        new_ssp["bModelSaaS"] = False
    else:
        new_ssp["bModelSaaS"] = True
    #
    new_ssp["bModelPaaS"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='paas']",
        namespaces=ns,
    )
    if len(new_ssp["bModelPaaS"]) == 0:
        new_ssp["bModelPaaS"] = False
    else:
        new_ssp["bModelPaaS"] = True
    #
    new_ssp["bModelIaaS"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='iaas']",
        namespaces=ns,
    )
    if len(new_ssp["bModelIaaS"]) == 0:
        new_ssp["bModelIaaS"] = False
    else:
        new_ssp["bModelIaaS"] = True
    #
    new_ssp["bModelOther"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='other']",
        namespaces=ns,
    )
    if len(new_ssp["bModelOther"]) == 0:
        new_ssp["bModelOther"] = False
    else:
        new_ssp["bModelOther"] = True
    #
    remarks = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='other']/ns1:remarks",
        namespaces=ns,
    )
    if len(remarks) == 0:
        pass
    else:
        new_ssp["OtherModelRemarks"] = ""
        for p in remarks[0].findall("ns1:p", namespaces=ns):
            new_ssp["OtherModelRemarks"] = new_ssp["OtherModelRemarks"] + p.text + " "

    # CLOUD DEPLOYMENTS

    new_ssp["bDeployPublic"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-deployment-model'][@value='public-cloud']",
        namespaces=ns,
    )
    if len(new_ssp["bDeployPublic"]) == 0:
        new_ssp["bDeployPublic"] = False
    else:
        new_ssp["bDeployPublic"] = True
    #
    new_ssp["bDeployPrivate"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-deployment-model'][@value='private-cloud']",
        namespaces=ns,
    )
    if len(new_ssp["bDeployPrivate"]) == 0:
        new_ssp["bDeployPrivate"] = False
    else:
        new_ssp["bDeployPrivate"] = True
    #
    new_ssp["bDeployGov"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-deployment-model'][@value='government-only-cloud']",
        namespaces=ns,
    )
    if len(new_ssp["bDeployGov"]) == 0:
        new_ssp["bDeployGov"] = False
    else:
        new_ssp["bDeployGov"] = True
    #
    new_ssp["bDeployHybrid"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-deployment-model'][@value='hybrid-cloud']",
        namespaces=ns,
    )
    if len(new_ssp["bDeployHybrid"]) == 0:
        new_ssp["bDeployHybrid"] = False
    else:
        new_ssp["bDeployHybrid"] = True
    #
    new_ssp["bDeployOther"] = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-deployment-model'][@value='other-cloud']",
        namespaces=ns,
    )
    if len(new_ssp["bDeployOther"]) == 0:
        new_ssp["bDeployOther"] = False
    else:
        new_ssp["bDeployOther"] = True
    #
    remarks = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:prop[@name='cloud-service-model'][@value='other']/ns1:remarks",
        namespaces=ns,
    )
    if len(remarks) == 0:
        pass
    else:
        new_ssp["DeployOtherRemarks"] = ""
        for p in remarks[0].findall("ns1:p", namespaces=ns):
            new_ssp["DeployOtherRemarks"] = new_ssp["DeployOtherRemarks"] + p.text + " "
    # TODO: This RegScale value doesn't seem to have a FedRAMP counterpart. Confirm w/ Travis or Dale
    new_ssp["systemType"] = "Major Application"
    new_ssp["systemOwnerId"] = app.config["userId"]
    from regscale.utils.version import RegscaleVersion
    from packaging.version import Version

    regscale_version = RegscaleVersion.get_platform_version()
    if len(regscale_version) >= 10 or Version(regscale_version) >= Version("6.13.0.0"):
        new_ssp["complianceSettingsId"] = get_compliance_settings_id()
    ssp_id = post_SSP(api, new_ssp)
    return ssp_id


def parse_system_characteristics(
    ssp_id: Union[int, str], root: Element, events_list: Optional[list] = None, ns: Optional[dict] = None
):
    """Parse system characteristics from OSCAL SSP XML to RegScale SSP JSON

    :param Union[int, str] ssp_id: The ID of the SSP to be updated
    :param Element root: lxml root Element from SSP
    :param Optional[list] events_list: list to be populated with parsed data, defaults to None
    :param Optional[dict] ns: namespace dict, defaults to None
    """

    ssp_updates = {}  # store any key value pairs to update SSP with

    # Information / Classification Types
    information_types = root.xpath(
        "/*/ns1:system-characteristics/ns1:system-information/ns1:information-type",
        namespaces=ns,
    )
    if len(information_types) == 0:
        events_list.append(
            log_error(
                record_type="Information Types",
                missing_element="At least one Information Type",
                model_layer=SYSTEM_CHARS,
            )
        )
    else:
        parse_classificationType(information_types, ns, events_list, ssp_id)

    # Privacy Impact Assessment
    # TODO: Doesn't seem to be a RegScale counterpart for <prop name="privacy-sensitive" value="yes"/>  - confirm w/ SME
    parse_privacy(root=root, ns=ns, events_list=events_list, ssp_id=ssp_id)

    # SYSTEM DESCRIPTION
    authorizationBoundary = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:authorization-boundary/ns1:description",
        namespaces=ns,
    )
    if len(authorizationBoundary) > 0:
        ssp_updates["authorizationBoundary"] = ""
        for p in authorizationBoundary[0].findall("ns1:p", namespaces=ns):
            if p.text:
                ssp_updates["authorizationBoundary"] = ssp_updates["authorizationBoundary"] + p.text + " "
        events_list.append(
            log_event(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                event_msg="Authorization Boundary recorded.",
            )
        )
    else:
        events_list.append(
            log_error(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                missing_element="Auth. Boundary Description",
            )
        )

    # check if there is back-matter
    if back_matter := root.find(".//ns1:back-matter", namespaces=ns):
        # get the resources
        resources = back_matter.findall(".//ns1:resource", namespaces=ns)
        results = parse_backmatter(
            resource_elem=resources,
            back_matter=back_matter,
            root=root,
            ns=ns,
            ssp_id=ssp_id,
            events_list=events_list,
        )
        event_msg = (
            f"Created {results['linksCreated']} new link(s), created "
            f"{results['referencesCreated']} reference(s), and uploaded "
            f"{results['filesUploaded']} file(s) in RegScale."
        )
        events_list.append(
            log_event(
                record_type="Back Matter",
                event_msg=event_msg,
                model_layer="Back Matter",
            )
        )
    else:
        events_list.append(
            log_error(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                missing_element="back-matter",
            )
        )

    network_architecture = (
        root.xpath(
            "/ns1:system-security-plan/ns1:system-characteristics/ns1:network-architecture/ns1:description",
            namespaces=ns,
        )
        or []
    )

    if len(network_architecture) > 0:
        ssp_updates["networkArchitecture"] = ""
        for p in network_architecture[0].findall("ns1:p", namespaces=ns):
            if p.text:
                ssp_updates["networkArchitecture"] = ssp_updates["networkArchitecture"] + p.text + " "
        events_list.append(
            log_event(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                event_msg="Network Architecture description recorded.",
            )
        )
    else:
        events_list.append(
            log_error(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                missing_element="Network Architecture",
            )
        )
    #
    dataFlow = root.xpath(
        "/ns1:system-security-plan/ns1:system-characteristics/ns1:data-flow/ns1:description",
        namespaces=ns,
    )
    if len(dataFlow) > 0:
        ssp_updates["dataFlow"] = ""
        for p in dataFlow[0].findall("ns1:p", namespaces=ns):
            if p.text:
                ssp_updates["dataFlow"] = ssp_updates["dataFlow"] + p.text + " "
        events_list.append(
            log_event(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                event_msg="Data Flow description recorded.",
            )
        )
    else:
        events_list.append(
            log_error(
                model_layer=SYSTEM_CHARS,
                record_type=SYSTEM_INFO,
                missing_element="Data Flow",
            )
        )

    update_ssp(ssp_updates, ssp_id)

    # properties such as authorization type will be mapped to regscale counterparts, where applicable, but will also be
    # stored as properties for consistency in export.
    # if Export team needs these NOT to be recorded in properties. that can be arranged. Export could just choose
    # to check if a property already exists before adding it, however, which would avoid potential for duplication on export
    """
        else:  # if none of these other condit`ions are met, store as a custom property
            ancestry = ''
            for parent in prop.parents:
                ancestry = ancestry + '/' + parent.name
            property_ = {}
            property_['key'] = prop.attrs['name']
            property_['value'] = prop.attrs['value']
            property_['label'] = 'Custom Property'
            property_['otherAttributes'] = ancestry + str(prop)
            properties_list.append(property_)
    """


def apply_mapping(mapping: List[tuple], value: str) -> str:
    """
    Apply a mapping to a value

    :param List[tuple] mapping: List of mapping pair tuples - (original,new)
    :param str value: Thing to be mapped to a new value
    :return: New value
    :rtype: str
    """
    for original, new in mapping:
        if value == original:
            value = new
            break
    return value


def post_SSP(api: Api, new_ssp: dict):
    """Create the initial SSP"""
    app = Application()
    headers_json = {
        "accept": "*/*",
        "Content-Type": "application/json-patch+json",
        "Authorization": app.config["token"],
    }
    # If data is incomplete This fails w/ 500 error ( which means the json string being received by the server is either malformed or missing something
    logger.info("Uploading SSP to RegScale...")
    try:
        ssp = SecurityPlan(**new_ssp)
    except ValidationError as exc:
        logger.error(f"Failed to validate: {exc}")
        return "artifacts/import-results.csv", {
            "status": "failed",
        }

    if new_ssp := ssp.create():
        new_ssp_id = new_ssp.id
    else:
        new_ssp_id = None
    logger.debug(new_ssp_id)

    if not new_ssp_id:
        # This generally succeeds if the ssp failed to pass pydantic check for required values in securityplans module
        logger.warning("Some required data may have failed to be imported. Trying to upload SSP with incomplete data ")
        import json

        dat = {}
        response = api.post(
            url=app.config["domain"] + "/api/securityplans",
            json=new_ssp,
        )
        logger.debug(response.status_code)
        if not response.raise_for_status():
            dat = response.json()
        if "id" in dat:
            new_ssp_id = dat["id"]

    return new_ssp_id


def parse_classificationType(information_types, ns, events_list, ssp_id):
    """Information Types in FedRAMP language correspond to Classification Types in RegScale, and are stored in the
    ClassificationTypes table. . Classification/Information Types are created in the 'Setup' portion of the RegScale app
    & at the Tenant level. Classification/Information types are then associated with an individual SSP through the
    'Subsystems' menu. The mapping between a Classification/Information type and the SSP is stored in the
    ClassifiedRecords database table."""

    # TODO: There currently isn't capability to track the base vs selected & adjustment reason, or categ. system
    for information_type in information_types:
        classificationType_dict = {}
        classificationType_dict["uuid"] = information_type.attrib["uuid"]
        # start with default values to avoid breaking on import
        classificationType_dict["title"] = "Name of Information Type"
        classificationType_dict["description"] = ""
        classificationType_dict["confidentiality"] = "Low"
        classificationType_dict["integrity"] = "Low"
        classificationType_dict["availability"] = "Low"
        if information_type.find("ns1:title", namespaces=ns) is not None:
            classificationType_dict["title"] = information_type.find("ns1:title", namespaces=ns).text
        if information_type.find("ns1:description", namespaces=ns) is not None:
            for p in information_type.find("ns1:description", namespaces=ns).findall("ns1:p", namespaces=ns):
                classificationType_dict["description"] = classificationType_dict["description"] + p.text + " "
        if information_type.find("ns1:confidentiality-impact/ns1:selected", namespaces=ns) is not None:
            classificationType_dict["confidentiality"] = apply_mapping(
                CAT_MAPPING,
                information_type.find("ns1:confidentiality-impact/ns1:selected", namespaces=ns).text,
            )
        if information_type.find("ns1:integrity-impact/ns1:selected", namespaces=ns) is not None:
            classificationType_dict["integrity"] = apply_mapping(
                CAT_MAPPING,
                information_type.find("ns1:integrity-impact/ns1:selected", namespaces=ns).text,
            )
        if information_type.find("ns1:availability-impact/ns1:selected", namespaces=ns) is not None:
            classificationType_dict["availability"] = apply_mapping(
                CAT_MAPPING,
                information_type.find("ns1:availability-impact/ns1:selected", namespaces=ns).text,
            )
        classification_type_id = upload_classificationType(classificationType_dict, ssp_id)
        if classification_type_id:
            events_list.append(
                log_event(
                    record_type="Information Type",
                    model_layer=SYSTEM_CHARS,
                    event_msg=f'Recorded Information Type for: {classificationType_dict["title"]}',
                )
            )
        else:
            events_list.append(
                log_error(
                    record_type="Information Type",
                    model_layer=SYSTEM_CHARS,
                    missing_element="Information Type",
                    event_msg='Failed to post Information Type for {classificationType_dict["title"]}.',
                )
            )


def upload_classificationType(classificationType_dict, ssp_id):
    app = Application()
    api = Api()
    headers_json = {
        "accept": "*/*",
        "Content-Type": "application/json-patch+json",
        "Authorization": app.config["token"],
    }
    ssp_classification = json.dumps(classificationType_dict)
    response = api.post(
        url=app.config["domain"] + "/api/classificationTypes",
        data=ssp_classification,
        headers=headers_json,
    )
    if response.status_code == 200:  # If successfully upload classification type, then add mapping to SSP
        classifiedRecords_entry = {}
        classifiedRecords_entry["classificationTypeId"] = json.loads(response.content)["id"]
        classifiedRecords_entry["parentRecordId"] = ssp_id
        classifiedRecords_entry["parentModule"] = "securityplans"
        classifiedRecord_json = json.dumps(classifiedRecords_entry)
        response = api.post(
            url=app.config["domain"] + "/api/classifiedRecords",
            data=classifiedRecord_json,
            headers=headers_json,
        )
        if response.status_code == 200:
            return "Success"
        else:
            return None
    else:
        return None


def parse_privacy(root, events_list, ns, ssp_id):
    "Privacy Impact Assessment pertains to the Privacy tab of RegScale Application and the Privacy database table."
    try:
        privacyImpactAssessment = {}
        privacyImpactAssessment["piiCollection"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="pta-1"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["piiPublicCollection"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="pta-2"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["piaConducted"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="pta-3"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["privacyActSystem"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="pta-4"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["sornExists"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="pta-4"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["sornId"] = root.xpath(
            '/*/ns1:system-characteristics/ns1:system-information/ns1:prop[@name="sorn-id"][@ns="https://fedramp.gov/ns/oscal"]/@value',
            namespaces=ns,
        )[0].capitalize()
        privacyImpactAssessment["SecurityPlanId"] = ssp_id
        privacyImpactAssessment["isPublic"] = True
        # Will have to come back to this. Requires linking to the Privacy officer / information officer contacts per
        # application layer logic, if any of the privacy questions are "yes".
        """
        response_id = post_privacy(privacyImpactAssessment)
        if response_id:
            events_list.append(log_event(model_layer='System Characteristics', record_type='Privacy Impact Assessment',
                                         event_msg='Successfully imported PTA/PIA data.'))
        else:
            events_list.append(log_error(model_layer='System Characteristics', record_type='Privacy Assessment',
                                         missing_element='Privacy Assessment',
                                         event_msg='Problem extracting or uploading PTA/PIA data.'))
        """
    except Exception as e:
        logger.warning(e)
        events_list.append(
            log_error(
                model_layer=SYSTEM_CHARS,
                record_type="Privacy Assessment",
                missing_element="Privacy Assessment",
                event_msg="Problem extracting PTA/PIA data.",
            )
        )
