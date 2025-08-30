"""fedramp v5 docx parser"""

import datetime
import logging
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from tempfile import gettempdir
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import error_and_exit, get_current_datetime
from regscale.core.utils.date import datetime_str
from regscale.integrations.public.fedramp.appendix_parser import AppendixAParser
from regscale.integrations.public.fedramp.docx_parser import SSPDocParser
from regscale.integrations.public.fedramp.markdown_parser import MDDocParser
from regscale.integrations.public.fedramp.rosetta import RosettaStone
from regscale.models import (
    ControlImplementation,
    ControlImplementationStatus,
    ControlObjective,
    ControlParameter,
    File,
    ImplementationObjective,
    ImplementationOption,
    LeveragedAuthorization,
    Parameter,
    PortsProtocol,
    Profile,
    ProfileMapping,
    SecurityControl,
    SecurityPlan,
    StakeHolder,
    SystemRole,
    User,
    ImplementationControlOrigin,
)
from regscale.utils.version import RegscaleVersion

SERVICE_PROVIDER_CORPORATE = "Service Provider Corporate"
DEFAULT_STATUS = ControlImplementationStatus.NotImplemented
SYSTEM_DESCRIPTION = "System Description"
AUTHORIZATION_BOUNDARY = "Authorization Boundary"
NETWORK_ARCHITECTURE = "System and Network Architecture"
DATA_FLOW = "Data Flows"
ENVIRONMENT = "System Environment and Inventory"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


IN_MEMORY_ROLES_PROCESSED = []
# precompile part pattern
PART_PATTERN = re.compile(r"(<p>Part\s[a-zA-Z]:</p>.*?)(?=<p>Part\s[a-zA-Z]:</p>|$)", re.DOTALL)


def get_fedramp_compliance_setting() -> Optional[Any]:
    """
    Quick lookup for the FedRAMP Compliance Setting

    :return: The FedRAMP Compliance Setting
    :rtype: Optional[Any]
    """
    # We have to be generic here, as ComplianceSetting may not exist in the database
    fedramp_comp = None
    try:
        from regscale.models.regscale_models.compliance_settings import ComplianceSettings

        setting = ComplianceSettings.get_by_current_tenant()
        logger.debug("Using new ComplianceSettings API")
        fedramp_comp = next(
            comp for comp in setting if comp.title == "FedRAMP Compliance Setting"
        )  # if this raises a StopIteration, we have a problem, Houston
    except Exception as e:
        logger.debug(f"Error getting Compliance Setting: {e}")
    return fedramp_comp


@dataclass
class Person:
    """
    Represents a person.
    """

    name: str
    phone: str
    email: str
    title: str
    user_id: Optional[str] = None


@dataclass
class Organization:
    """
    Represents an organization.
    """

    name: str
    address: str
    point_of_contact: Person


@dataclass
class PreparedBy:
    """
    Represents the prepared by information.
    """

    name: str
    street: str
    building: str
    city_state_zip: str


@dataclass
class SSPDoc:
    """
    Represents an SSP document.
    """

    name: str
    fedramp_id: str
    service_model: str
    digital_identity_level: str
    fips_199_level: str
    date_fully_operational: str
    deployment_model: str
    authorization_path: str
    description: str
    expiration_date: Optional[str] = None
    date_submitted: Optional[str] = None
    approval_date: Optional[str] = None
    csp_name: Optional[str] = None
    csp_street: Optional[str] = None
    csp_building: Optional[str] = None
    csp_city_state_zip: Optional[str] = None
    three_pao_name: Optional[str] = None
    three_pao_street: Optional[str] = None
    three_pao_building: Optional[str] = None
    three_pao_city_state_zip: Optional[str] = None
    version: str = "1.0"


@dataclass
class LeveragedService:
    """
    Represents a leveraged service.
    """

    fedramp_csp_name: str
    cso_name: str
    auth_type_fedramp_id: str
    agreement_type: str
    impact_level: str
    data_types: str
    authorized_user_authentication: str


@dataclass
class LeveragedServices:
    """
    Represents a list of leveraged services.
    """

    leveraged_services: List[LeveragedService]


@dataclass
class PortsAndProtocolData:
    """
    Represents ports and protocol data.
    """

    service: str
    port: int
    start_port: int
    end_port: int
    protocol: str
    ref_number: str
    purpose: str
    used_by: str


@dataclass
class ParamData:
    """
    Represents parameter data.
    """

    control_id: str
    parameter: Optional[str]
    parameter_value: str


def process_company_info(list_of_dicts: List[Dict[str, str]]) -> Organization:
    """
    Processes the company information table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: An Organization object representing the company information.
    :rtype: Organization
    """
    company_info = merge_dicts(list_of_dicts, True)

    person = Person(
        name=company_info.get("Name"),
        phone=company_info.get("Phone Number"),
        email=company_info.get("Email Address"),
        title="System Owner",
    )

    return Organization(
        name=company_info.get("Company / Organization"),
        address=company_info.get("Address"),
        point_of_contact=person,
    )


def process_ssp_info(list_of_dicts: List[Dict[str, str]]) -> SSPDoc:
    """
    Processes the SSP information table.

    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: An SSPDoc object representing the SSP information.
    :rtype: SSPDoc
    """
    ssp_info = merge_dicts(list_of_dicts, True)
    # print(ssp_info)

    today_dt = datetime.date.today()
    expiration_date = datetime.date(today_dt.year + 3, today_dt.month, today_dt.day).strftime("%Y-%m-%d %H:%M:%S")

    return SSPDoc(
        name=ssp_info.get("CSP Name:"),
        fedramp_id=ssp_info.get("FedRAMP Package ID:"),
        service_model=ssp_info.get("Service Model:"),
        digital_identity_level=ssp_info.get("Digital Identity Level (DIL) Determination (SSP Appendix E):"),
        fips_199_level=ssp_info.get("FIPS PUB 199 Level (SSP Appendix K):"),
        date_fully_operational=ssp_info.get("Fully Operational as of:"),
        deployment_model=ssp_info.get("Deployment Model:"),
        authorization_path=ssp_info.get("Authorization Path:"),
        description=ssp_info.get("General System Description:"),
        expiration_date=ssp_info.get("Expiration Date:", expiration_date),
        date_submitted=ssp_info.get("Date Submitted:", get_current_datetime()),
        approval_date=ssp_info.get("Approval Date:", get_current_datetime()),
    )


def build_leveraged_services(leveraged_data: List[Dict[str, str]]) -> List[LeveragedService]:
    """
    Processes the leveraged services table.

    :param List[Dict[str, str]] leveraged_data: The table to process.
    :return: A list of LeveragedService objects representing the leveraged services.
    :rtype: List[LeveragedService]
    """
    services = []
    for row in leveraged_data:
        service = LeveragedService(
            fedramp_csp_name=row.get("CSP/CSO Name (Name on FedRAMP Marketplace)"),
            cso_name=row.get(
                "CSO Service (Names of services and features - services from a single CSO can be all listed in one cell)"
            ),
            auth_type_fedramp_id=row.get("Authorization Type (JAB or Agency) and FedRAMP Package ID #"),
            agreement_type=row.get("Nature of Agreement"),
            impact_level=row.get("Impact Level (High, Moderate, Low, LI-SaaS)"),
            data_types=row.get("Data Types"),
            authorized_user_authentication=row.get("Authorized Users/Authentication"),
        )
        services.append(service)

    return services


def process_person_info(list_of_dicts: List[Dict[str, str]]) -> Person:
    """
    Processes the person information table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: A Person object representing the person information.
    :rtype: Person
    """
    person_data = merge_dicts(list_of_dicts, True)
    person = Person(
        name=person_data.get("Name"),
        phone=person_data.get("Phone Number"),
        email=person_data.get("Email Address"),
        title=person_data.get("Title"),
    )
    return person


def process_ports_and_protocols(list_of_dicts: List[Dict[str, str]]) -> List[PortsAndProtocolData]:
    """
    Processes the ports and protocols table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: A list of PortsAndProtocolData objects representing the ports and protocols information.
    :rtype: List[PortsAndProtocolData]
    """
    ports_an_protocols = []
    for row in list_of_dicts:
        try:
            port_col = "Port #"
            ports_an_protocols.append(
                PortsAndProtocolData(
                    service=row.get("Service Name"),
                    port=int(row.get(port_col)) if "-" not in row.get(port_col) else 0,
                    start_port=(
                        int(row.get(port_col).split("-")[0]) if "-" in row.get(port_col) else row.get(port_col, 0)
                    ),
                    end_port=int(row.get(port_col).split("-")[1]) if "-" in row.get(port_col) else row.get(port_col, 0),
                    protocol=row.get("Transport Protocol"),
                    ref_number=row.get("Reference #"),
                    purpose=row.get("Purpose"),
                    used_by=row.get("Used By"),
                )
            )
        except ValueError:
            logger.warning(f"Skipping bad data unable to processing row: {row}")

    return ports_an_protocols


def merge_dicts(list_of_dicts: List[Dict], prioritize_first: bool = False) -> dict:
    """
    Merges a list of dictionaries into a single dictionary.
    :param List[Dict] list_of_dicts: The list of dictionaries to merge.
    :param bool prioritize_first: Whether to prioritize the first dictionary in the list.
    :return: A single dictionary containing the merged data.
    :rtype: dict
    """

    merged_dict = {}
    for d in list_of_dicts:
        if prioritize_first:
            merged_dict.update(d, **merged_dict)  # Merge with priority to earlier values
        else:
            merged_dict.update(d)  # Simple merge

    return merged_dict


def identify_and_process_tables(tables: List[Dict[str, Any]]):
    """
    Identifies and processes tables based on their content keywords and processes them accordingly.
    :param List[Dict[str, Any]] tables: The tables to process.
    :return: A dictionary containing the processed data.
    :rtype: Dict[str, Any]
    """
    processed_data = {
        "ssp_doc": None,
        "org": None,
        "prepared_by": None,
        "stakeholders": [],
        "services": [],
        "ports_and_protocols": [],
    }
    # logger.info(tables)
    for item in tables:
        process_table_based_on_keys(item, processed_data)
        logger.debug(item.get("preceding_text"))
        logger.debug(item.get("table_data"))

    owner, isso = identify_owner_or_isso(processed_data.get("stakeholders", []))
    logger.debug(f"Owner: {owner}")
    if owner:
        processed_data["owner"] = owner
    if isso:
        processed_data["isso"] = isso

    return processed_data


def identify_owner_or_isso(people: List[Person]) -> Tuple[Person, Person]:
    """
    Identifies the ISSO and the Owner from a list of people.

    :param List[Person] people: A list of Person objects representing the stakeholders.
    :returns: A tuple containing the ISSO and the Owner.
    :rtype: Tuple[Person, Person]
    """
    logger.info(f"Found People: {len(people)}")
    existing_users = []
    try:
        existing_users = User.get_list()
    except Exception as e:
        logger.warning(f"Error getting Users: {e}")
    logger.debug(f"Found Users: {existing_users}")
    owner, isso = find_owner_and_isso(people)

    logger.debug(f"Found owner: {owner}")
    logger.debug(f"Found isso: {isso}")
    if owner or isso:
        logger.debug(f"Found existing Users: {len(existing_users)}")
    existing_users_dict = {u.email: u for u in existing_users if hasattr(u, "email")}
    if existing_users_dict and owner and isso:
        try:
            owner = existing_users_dict.get(owner.email)
            isso = existing_users_dict.get(isso.email)
        except Exception as e:
            logger.warning(f"Error getting Users: {e}")
    return owner, isso


def find_owner_and_isso(
    people: List[Person],
) -> Tuple[Optional[Person], Optional[Person]]:
    """
    Identifies the ISSO and the Owner from a list of people.

    :param List[Person] people: A list of Person objects representing the stakeholders.
    :returns: A tuple containing the ISSO and the Owner.
    :rtype: Tuple[Optional[Person], Optional[Person]]
    """
    owner = None
    isso = None
    try:
        for person in people:
            percent_match_owner = "System Owner".lower() in person.title.lower()
            percent_match_isso = "Information System Security Officer".lower() in person.title.lower()

            logger.debug(f"Owner match: {percent_match_owner}")
            logger.debug(f"Isso match: {percent_match_isso}")
            if percent_match_owner:
                owner = person
            if percent_match_isso:
                isso = person
    except Exception as e:
        logger.warning(f"Error finding Owner and ISSO: {e}")
    return owner, isso


def process_table_based_on_keys(table: any, processed_data: Dict[str, Any]):
    """
    Processes a table based on the keys present in the first row of the table.
    :param any table: The table to process.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    """
    try:
        key = table.get("preceding_text")
        merged_dict = merge_dicts(table.get("table_data"), True)
        table_data = table.get("table_data")
        fetch_ports(key, processed_data, table_data, merged_dict)
        fetch_stakeholders(merged_dict, table_data, processed_data, key)
        fetch_services(merged_dict, table_data, processed_data)
        fetch_ssp_info(merged_dict, table_data, processed_data, key)
        fetch_prep_data(table_data, processed_data, key)
    except Exception as e:
        logger.warning(f"Error Processing Table - {table.get('preceding_text', '') if table else ''}: {e}")


def fetch_prep_data(
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches Prepared By and Prepared For information from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.

    """
    if "Prepared by" in key:
        logger.info("Processing Prepared By")
        processed_data["prepared_by"] = process_prepared_by(table_data)
    if "Prepared for" in key:
        logger.info("Processing Prepared By")
        processed_data["prepared_for"] = process_prepared_by(table_data)


def fetch_ssp_info(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches SSP information from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "CSP Name:" in merged_dict:
        logger.info("Processing SSP Doc")
        processed_data["ssp_doc"] = process_ssp_info(table_data)
    if "Document Revision History" in key:
        logger.info("Processing Version")
        processed_data["version"] = get_max_version(entries=table_data)
        if processed_data["ssp_doc"]:
            processed_data["ssp_doc"].version = processed_data.get("version")
        logger.info(f"Processed Version: {processed_data['version']}")


def fetch_services(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
):
    """
    Fetches services data from the table.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "CSP/CSO Name (Name on FedRAMP Marketplace)" in merged_dict:
        logger.info("Processing Leveraged Services")
        processed_data["services"] = build_leveraged_services(table_data)


def fetch_stakeholders(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches stakeholders data from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "Name" in merged_dict and "Company / Organization" in table_data[0]:
        logger.info("Processing Organization and Stakeholders")
        process_organization_and_stakeholders(table_data, processed_data)
    if ("ISSO (or Equivalent) Point of Contact" in key) or ("Table 4.1" in key):
        logger.info("Processing Stakeholders")
        person = process_person_info(table_data)
        processed_data["stakeholders"].append(person)


def fetch_ports(
    key: str,
    processed_data: Dict[str, Any],
    table_data: List[Dict[str, str]],
    merged_dict: Dict[str, str],
):
    """
    Fetches ports and protocols data from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "Services, Ports, and Protocols" in key and "Port #" in merged_dict:
        logger.info("Processing Ports and Protocols")
        processed_data["ports_and_protocols"] = process_ports_and_protocols(table_data)


def process_prepared_by(table: List[Dict[str, str]]) -> PreparedBy:
    """
    Processes the prepared by information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :return: A PreparedBy object representing the prepared by information.
    :rtype: PreparedBy
    """
    prepared_by = merge_dicts(table, True)
    return PreparedBy(
        name=prepared_by.get("Organization Name"),
        street=prepared_by.get("Street Address"),
        building=prepared_by.get("Suite/Room/Building"),
        city_state_zip=prepared_by.get("City, State, Zip"),
    )


def process_version(table: List[Dict[str, str]]) -> str:
    """
    Processes the version information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :return: The version number.
    :rtype: str
    """
    # Assuming the version is stored under a key named "Version" in one of the table rows
    return get_max_version(table)


def process_organization_and_stakeholders(table: List[Dict[str, str]], processed_data: Dict[str, Any]):
    """
    Processes organization and stakeholders information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    """
    processed_data["org"] = process_company_info(table)
    person = process_person_info(table)
    processed_data["stakeholders"].append(person)


def process_fedramp_docx_v5(
    file_name: str,
    base_fedramp_profile_id: int,
    save_data: bool,
    add_missing: bool,
    appendix_a_file_name: str,
) -> int:
    """
    Processes a FedRAMP document and loads it into RegScale.
    :param str file_name: The path to the FedRAMP document.
    :param int base_fedramp_profile_id: The name of the RegScale FedRAMP profile to use.
    :param bool save_data: Whether to save the data as a JSON file.
    :param bool add_missing: Whether to create missing controls from profile in the SSP.
    :param str appendix_a_file_name: The path to the Appendix A document.
    :return: The created SSP ID.
    :rtype: int
    """
    logger.info(f"Processing FedRAMP Document: {file_name}")
    logger.info(f"Appendix A File: {appendix_a_file_name}")
    ssp_parser = SSPDocParser(file_name)

    logger.info(f"Using the following values: save_data: {save_data} and add_missing: {add_missing}")

    tables = ssp_parser.parse()
    doc_text_dict = ssp_parser.text
    app = Application()
    config = app.config
    user_id = config.get("userId")

    processed_data = identify_and_process_tables(tables)
    parent_id = processing_data_from_ssp_doc(processed_data, user_id, doc_text_dict)
    if appendix_a_file_name:
        logger.info(f"Converting {appendix_a_file_name} to markdown format...")
        try:
            mdparser = MDDocParser(appendix_a_file_name, base_fedramp_profile_id)
        except Exception as e:
            logger.error(f"Error converting {appendix_a_file_name} to markdown format: {e}.")
            return parent_id

        logger.info("Successfully converted Appendix A file to markdown format.")

        # new markdown dictionary for control parts.
        mdparts_dict = mdparser.get_parts()

        logger.info(f"Processing Appendix A File: {appendix_a_file_name}")

        parser = AppendixAParser(filename=appendix_a_file_name)
        controls_implementation_dict = parser.fetch_controls_implementations()

        process_appendix_a(
            parent_id=parent_id,
            profile_id=base_fedramp_profile_id,
            add_missing=add_missing,
            controls_implementation_dict=controls_implementation_dict,
            mdparts_dict=mdparts_dict,
        )
    extract_and_upload_images(file_name, parent_id)
    return parent_id


def log_dictionary_items(dict_items: Dict[str, str]):
    """
    Logs the items in a dictionary.
    :param Dict[str, str] dict_items: The dictionary to log.
    """
    for key, value in dict_items.items():
        if value:
            logger.info(f"{key}: {value}")


def handle_implemented(row_data: Dict, status: str) -> str:
    """
    Handles the implemented status of a control.
    :param Dict row_data: The data from the row.
    :param str status: The current status of the control.
    :return: The updated status of the control.
    :rtype: str
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if key == "Implemented" and value:
            status = ControlImplementationStatus.FullyImplemented.value
    return status


def handle_service_provider_corporate(row_data: Dict, responsibility: str) -> str:
    """
    Handles the service provider corporate responsibility of a control.
    :param Dict row_data:
    :param str responsibility:
    :return: fetched responsibility
    :rtype: str
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if value:
            responsibility = key
    return responsibility


def handle_parameter(row_data: Dict, parameters: Dict, control_id: int):
    """
    Handles the parameters of a control.
    :param Dict row_data: The data from the row.
    :param Dict parameters: The parameters dictionary.
    :param int control_id: The control ID.
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if value:
            if parameters.get(control_id):
                parameters[control_id].append(value)
            else:
                parameters[control_id] = [value]


def handle_row_data(
    row: Dict,
    control: ControlImplementation,
    status: str,
    responsibility: str,
    parameters: Dict,
    key: str,
    alternative_key: str,
) -> Tuple[str, str, Dict]:
    """
    Handles the data from a row.
    :param Dict row: The row to process.
    :param ControlImplementation control:
    :param str status:
    :param str responsibility:
    :param Dict parameters:
    :param str key:
    :param str alternative_key:
    :return: A tuple containing the updated status, responsibility, and parameters.
    :rtype: Tuple[str, str, Dict]
    """
    row_data = row.get(key, row.get(alternative_key))
    logger.info(f"Row Data: {row_data}")

    if "Implemented" in row_data:
        status = handle_implemented(row_data, status)
    elif SERVICE_PROVIDER_CORPORATE in row_data:
        responsibility = handle_service_provider_corporate(row_data, responsibility)
    elif "Parameter" in row_data:
        handle_parameter(row_data, parameters, control.id)

    return status, responsibility, parameters


def process_fetch_key_value(summary_data: Dict) -> Optional[str]:
    """
    Extracts key information from the summary data.
    :param Dict summary_data: The summary data from the row.
    :return: str: The key from the summary data.
    :rtype: Optional[str]
    """
    for key, value in summary_data.items():
        if value:
            logger.info(f"{key}: {value}")
            return key
    return None


def process_parameter(summary_data: Dict, control_id: int, current_parameters: List[Dict]):
    """
    Processes the parameters from the summary data.
    :param Dict summary_data: The summary data from the row.
    :param int control_id: The control ID.
    :param List[Dict] current_parameters: The current parameters.
    """
    for key, value in summary_data.items():
        if value:
            parameter_name = key.replace("Parameter ", "").strip()
            param = {
                "control_id": control_id,
                "parameter_name": parameter_name if parameter_name else None,
                "parameter_value": value,
            }
            if param not in current_parameters:
                current_parameters.append(param)


def process_row_data(row: Dict, control: SecurityControl, control_dict: Dict) -> Tuple[str, str, List[Dict]]:
    """
    Processes a single row of data, updating status, responsibility, and parameters based on control summary information.
    :param Dict row: The row to process.
    :param SecurityControl control: The control to process.
    :param Dict control_dict: The dictionary containing the control data.
    :return: A tuple containing the updated status, responsibility, and parameters.
    :rtype: Tuple[str, str, List[Dict]]
    """
    control_id_key = f"{control.controlId} Control Summary Information"
    alternate = format_alternative_control_key(control.controlId) or control.controlId
    alternative_control_id_key = f"{alternate} Control Summary Information"

    summary_data = row.get(control_id_key, row.get(alternative_control_id_key))
    if summary_data:
        logger.info(f"Row Data: {summary_data}")

        if "Implemented" in summary_data:
            status = process_fetch_key_value(summary_data)
            control_dict["status"] = (
                ControlImplementationStatus.FullyImplemented.value if status == "Implemented" else status
            )

        if SERVICE_PROVIDER_CORPORATE in summary_data:
            control_dict["responsibility"] = process_fetch_key_value(summary_data)

        if "Parameter" in summary_data:
            process_parameter(summary_data, control.id, control_dict.get("parameters", []))

    return (
        control_dict.get("status"),
        control_dict.get("responsibility"),
        control_dict.get("parameters"),
    )


def process_fetch_key_if_value(summary_data: Dict) -> str:
    """
    Extracts key information from the summary data.
    :param Dict summary_data: The summary data from the row.
    :return: str: The key from the summary data.
    :rtype: str
    """
    for key, value in summary_data.items():
        if value is True or value == "☒":
            logger.info(f"{key}: {value}")
            return key


def _find_statement(control: any, alternative_control_id: str, row: Dict, control_dict: Dict) -> str:
    """
    Find the statement for the control.
    :param any control:
    :param str alternative_control_id:
    :param Dict row:
    :param Dict control_dict:
    :return: str: The statement for the control.
    :rtype: str
    """
    key_statment = f"{control.controlId} What is the solution and how is it implemented?"
    key_alt_statment = f"{alternative_control_id} What is the solution and how is it implemented?"
    statement_dict = row.get(key_statment) or row.get(key_alt_statment)

    if isinstance(statement_dict, dict):
        control_dict["statement"] = " ".join(f"{key} {value}" for key, value in statement_dict.items() if value)
    elif isinstance(statement_dict, str):
        control_dict["statement"] = statement_dict
    return ""


def fetch_profile_mappings(profile_id: int) -> List[ProfileMapping]:
    """
    Fetches the profile mappings for a given profile.
    :param int profile_id: The profile ID.
    :return: A list of ProfileMapping objects.
    :rtype: List[ProfileMapping]
    """
    profile_mappings = []
    try:
        profile = Profile.get_object(object_id=profile_id)
        if profile and getattr(profile, "name"):
            logger.debug(f"Profile: {profile.name}")
            profile_mappings = ProfileMapping.get_by_profile(profile_id=profile.id)
    except AttributeError:
        error_and_exit(f"Profile #{profile_id} not found, exiting ..")
    logger.info(f"Found {len(profile_mappings)} controls in profile")
    return profile_mappings


def load_appendix_a(
    appendix_a_file_name: str,
    parent_id: int,
    profile_id: int,
    add_missing: bool,
):
    """
    Loads the Appendix A data.
    :param str appendix_a_file_name: The path to the Appendix A file.
    :param int parent_id: The parent ID.
    :param int profile_id: The profile ID.
    :param bool add_missing: Whether to add missing controls.
    """
    logger.info(f"Processing Appendix A File: {appendix_a_file_name}")
    parser = AppendixAParser(filename=appendix_a_file_name)
    controls_implementation_dict = parser.fetch_controls_implementations()

    process_appendix_a(
        parent_id=parent_id,
        profile_id=profile_id,
        add_missing=add_missing,
        controls_implementation_dict=controls_implementation_dict,
    )


def process_appendix_a(
    parent_id: int,
    profile_id: int,
    add_missing: bool = False,
    controls_implementation_dict: Dict = None,
    mdparts_dict: Dict = None,
):
    """
    Processes the Appendix A data.
    :param int parent_id: The parent ID.
    :param int profile_id: The profile ID.
    :param bool add_missing: Whether to add missing controls.
    :param Dict controls_implementation_dict: The controls implementation dictionary.
    :param Dict mdparts_dict: The control parts dictionary.
    """
    profile_mappings = fetch_profile_mappings(profile_id=profile_id)
    data_dict = controls_implementation_dict
    existing_controls: list[ControlImplementation] = ControlImplementation.get_all_by_parent(
        parent_id=parent_id, parent_module=SecurityPlan.get_module_slug()
    )
    for control in existing_controls:
        if not control.parentId or control.parentId == 0:
            control.parentId = parent_id

    logger.info(f"Found {len(existing_controls)} existing controls")
    logger.debug(f"{existing_controls=}")
    existing_control_dict = {c.controlID: c for c in existing_controls if c and c.controlID}

    param_mapper = RosettaStone()
    param_mapper.load_fedramp_version_5_mapping()
    param_mapper.lookup_l0_by_l1()
    for mapping in profile_mappings:
        control = SecurityControl.get_object(object_id=mapping.controlID)

        if not control:
            logger.debug(f"Control not found in mappings: {mapping.controlID}")
            continue
        alternate = control.controlId
        try:
            alternate = format_alternative_control_key(control.controlId)
        except ValueError:
            logger.debug(f"Error formatting alternative control key: {control.controlId}")
        alternative_control_id = alternate
        control_dict = data_dict.get(control.controlId)
        if not control_dict:
            control_dict = data_dict.get(alternative_control_id)
        if not control_dict:
            logger.debug(f"Control not found in parsed controls: {control.controlId}")
            continue

        process_control_implementations(
            existing_control_dict,
            control,
            control_dict,
            parent_id,
            add_missing,
            mdparts_dict,
        )


def process_control_implementations(
    existing_control_dict: Dict,
    control: SecurityControl,
    control_dict: Dict,
    parent_id: int,
    add_missing: bool = False,
    mdparts_dict: Dict = None,
):
    """
    Processes the control implementations.
    :param Dict existing_control_dict: The existing control dictionary.
    :param SecurityControl control: The control implementation object.
    :param Dict control_dict: The control dictionary.
    :param int parent_id: The parent ID.
    :param bool add_missing: Whether to add missing controls.
    :param Dict mdparts_dict: The control parts dictionary.
    """
    supporting_roles, primary_role = get_primary_and_supporting_roles(
        control_dict.get("responsibility").split(",") if control_dict.get("responsibility") else [],
        parent_id,
    )

    if existing_control := existing_control_dict.get(control.id):
        _update_existing_control(
            existing_control,
            control,
            control_dict,
            primary_role,
            supporting_roles,
            mdparts_dict,
            parent_id,
        )
    else:
        _create_control_implementation(
            control, control_dict, primary_role, parent_id, add_missing, supporting_roles, mdparts_dict
        )


def _create_control_implementation(
    control: SecurityControl,
    control_dict: Dict,
    primary_role: Dict,
    parent_id: int,
    add_missing: bool,
    supporting_roles: List[Dict],
    mdparts_dict: Dict,
):
    """
    Creates a new control implementation.
    :param SecurityControl control:
    :param Dict control_dict:
    :param Dict primary_role:
    :param int parent_id:
    :param bool add_missing:
    :param List[Dict] supporting_roles:
    :param Dict mdparts_dict:
    :return:
    """
    new_statement = mdparts_dict.get(control.controlId) if mdparts_dict else None
    implementation = create_implementations(
        control,
        parent_id,
        control_dict.get("status"),
        new_statement if new_statement else control_dict.get("statement"),
        control_dict.get("origination"),
        control_dict.get("parameters"),
        add_missing,
        role_id=primary_role.get("id") if primary_role else None,
    )
    if implementation:
        if parts := control_dict.get("parts"):
            handle_parts(
                parts=parts,
                status=map_implementation_status(control_dict.get("status")),
                control=control,
                control_implementation=implementation,
                mdparts_dict=mdparts_dict,
                origination=control_dict.get("origination"),
            )
        if params := control_dict.get("parameters"):
            handle_params(
                parameters=params,
                control=control,
                control_implementation=implementation,
            )
        add_roles_to_control_implementation(implementation, supporting_roles)


def _update_existing_control(
    existing_control: ControlImplementation,
    control: SecurityControl,
    control_dict: Dict,
    primary_role: Dict,
    supporting_roles: List[Dict],
    mdparts_dict: Dict,
    parent_id: int,
):
    """
    Updates the existing control implementation.
    :param existing_control ControlImplementation : The existing control implementation.
    :param control SecurityControl: The control object.
    :param control_dict Dict:
    :param primary_role Dict:
    :param supporting_roles List[Dict:
    :param mdparts_dict Dict:
    :param parent_id int:
    """
    new_statement = mdparts_dict.get(control.controlId) if mdparts_dict else None
    update_existing_control(
        existing_control,
        control_dict.get("status"),
        new_statement if new_statement else control_dict.get("statement"),
        control_dict.get("origination"),
        primary_role if primary_role and isinstance(primary_role, dict) and primary_role.get("id") else None,
        parent_id,
    )
    if params := control_dict.get("parameters"):
        handle_params(
            params,
            control=control,
            control_implementation=existing_control,
        )
    if parts := control_dict.get("parts"):
        handle_parts(
            parts=parts,
            status=map_implementation_status(control_dict.get("status")),
            control=control,
            control_implementation=existing_control,
            mdparts_dict=mdparts_dict,
            origination=control_dict.get("origination"),
        )
    add_roles_to_control_implementation(existing_control, supporting_roles)


def add_roles_to_control_implementation(implementation: ControlImplementation, roles: List[Dict]):
    """
    Updates roles for a control implementation by checking existing roles and adding/removing as appropriate.
    This prevents duplicate roles on successive imports.
    :param ControlImplementation implementation: The control implementation.
    :param List[Dict] roles: The list of roles to set.
    """
    if not implementation or not implementation.id:
        logger.warning("Control implementation is missing or has no ID, cannot update roles")
        return

    try:
        # Get existing roles for this control implementation
        from regscale.models.regscale_models.implementation_role import ImplementationRole

        # Get existing roles
        existing_roles = ImplementationRole.get_all_by_parent(
            parent_id=implementation.id, parent_module=implementation._module_string
        )
        existing_role_ids = {role.roleId for role in existing_roles if role and role.roleId}

        # Get target role IDs from the new roles list
        target_role_ids = {role.get("id") for role in roles if isinstance(role, dict) and role.get("id")}

        # Find roles to add (in target but not in existing)
        roles_to_add = target_role_ids - existing_role_ids

        # Find roles to remove (in existing but not in target)
        roles_to_remove = existing_role_ids - target_role_ids

        # Add new roles
        for role_id in roles_to_add:
            try:
                implementation.add_role(role_id)
                logger.debug(f"Added role {role_id} to control implementation {implementation.id}")
            except Exception as e:
                logger.warning(f"Failed to add role {role_id} to control implementation {implementation.id}: {e}")

        # Remove roles that are no longer needed
        _remove_roles_from_control_implementation(implementation, roles_to_remove, existing_roles)

        if roles_to_add or roles_to_remove:
            logger.info(
                f"Updated roles for control implementation {implementation.id}: added {len(roles_to_add)}, removed {len(roles_to_remove)}"
            )
        else:
            logger.debug(f"No role changes needed for control implementation {implementation.id}")

    except Exception as e:
        logger.error(f"Error updating roles for control implementation {implementation.id}: {e}")
        # Fallback to old behavior if there's an error
        _fallback_add_roles_to_control_implementation(implementation, roles)


def _remove_roles_from_control_implementation(
    implementation: ControlImplementation, roles_to_remove: set, existing_roles: List
):
    """
    Removes roles that are no longer needed from a control implementation.
    :param ControlImplementation implementation: The control implementation to remove roles from.
    :param set roles_to_remove: Set of role IDs that should be removed.
    :param List existing_roles: List of existing ImplementationRole objects.
    """
    for role_id in roles_to_remove:
        try:
            # Find the ImplementationRole record to delete
            for existing_role in existing_roles:
                if existing_role.roleId == role_id:
                    existing_role.delete()
                    logger.debug(f"Removed role {role_id} from control implementation {implementation.id}")
                    break
        except Exception as e:
            logger.warning(f"Failed to remove role {role_id} from control implementation {implementation.id}: {e}")


def _fallback_add_roles_to_control_implementation(implementation: ControlImplementation, roles: List[Dict]):
    """
    Fallback method for adding roles to a control implementation when the main method fails.
    This uses the old behavior of simply adding roles without checking for duplicates.
    :param ControlImplementation implementation: The control implementation.
    :param List[Dict] roles: The list of roles to add.
    """
    if roles and len(roles) > 0:
        for role in roles:
            if isinstance(role, dict) and role.get("id"):
                try:
                    implementation.add_role(role.get("id"))
                except Exception as add_error:
                    logger.warning(f"Failed to add role {role.get('id')}: {add_error}")


def get_primary_and_supporting_roles(roles: List, parent_id: int) -> Tuple[List, Dict]:
    """
    Get the primary role.
    :param List roles: The list of roles.
    :param int parent_id: The parent ID.
    :return: The primary role and supporting roles.
    :rtype: Tuple[List, Dict]
    """
    supporting_roles = []
    primary_role = None
    if roles and len(roles) >= 1:
        primary_role = get_or_create_system_role(roles[0], parent_id)
        for role in roles[1:]:
            if role:
                supporting_roles.append(get_or_create_system_role(role, parent_id))
    return supporting_roles, primary_role


def get_or_create_system_role(role: str, ssp_id: int) -> Optional[Dict]:
    """
    Creates a System Role.
    :param str role: The name of the role.
    :param int ssp_id: The user ID.
    :return: The created role.
    :rtype: Optional[Dict]
    """
    app = Application()
    try:
        role_name = role.strip().replace(",", "")
        if role_name == "<Roles>":
            return None
        existing_sys_roles = [
            r
            for r in SystemRole.get_all_by_parent(parent_id=ssp_id, parent_module=SecurityPlan.get_module_slug())
            if r is not None
        ]
        existing_roles_dict = {r.roleName: r for r in existing_sys_roles}
        in_mem_roles_processed_dict = {r.roleName: r for r in IN_MEMORY_ROLES_PROCESSED if r is not None}
        existing_role = existing_roles_dict.get(role_name) or in_mem_roles_processed_dict.get(role_name)
        IN_MEMORY_ROLES_PROCESSED.append(existing_role)

        if existing_role:
            logger.debug("Role: %s already exists in RegScale, skipping insert..", role_name.strip())
            return existing_role.model_dump()
        else:
            user_id = app.config.get("userId")
            if role_name:
                sys_role = SystemRole(
                    roleName=role_name,
                    roleType="Internal",
                    accessLevel="Privileged",
                    sensitivityLevel=ControlImplementationStatus.NA.value,
                    assignedUserId=user_id,
                    privilegeDescription=role_name,
                    securityPlanId=ssp_id,
                    functions=role_name,
                ).create()
                if sys_role:
                    IN_MEMORY_ROLES_PROCESSED.append(sys_role)
                return sys_role.model_dump()
    except Exception as e:
        logger.warning(f"Error creating role: {role} - {e}")
        return {}


def create_implementations(
    control: SecurityControl,
    parent_id: int,
    status: str,
    statement: str,
    responsibility: str,
    parameters: List[Dict],
    add_missing: bool = False,
    role_id: int = None,
) -> ControlImplementation:
    """
    Creates the control implementations.
    :param SecurityControl control: The control object.
    :param int parent_id: The parent ID.
    :param str status: The status of the implementation.
    :param str statement: The statement of the implementation.
    :param str responsibility: The responsibility of the implementation.
    :param List[Dict] parameters: The parameters of the implementation.
    :param bool add_missing: Whether to add missing controls.
    :param int role_id: The role ID.
    :return: The created control implementation.
    :rtype: ControlImplementation
    """
    if status and status.lower() == "implemented":
        status = ControlImplementationStatus.FullyImplemented.value
    if control and (status == DEFAULT_STATUS and add_missing) or (status != DEFAULT_STATUS):
        logger.debug(
            f"Creating Control: {control.controlId} - {control.id} - {status} - {statement} - {responsibility}"
        )
        logger.debug(f"params: {parameters}")
        justification, planned_date, steps_to_implement = create_control_implementation_defaults(status)

        control_implementation = ControlImplementation(
            parentId=parent_id,
            parentModule="securityplans",
            controlID=control.id,
            status=map_implementation_status(status),
            responsibility=map_responsibility(responsibility),
            implementation=clean_statement(statement),
            systemRoleId=role_id,
            exclusionJustification=justification,
            stepsToImplement=steps_to_implement,
            plannedImplementationDate=planned_date,
        )
        return control_implementation.create()
        # handle_params(parameters, control, control_implementation)


def create_control_implementation_defaults(status: str) -> Tuple[str, str, str]:
    """
    Creates a tuple with default values for exclusion_justification and planned_implementation_date.

    :return: A tuple with default values for exclusion_justification and planned_implementation_date.
    :rtype: Tuple[str, str, str]
    """
    exclusion_justification = None
    planned_implementation_date = None
    steps_to_implement = None
    if status == ControlImplementationStatus.NA.value:
        exclusion_justification = "This is an automated justification, please update"

    if status == "Planned":
        current_date = datetime.datetime.now()
        planned_implementation_date = datetime_str(current_date + datetime.timedelta(days=30))
        steps_to_implement = "Automated steps to implement, please update"

    return exclusion_justification, planned_implementation_date, steps_to_implement


def clean_statement(statement: Union[str, List]) -> str:
    """
    Cleans the statement.
    :param Union[str, List] statement: The statement to clean.'
    :return: The cleaned statement.
    :rtype: str
    """
    if isinstance(statement, list):
        return " ".join(statement)
    return statement or ""


def find_matching_parts(part: str, other_ids: List[str]) -> List[str]:
    """
    Find and return the otherId values that contain the specified part (e.g., "Part a"),
    by directly checking for the presence of a substring like '_obj.a'.
    :param str part: The part to look for.
    :param List[str] other_ids: The list of otherId values to search.
    :return: A list of otherId values that contain the specified part.
    :rtype: List[str]
    """
    # Extract the letter part (e.g., "a") from the input string.
    part_letter = part[-1].lower()  # Assuming the format "Part X" where X is the part letter.

    # Construct the substring to look for in otherId values.
    part_pattern = f"_obj.{part_letter}"

    # Collect and return all matching otherId values.
    matches = [
        other_id for other_id in other_ids if part_pattern in other_id.lower() or part_letter in other_id.lower()
    ]

    return matches


def get_or_create_option(
    part_name: str,
    part_value: str,
    control: SecurityControl,
    objective: ControlObjective,
    existing_options: List[ImplementationOption],
    status: Optional[str],
    parent_id: int,
) -> Optional[ImplementationOption]:
    """
    Get or create an implementation option.
    :param str part_name: The name of the part.
    :param str part_value: The value of the part.
    :param SecurityControl control: The security control object.
    :param ControlObjective objective: The control objective object.
    :param List[ImplementationOption] existing_options: The existing options.
    :param Optional[str] status: The status of the implementation.
    :param int parent_id: The parent ID.
    :return: The implementation option.
    :rtype: Optional[ImplementationOption]
    """
    option = None
    for o in existing_options:
        if o.name == part_name:
            option = o
            break
    if not option:
        try:
            option = ImplementationOption(
                name=part_name,
                description=part_value,
                objectiveId=objective.id,
                acceptability=status,
                securityControlId=objective.securityControlId,
            )
            options = ImplementationOption.get_all_by_parent(parent_id=objective.securityControlId, plan_id=parent_id)
            for o in options:
                if o.name == part_name:
                    return o
                elif option.name == o.name:
                    return o
                else:
                    option.get_or_create()
                    return option
        except Exception:
            logger.warning(f"Error creating option: {part_name}")
    return option


def extract_parts(content: str) -> dict:
    """
    Splits a string into parts based on markers like "Part a:", "Part b:", etc.
    If no markers are found, the entire content is treated as general content.
    :param str content: The content to split into parts.
    :return: A dictionary where keys are "Part a", "Part b", etc., and values are the corresponding content.
    :rtype: dict
    """
    output = {}
    if not content:
        return output
    # Regex to find "Part a:", "Part b:", etc., regardless of surrounding HTML tags
    part_pattern = re.compile(r"(?:<[^>]*>)?Part ([a-z]):(?:</[^>]*>)?", re.IGNORECASE)

    # Find all matches for "Part a:", "Part b:", etc.
    parts = part_pattern.split(content)

    if len(parts) == 1:  # No "Part a:", "Part b:" markers
        output["default"] = content.strip()
    else:
        # First chunk is general content (if any)
        general_content = parts[0].strip()
        if general_content:
            output["default"] = general_content

        # Iterate through the matched parts and their corresponding content
        for i in range(1, len(parts), 2):
            part_letter = parts[i].lower()  # Part letter (e.g., 'a', 'b')
            part_content = parts[i + 1].strip()  # Corresponding HTML/content for the part
            output[f"Part {part_letter}"] = part_content

    return output


def handle_parts(
    parts: Dict,
    status: str,
    control: SecurityControl,
    control_implementation: ControlImplementation,
    mdparts_dict: Dict,
    origination: str = None,
):
    """
    Handle the parts for the given control and control implementation.
    :param Dict parts: The parts to handle.
    :param str status: The status of the implementation.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.
    :param Dict mdparts_dict: The control parts dictionary.
    :param str origination: The origination of the implementation.
    """

    # Compliance settings groups are too inconsistent to auto map, so we need to manually map them
    status_map = {
        ControlImplementationStatus.FullyImplemented.value: "Implemented",
        ControlImplementationStatus.PartiallyImplemented.value: ControlImplementationStatus.PartiallyImplemented.value,
        ControlImplementationStatus.NA.value: ControlImplementationStatus.NA.value,
        ControlImplementationStatus.NotImplemented.value: ControlImplementationStatus.NotImplemented.value,
        "Planned": "Planned",
    }

    control_parts_string_from_mdict = mdparts_dict.get(control.controlId) if mdparts_dict else None
    parts_dict = extract_parts(content=control_parts_string_from_mdict)
    control_objectives = ControlObjective.get_by_control(control_id=control.id)
    imp_objectives: List[ImplementationObjective] = []
    for index, part in enumerate(parts):
        logger.debug(f"Part: {part.get('name')}")
        if part.get("value") == "":
            continue
        logger.debug(f"Control: {control.controlId} Part: {part.get('name')}")
        part_dict = extract_parts(control_parts_string_from_mdict)
        part_name = part.get("name", "")
        logger.debug(f"Part Name: {part_name}")
        part_letter = get_part_letter(part_name)
        logger.debug(f"Part Letter: {part_letter}")
        part_statement = part_dict.get(f"Part {part_letter}", parts_dict.get("default"))
        logger.debug(f"Control Id: {control.controlId}")
        multiple_control_objectives = len(control_objectives) > 1
        matching_objectives = (
            [o for o in control_objectives if o.name.replace("(", "").startswith(part_letter)]
            if multiple_control_objectives
            else control_objectives
        )
        logger.debug(f"Matching Objectives: {matching_objectives}")
        if RegscaleVersion.meets_minimum_version("6.13.0.0"):
            status = status_map.get(status, status)

        # Status should never be None
        if status is None:
            error_and_exit("Status should never be None.")

        handle_matching_objectives(
            matching_objectives=matching_objectives,
            part=part,
            control=control,
            control_implementation=control_implementation,
            status=status_map.get(status, status),
            imp_objectives=imp_objectives,
            origination=map_responsibility(origination),
            new_statement=part_statement or None,
        )
    ImplementationObjective.batch_create(items=imp_objectives)


def handle_matching_objectives(
    matching_objectives: List[ControlObjective],
    part: Dict,
    control: SecurityControl,
    control_implementation: ControlImplementation,
    status: Optional[str],
    imp_objectives: List[ImplementationObjective],
    origination: Optional[str] = None,
    new_statement: Optional[str] = None,
):
    """
    Handle the matching objectives for the given part.
    :param List[ControlObjective] matching_objectives: The matching objectives.
    :param Dict part: The part to handle.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.
    :param Optional[str] status: The status of the implementation.
    :param List[ImplementationObjective] imp_objectives: The list of implementation objectives.
    :param Optional[str] origination: The origination of the implementation.
    :param Optional[str] new_statement: The new statement for the implementation.
    """
    statements_used = []
    for objective in matching_objectives:
        logger.info(f"Objective: {objective.id} - {objective.name} - {objective.securityControlId}")
        part_statement = f"{part.get('value', '')}" if not new_statement else new_statement
        statements_used.append(part_statement)

        has_existing_obj = check_for_existing_objective(
            control_implementation, objective, status, part_statement, origination
        )
        if has_existing_obj:
            continue
        duplicate = True if part_statement in statements_used else False
        handle_implementation_objectives(
            objective,
            part_statement,
            status,
            control_implementation,
            imp_objectives,
            control,
            duplicate,
            origination,
        )


def check_for_existing_objective(
    control_implementation: ControlImplementation,
    objective: ControlObjective,
    status: Optional[str],
    part_statement: str,
    origination: Optional[str] = None,
) -> bool:
    """
    Check for existing implementation objectives.
    :param ControlImplementation control_implementation: The control implementation object.
    :param ControlObjective objective: The control objective object.
    :param Optional[str] status: The status of the implementation.
    :param str part_statement: The part statement.
    :param Optional[str] origination: The origination of the implementation.
    :return: True if an existing implementation objective is found, False otherwise.
    :rtype: bool
    """
    status_map = {
        ControlImplementationStatus.FullyImplemented.value: "Implemented",
        ControlImplementationStatus.PartiallyImplemented.value: ControlImplementationStatus.PartiallyImplemented.value,
        ControlImplementationStatus.NA.value: ControlImplementationStatus.NA.value,
        ControlImplementationStatus.NotImplemented.value: ControlImplementationStatus.NotImplemented.value,
        ControlImplementationStatus.Planned.value: ControlImplementationStatus.Planned.value,
    }

    existing_objectives: List[ImplementationObjective] = ImplementationObjective.get_by_control(
        implementation_id=control_implementation.id
    )
    for existing_obj in existing_objectives:
        if existing_obj.objectiveId == objective.id:
            if status:
                if isinstance(status, ControlImplementationStatus):
                    status = status.value
                existing_obj.status = status_map.get(status, status)
            existing_obj.statement = part_statement
            if origination is not None:
                existing_obj.responsibility = origination
            existing_obj.parentObjectiveId = objective.id
            existing_obj.save()
            return True
    return False


def map_responsibility(responsibility: str) -> str:
    """
    Map the responsibility to the appropriate value.
    :param str responsibility: The responsibility to map.
    :return: The mapped responsibility.
    :rtype: str
    """
    if not responsibility:
        return ""  # Return empty string instead of None

    # Handle comma-separated values
    if "," in responsibility:
        responsibility_values = [r.strip() for r in responsibility.split(",")]
        return ",".join([map_responsibility(r) for r in responsibility_values])

    # This should be server code with proper enums, but this is the best we can do for now
    responsibility_map = {
        "Service Provider Corporate": ImplementationControlOrigin.SERVICE_PROVIDER_CORPORATE.value,
        "Service Provider System Specific": ImplementationControlOrigin.SERVICE_PROVIDER_SYSTEM.value,
        "Service Provider Hybrid (Corporate and System Specific)": ImplementationControlOrigin.SERVICE_PROVIDER_HYBRID.value,  # Map to closest value
        "Configured by Customer (Customer System Specific)": ImplementationControlOrigin.CONFIGURED_BY_CUSTOMER.value,
        "Provided by Customer (Customer System Specific)": ImplementationControlOrigin.PROVIDED_BY_CUSTOMER.value,
        "Shared (Service Provider and Customer Responsibility)": ImplementationControlOrigin.SHARED.value,
        "Inherited from pre-existing FedRAMP Authorization": ImplementationControlOrigin.INHERITED_FROM_PRE_EXISTING_FEDRAMP_AUTHORIZATION.value,
    }

    return responsibility_map.get(responsibility, responsibility or "")


def handle_implementation_objectives(
    objective: ControlObjective,
    part_statement: str,
    status: Optional[str],
    control_implementation: Union[ControlImplementation, int, None],
    imp_objectives: List[ImplementationObjective],
    control: SecurityControl,
    duplicate: bool,
    origination: Optional[str] = None,
):
    """
    Handle the implementation objectives for the given objective, option, and control implementation.
    :param ControlObjective objective: The control objective.
    :param str part_statement: The statement text for this part.
    :param Optional[str] status: The implementation status.
    :param Union[ControlImplementation, int, None] control_implementation: The control implementation object or ID.
    :param List[ImplementationObjective] imp_objectives: List to collect implementation objectives.
    :param SecurityControl control: The security control.
    :param bool duplicate: Whether the option is a duplicate will add note if True.
    :param Optional[str] origination: The origination of the implementation.
    """
    if isinstance(status, ControlImplementationStatus):
        status = status.value

    # Ensure part_statement is valid
    statement = part_statement if part_statement else ""

    imp_obj = ImplementationObjective(
        securityControlId=control.id,
        implementationId=control_implementation.id if hasattr(control_implementation, "id") else control_implementation,
        objectiveId=objective.id,
        optionId=None,
        status=status,
        statement=statement,
        notes="#replicated-data-part" if duplicate else "",
        responsibility=origination,
    )
    if imp_obj not in imp_objectives:
        imp_objectives.append(imp_obj)


def add_implementation_to_list(objective: ImplementationObjective, implementation_list: List[ImplementationObjective]):
    """
    Add the implementation objective to the list.
    :param ImplementationObjective objective: The implementation objective to add.
    :param List[ImplementationObjective] implementation_list: The list of implementation objectives.
    """
    if objective not in implementation_list:
        implementation_list.append(objective)


def get_matching_objectives(control_objectives: List[ControlObjective], part_name: str) -> List[ControlObjective]:
    """
    Find and return the control objectives that match the specified part name.
    :param List[ControlObjective] control_objectives: The list of control objectives to search.
    :param str part_name: The part name to match.
    :return: A list of control objectives that match the specified part name.
    :rtype: List[ControlObjective]
    """
    matching_objectives = []
    try:
        matching_objectives = get_objectives_by_matching_property(
            control_objectives=control_objectives, property_name="name", part_letter=get_part_letter(part_name)
        )
    except Exception as e:
        logger.warning(f"Error finding matching objectives: {e}")
    return matching_objectives


def get_part_letter(part: str) -> str:
    """
    Get the part letter from the part name.
    :param str part: The part name.
    :return: The part letter.
    :rtype: str
    """
    return part.lower().replace("part", "").strip()  # Assuming the format "Part X" where X is the part letter.


def get_objectives_by_matching_property(
    control_objectives: List[ControlObjective], property_name: str, part_letter: str
) -> List[ControlObjective]:
    """
    Find and return the control objectives that match the specified property name.
    :param List[ControlObjective] control_objectives: The list of control objectives to search.
    :param str property_name: The property name to match.
    :param str part_letter: The part letter to match.
    :return: A list of control objectives that match the specified property name.
    :rtype: List[ControlObjective]
    """
    matching_objectives = []
    try:
        matching_objectives = [
            o for o in control_objectives if part_letter.lower() in getattr(o, property_name).lower()
        ]
    except Exception as e:
        logger.warning(f"Error finding matching objectives: {e}")
    return matching_objectives


def handle_params(
    parameters: List[Dict],
    control: SecurityControl,
    control_implementation: ControlImplementation,
):
    """
    Handle the parameters for the given control and control implementation.
    :param List[Dict] parameters: The parameters to handle.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.

    """
    # Log the initial handling of parameters for the given control.
    logger.info(f"Handling Parameters for Control: {control.id} - {len(parameters)}")
    param_mapper = RosettaStone()
    if not param_mapper.map:
        param_mapper.load_fedramp_version_5_mapping()
        param_mapper.lookup_l0_by_l1()
    mappings = param_mapper.map
    base_control_params = ControlParameter.get_by_control(control_id=control.id)
    base_control_params_dict = {param.otherId: param for param in base_control_params}
    for param in parameters:
        gen_param_name = f"Parameter {param.get('name').replace(' ', '')}"
        if gen_param_name not in mappings:
            logger.debug(f"Parameter: {gen_param_name} not found in mappings")
        logger.info(gen_param_name)
        control_param_name = mappings.get(gen_param_name)
        base_control_param = base_control_params_dict.get(control_param_name)

        if base_control_param:
            existing_params = Parameter.get_by_parent_id(parent_id=control_implementation.id)
            existing_param_names_dict = {param.name: param for param in existing_params}
            existing_parameter = existing_param_names_dict.get(control_param_name)
            existing_param_by_external_name_dict = {param.externalPropertyName: param for param in existing_params}
            if not existing_parameter:
                existing_parameter = existing_param_by_external_name_dict.get(control_param_name)
            try:
                if not existing_params or not existing_parameter:
                    Parameter(
                        controlImplementationId=control_implementation.id,
                        name=param.get("name").strip(),
                        value=param.get("value"),
                        externalPropertyName=base_control_param.otherId,
                        parentParameterId=base_control_param.id,
                    ).create()
                else:
                    existing_param = existing_parameter
                    if existing_param.name == control_param_name:
                        existing_param.value = param.get("value")
                        existing_param.parentParameterId = base_control_param.id
                        existing_param.save()
            except Exception as e:
                logger.warning(f"warning handling parameter: {e}")
        else:
            logger.warning(f"Param: {gen_param_name} not found: {control_param_name}")


def build_params(base_control_params: List[ControlParameter], parameters: List[Dict]) -> List[Dict]:
    """
    Builds the parameters for the control implementation.
    :param List[ControlParameter] base_control_params: The base control parameters.
    :param List[Dict] parameters: The parameters to build.
    :return: List[Dict]: The built parameters.
    :rtype: List[Dict]
    """
    new_params = []
    if len(base_control_params) >= len(parameters):
        for index, base_param in enumerate(base_control_params):
            if len(parameters) >= index + 1:
                new_param_dict = {}
                new_param_dict["name"] = base_param.parameterId
                new_param_dict["value"] = parameters[index].get("value") if parameters[index] else base_param.default
                new_params.append(new_param_dict)
    return new_params


def map_implementation_status(status: str) -> str:
    """
    Maps the implementation status to the appropriate value.
    :param str status: The status to map.
    :return: The mapped status.
    :rtype: str
    """

    if status and status.lower() == "implemented":
        return ControlImplementationStatus.Implemented.value
    elif status and status.lower() == "fully implemented":
        return ControlImplementationStatus.Implemented.value
    elif status and status.lower() == "partially implemented":
        return ControlImplementationStatus.PartiallyImplemented.value
    elif status and status.lower() == "planned":
        return ControlImplementationStatus.Planned.value
    elif status and status.lower() == "not applicable":
        return ControlImplementationStatus.NA.value
    elif status and status.lower() == "alternative implementation":
        return ControlImplementationStatus.FullyImplemented.value
    else:
        return ControlImplementationStatus.NotImplemented.value


def update_existing_control(
    control: ControlImplementation, status: str, statement: str, responsibility: str, primary_role: Dict, parent_id: int
):
    """
    Updates an existing control with new information.
    :param ControlImplementation control: The control implementation object.
    :param str status: The status of the implementation.
    :param str statement: The statement of the implementation.
    :param str responsibility: The responsibility of the implementation.
    :param Dict primary_role: The primary role of the implementation.
    :param int parent_id: The parent ID.
    """
    state_text = clean_statement(statement)
    justify = (
        state_text or "Unknown" if map_implementation_status(status) == ControlImplementationStatus.NA.value else None
    )
    control.parentId = parent_id
    control.status = map_implementation_status(status)
    control.exclusionJustification = justify
    _, planned_date, steps_to_implement = create_control_implementation_defaults(status)
    if not control.plannedImplementationDate and planned_date:
        control.plannedImplementationDate = planned_date
    if not control.stepsToImplement and steps_to_implement:
        control.stepsToImplement = steps_to_implement
    control.implementation = state_text
    control.responsibility = map_responsibility(responsibility)
    control.systemRoleId = primary_role.get("id") if primary_role and isinstance(primary_role, dict) else None
    # Clean statement
    # So, exclusion
    # justification is required for "N/A"... "Planned" requires Planned Implementation Date and Steps to Implement....
    # the only other validation is: Needs "Implementation", "Cloud Implementation", or "Customer Responsibility" if "Implemented" or "Partially Implemented".

    # Convert the model to a dict and back to a model to workaround these odd 400 errors.
    try:
        control.save()
    except Exception as e:
        logger.warning(f"Error updating control: {control.id} - {e}")


def format_alternative_control_key(control_id: str) -> str:
    """
    Formats the key for the alternative control information.
    :param str control_id: The control ID to format.
    :return: The formatted control ID.
    :rtype: str
    """
    # Unpack the control_family and the rest (assumes there's at least one '-')
    control_family, *rest = control_id.split("-")
    rest_joined = "-".join(rest)  # Join the rest back in case there are multiple '-'

    # Check for '(' and split if needed, also handling the case without '(' more cleanly
    if "(" in rest_joined:
        control_num, control_ending = rest_joined.split("(", 1)  # Split once
        control_ending = control_ending.rstrip(")")  # Remove trailing ')' if present
        alternative_control_id = f"{control_family}-{format_int(int(control_num))}({control_ending})"
    else:
        control_num = rest_joined
        alternative_control_id = f"{control_family}-{format_int(int(control_num))}"

    return alternative_control_id


def format_int(n: int) -> str:
    """
    Formats an integer to a string with a leading zero if it's a single digit.
    :param int n: The integer to format.
    :return: The formatted integer as a string.
    :rtype: str
    """
    # Check if the integer is between 0 and 9 (inclusive)
    if 0 <= n <= 9:
        # Prepend a "0" if it's a single digit
        return f"0{n}"
    else:
        # Just convert to string if it's not a single digit
        return str(n)


def build_data_dict(tables: List) -> Dict:
    """
    Builds a dictionary from a list of tables.

    :param List tables: A list of tables.
    :return: A dictionary containing the tables.
    :rtype: Dict
    """
    table_dict = {}
    for table in tables:
        k_parts = list(table.keys())[0].split()
        if k_parts:
            key_control = k_parts[0]
            if key_control in table_dict:
                table_dict[key_control].append(table)
            else:
                table_dict[key_control] = [table]
    return table_dict


def processing_data_from_ssp_doc(processed_data, user_id, doc_text_dict: Dict) -> int:
    """
    Finalizes the processing of data by creating necessary records in the system.
    :param Dict[str, Any] processed_data: The processed data.
    :param str user_id: The ID of the user performing the operation.
    :param Dict[str, str] doc_text_dict: The dictionary containing the text from the document.
    :return: The ID of the parent object.
    :rtype: int
    """
    processed_data["doc_text_dict"] = doc_text_dict
    # Process SSP Document if present
    if not processed_data.get("ssp_doc"):
        logger.warning("No SSP Document found")
        sys.exit(1)
    ssp = process_ssp_doc(
        processed_data.get("ssp_doc"),
        processed_data,
        user_id,
    )
    parent_id = ssp.id
    logger.info(f"Parent ID: {parent_id}")
    parent_module = "securityplans"
    approval_date = ssp.approvalDate

    # Create stakeholders
    if processed_data.get("stakeholders"):
        create_stakeholders(processed_data.get("stakeholders"), parent_id, parent_module)
    # Process services if present
    if processed_data.get("services"):
        create_leveraged_authorizations(
            processed_data["services"], user_id, parent_id, approval_date
        )  # Assuming parent_id is the ssp_id for simplicity

    # Process ports and protocols if present
    if processed_data.get("ports_and_protocols"):
        create_ports_and_protocols(
            processed_data["ports_and_protocols"], parent_id
        )  # Assuming parent_id is the ssp_id for simplicity
    return parent_id


def create_stakeholders(stakeholders: List[Person], parent_id: int, parent_module: str) -> None:
    """
    Creates stakeholders in RegScale.
    :param List[Person] stakeholders: A list of Person objects representing the stakeholders.
    :param int parent_id: The ID of the parent object.
    :param str parent_module: The parent module.

    """
    logger.info(f"Creating Stakeholders: {parent_id} - {parent_module}")
    existing_stakeholders: List[StakeHolder] = StakeHolder.get_all_by_parent(
        parent_id=parent_id, parent_module=parent_module
    )
    for person in stakeholders:
        existing_stakeholder = next(
            (s for s in existing_stakeholders if s.name == person.name and s.email == person.email),
            None,
        )
        if existing_stakeholder:
            logger.debug(existing_stakeholder.model_dump())
            existing_stakeholder.name = person.name
            existing_stakeholder.email = person.email
            existing_stakeholder.phone = person.phone
            existing_stakeholder.title = person.title
            existing_stakeholder.save()
        else:
            StakeHolder(
                name=person.name,
                email=person.email,
                phone=person.phone,
                title=person.title,
                parentId=parent_id,
                parentModule=parent_module,
            ).create()


def process_cloud_info(ssp_doc: SSPDoc) -> Dict:
    """
    Processes the cloud information from the SSP document.
    :param SSPDoc ssp_doc: The SSP document object.
    :return: A dictionary containing the cloud deployment model information.
    :rtype: Dict
    """
    return {
        "saas": "SaaS" in ssp_doc.service_model,
        "paas": "PaaS" in ssp_doc.service_model,
        "iaas": "IaaS" in ssp_doc.service_model,
        "other_service_model": not any(service in ssp_doc.service_model for service in ["SaaS", "PaaS", "IaaS"]),
        "deploy_gov": "gov" in ssp_doc.deployment_model.lower() or "government" in ssp_doc.deployment_model.lower(),
        "deploy_hybrid": "hybrid" in ssp_doc.deployment_model.lower(),
        "deploy_private": "private" in ssp_doc.deployment_model.lower(),
        "deploy_public": "public" in ssp_doc.deployment_model.lower(),
        "deploy_other": not any(
            deploy in ssp_doc.deployment_model.lower()
            for deploy in ["gov", "government", "hybrid", "private", "public"]
        ),
    }


def process_ssp_doc(
    ssp_doc: SSPDoc,
    data: Dict,
    user_id: str,
) -> SecurityPlan:
    """
    Processes the SSP document.
    :param SSPDoc ssp_doc: The SSP document object.
    :param Dict[str, Any] data: The processed data.
    :param str user_id: The ID of the user performing the operation.
    :return: The security plan object.
    :rtype: SecurityPlan
    """
    if ssp_doc:
        cloud_info = process_cloud_info(ssp_doc)
        plans = SecurityPlan.get_list()
        plan_count = len(plans)
        logger.info(f"Found SSP Count of: {plan_count}")
        ssp = None
        for plan in plans:
            if plan.systemName == ssp_doc.name:
                ssp = SecurityPlan.get_object(object_id=plan.id)
                logger.info(f"Found SSP: {plan.systemName}")
                break
        if not ssp:
            ssp = create_ssp(ssp_doc, cloud_info, user_id, data)
        else:
            ssp = save_security_plan_info(ssp, cloud_info, ssp_doc, user_id, data)
        return ssp


def get_expiration_date(dt_format: Optional[str] = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Return the expiration date, which is 3 years from today

    :param Optional[str] dt_format: desired format for datetime string, defaults to "%Y-%m-%d %H:%M:%S"
    :return: Expiration date as a string, 3 years from today
    :rtype: str
    """
    expiration_date = datetime.datetime.now() + relativedelta(years=3)
    return expiration_date.strftime(dt_format)


def create_ssp(ssp_doc: SSPDoc, cloud_info: Dict, user_id: str, data: Dict) -> SecurityPlan:
    """
    Creates a security plan in RegScale.
    :param SSPDoc ssp_doc: The SSP document object.
    :param Dict cloud_info: A dictionary containing cloud deployment model information.
    :param str user_id: The ID of the user creating the security plan.
    :param Dict[str, Any] data: The processed data.
    :return: The security plan object.
    :rtype: SecurityPlan
    """
    compliance_setting = get_fedramp_compliance_setting()
    doc_text_dict = data.get("doc_text_dict")

    systemdescription = " ".join(doc_text_dict[SYSTEM_DESCRIPTION]) if SYSTEM_DESCRIPTION in doc_text_dict else None
    authboundarydescription = (
        " ".join(doc_text_dict[AUTHORIZATION_BOUNDARY]) if AUTHORIZATION_BOUNDARY in doc_text_dict else None
    )
    networkarchdescription = (
        " ".join(doc_text_dict[NETWORK_ARCHITECTURE]) if NETWORK_ARCHITECTURE in doc_text_dict else None
    )
    systemenvironment = " ".join(doc_text_dict[ENVIRONMENT]) if ENVIRONMENT in doc_text_dict else None
    dataflows = " ".join(doc_text_dict[DATA_FLOW]) if DATA_FLOW in doc_text_dict else None
    owner, isso = data.get("owner"), data.get("isso")
    prepared_by: PreparedBy = data.get("prepared_by")
    prepared_for: PreparedBy = data.get("prepared_for")
    compliance_setting_id = compliance_setting.id if compliance_setting else 2
    ssp = SecurityPlan(
        systemName=ssp_doc.name,
        fedrampId=ssp_doc.fedramp_id,
        systemOwnerId=owner.id if owner else user_id,
        planInformationSystemSecurityOfficerId=isso.id if isso else user_id,
        status="Operational",
        description=systemdescription,
        authorizationBoundary=authboundarydescription,
        networkArchitecture=networkarchdescription,
        environment=systemenvironment,
        dataFlow=dataflows,
        tenantsId=1,
        overallCategorization=ssp_doc.fips_199_level,
        bModelSaaS=cloud_info.get("saas", False),
        bModelPaaS=cloud_info.get("paas", False),
        bModelIaaS=cloud_info.get("iaas", False),
        bModelOther=cloud_info.get("other_service_model", False),
        bDeployGov=cloud_info.get("deploy_gov", False),
        bDeployHybrid=cloud_info.get("deploy_hybrid", False),
        bDeployPrivate=cloud_info.get("deploy_private", False),
        bDeployPublic=cloud_info.get("deploy_public", False),
        bDeployOther=cloud_info.get("deploy_other", False),
        deployOtherRemarks=ssp_doc.deployment_model,
        dateSubmitted=ssp_doc.date_submitted,
        approvalDate=ssp_doc.approval_date,
        expirationDate=get_expiration_date(),
        fedrampAuthorizationLevel=ssp_doc.fips_199_level,
        defaultAssessmentDays=365,
        version=data.get("version", "1.0"),
        executiveSummary="\n".join(doc_text_dict.get("Introduction", [])),
        purpose="\n".join(doc_text_dict.get("Purpose", [])),
        complianceSettingsId=compliance_setting_id,
    )
    if prepared_by:
        ssp.cspOrgName = prepared_by.name
        ssp.cspAddress = prepared_by.street
        ssp.cspOffice = prepared_by.building
        ssp.cspCityState = prepared_by.city_state_zip
    if prepared_for:
        ssp.prepOrgName = prepared_for.name
        ssp.prepAddress = prepared_for.street
        ssp.prepOffice = prepared_for.building
        ssp.prepCityState = prepared_for.city_state_zip
    return ssp.create()


def save_security_plan_info(
    ssp: SecurityPlan, cloud_info: Dict, ssp_doc: SSPDoc, user_id: str, data: Dict
) -> SecurityPlan:
    """
    Saves the security plan information to the database.
    :param SecurityPlan ssp: The security plan object.
    :param Dict cloud_info: A dictionary containing cloud deployment model information.
    :param SSPDoc ssp_doc: The SSP document object.
    :param str user_id: The ID of the user performing the operation.
    :param Dict[str, Any] data: The processed data.
    :return: The updated security plan object.
    :rtype: SecurityPlan
    """
    prepared_by: PreparedBy = data.get("prepared_by")
    prepared_for: PreparedBy = data.get("prepared_for")
    doc_text_dict: Dict = data.get("doc_text_dict")
    owner, isso = data.get("owner"), data.get("isso")

    logger.info(f"Updating SSP: {ssp.systemName}")
    ssp.fedrampId = ssp_doc.fedramp_id
    ssp.systemName = ssp_doc.name
    ssp.status = "Operational"
    ssp.description = ssp_doc.description
    ssp.authorizationBoundary = ssp_doc.authorization_path
    ssp.systemOwnerId = owner.id if owner else user_id
    ssp.planInformationSystemSecurityOfficerId = isso.id if isso else user_id
    ssp.overallCategorization = ssp_doc.fips_199_level
    ssp.bModelSaaS = cloud_info.get("saas", False)
    ssp.bModelPaaS = cloud_info.get("paas", False)
    ssp.bModelIaaS = cloud_info.get("iaas", False)
    ssp.bModelOther = cloud_info.get("other_service_model", False)
    ssp.bDeployGov = cloud_info.get("deploy_gov", False)
    ssp.bDeployHybrid = cloud_info.get("deploy_hybrid", False)
    ssp.bDeployPrivate = cloud_info.get("deploy_private", False)
    ssp.bDeployPublic = cloud_info.get("deploy_public", False)
    ssp.bDeployOther = cloud_info.get("deploy_other", False)
    ssp.deployOtherRemarks = ssp_doc.deployment_model
    ssp.dateSubmitted = ssp_doc.date_submitted
    ssp.approvalDate = ssp_doc.approval_date
    ssp.expirationDate = get_expiration_date()  # ssp_doc.expiration_date
    ssp.fedrampAuthorizationLevel = ssp_doc.fips_199_level
    ssp.version = data.get("version", "1.0")
    if prepared_by:
        ssp.cspOrgName = prepared_by.name
        ssp.cspAddress = prepared_by.street
        ssp.cspOffice = prepared_by.building
        ssp.cspCityState = prepared_by.city_state_zip
    if prepared_for:
        ssp.prepOrgName = prepared_for.name
        ssp.prepAddress = prepared_for.street
        ssp.prepOffice = prepared_for.building
        ssp.prepCityState = prepared_for.city_state_zip

    ssp.executiveSummary = "\n".join(doc_text_dict.get("Introduction", []))
    ssp.purpose = "\n".join(doc_text_dict.get("Purpose", []))
    ssp.save()
    return ssp


def create_leveraged_authorizations(services: List[LeveragedService], user_id: str, ssp_id: int, approval_date: str):
    """
    Creates leveraged authorization records for each service.

    :param List[LeveragedService] services: A list of services to be created.
    :param str user_id: The ID of the user creating the services.
    :param int ssp_id: The ID of the security plan these services are associated with.
    :param str approval_date: The date of approval.

    """
    existing_authorizations: List[LeveragedAuthorization] = LeveragedAuthorization.get_all_by_parent(parent_id=ssp_id)
    logger.info(f"Found {len(existing_authorizations)} existing LeveragedAuthorizations")
    for service in services:
        existing_service = next(
            (a for a in existing_authorizations if a.fedrampId == service.auth_type_fedramp_id),
            None,
        )

        if existing_service:
            logger.debug(existing_service.model_dump())
            existing_service.title = service.fedramp_csp_name
            existing_service.fedrampId = service.auth_type_fedramp_id
            existing_service.ownerId = user_id
            existing_service.securityPlanId = ssp_id
            existing_service.dateAuthorized = approval_date or get_current_datetime()
            existing_service.description = service.cso_name
            existing_service.dataTypes = service.data_types or "unknown"
            existing_service.authorizedUserTypes = service.authorized_user_authentication or "unknown"
            existing_service.impactLevel = service.impact_level
            existing_service.natureOfAgreement = service.agreement_type or "unknown"
            existing_service.tenantsId = 1
            existing_service.save()
        else:
            LeveragedAuthorization(
                title=service.fedramp_csp_name,
                fedrampId=service.auth_type_fedramp_id or "unknown",
                ownerId=user_id,
                securityPlanId=ssp_id,
                dateAuthorized=approval_date or get_current_datetime(),
                servicesUsed="unknown",
                description=service.cso_name,
                dataTypes=service.data_types or "unknown",
                authorizationType="SSO",
                authorizedUserTypes=service.authorized_user_authentication or "unknown",
                authenticationType="unknown",
                impactLevel=service.impact_level or "Low",
                natureOfAgreement=service.agreement_type or "unknown",
                tenantsId=1,
            ).create()
            logger.debug(f"LeveragedAuthorization: {service.fedramp_csp_name}")


def create_ports_and_protocols(ports_and_protocols: List[PortsAndProtocolData], ssp_id: int):
    """
    Creates port and protocol records for each entry.

    :param List[PortsAndProtocolData] ports_and_protocols: A list of ports and protocols to be created.
    :param int ssp_id: The ID of the security plan these ports and protocols are associated with.

    """
    existing_ports: List[PortsProtocol] = PortsProtocol.get_all_by_parent(
        parent_id=ssp_id, parent_module="securityplans"
    )
    logger.info(f"Found {len(existing_ports)} existing Ports & Protocols")
    created_count = 0
    for port in ports_and_protocols:
        port_to_create = PortsProtocol(
            service=port.service,
            startPort=port.start_port,
            endPort=port.end_port,
            protocol=port.protocol,
            purpose=port.purpose,
            usedBy=port.used_by,
            parentId=ssp_id,
            parentModule="securityplans",
        )
        existing = False
        for existing_port in existing_ports:
            if (
                existing_port.startPort == port_to_create.startPort
                and existing_port.endPort == port_to_create.endPort
                and existing_port.protocol == port_to_create.protocol
                and existing_port.service == port_to_create.service
                and existing_port.purpose == port_to_create.purpose
                and existing_port.usedBy == port_to_create.usedBy
                and existing_port.parentId == port_to_create.parentId
                and existing_port.parentModule == port_to_create.parentModule
            ):
                existing = True
                break

        if not existing:
            port_to_create.create()
            created_count += 1
    logger.info(f"Created {created_count} Port & Protocols")


def extract_and_upload_images(file_name: str, parent_id: int) -> None:
    """
    Extracts embedded images from a document and uploads them to RegScale with improved filenames.

    :param str file_name: The path to the document file.
    :param int parent_id: The parent ID in RegScale to associate the images with.

    """
    logger.debug(f"Processing embedded images in {file_name} for parent ID {parent_id}...")
    existing_files = fetch_existing_files(parent_id)
    extracted_files_path = extract_embedded_files(file_name)
    upload_files(extracted_files_path, existing_files, parent_id)


def fetch_existing_files(parent_id: int) -> list:
    """
    Fetches existing files for a given parent ID from RegScale.

    :param int parent_id: The parent ID whose files to fetch.
    :return: A list of existing files.
    :rtype: list
    """
    return File.get_files_for_parent_from_regscale(parent_id=parent_id, parent_module="securityplans")


def extract_embedded_files(file_name: str) -> str:
    """
    Extracts embedded files from a document and returns the path where they are stored.

    :param str file_name: The path to the document file.
    :return: The path where embedded files are extracted to.
    :rtype: str
    """
    file_dump_path = os.path.join(gettempdir(), "imagedump")
    with zipfile.ZipFile(file_name, mode="r") as archive:
        for file in archive.filelist:
            logger.debug(f"Extracting file: {file.filename}")
            if file.filename.startswith("word/media/") and file.file_size > 200000:  # 200KB filter
                archive.extract(file, path=file_dump_path)
    return file_dump_path


def upload_files(extracted_files_path: str, existing_files: list, parent_id: int) -> None:
    """
    Uploads files from a specified path to RegScale, avoiding duplicates.

    :param str extracted_files_path: The path where files are stored.
    :param list existing_files: A list of files already existing in RegScale to avoid duplicates.
    :param int parent_id: The parent ID in RegScale to associate the uploaded files with.

    """
    media_path = os.path.join(extracted_files_path, "word", "media")
    if not os.path.exists(media_path):
        os.makedirs(media_path)

    for filename in os.listdir(media_path):
        full_file_path = os.path.join(media_path, filename)
        if os.path.isfile(full_file_path):
            if not file_already_exists(filename, existing_files):
                logger.info(f"Uploading embedded image to RegScale: {filename}")
                upload_file_to_regscale(full_file_path, parent_id)


def file_already_exists(filename: str, existing_files: list) -> bool:
    """
    Checks if a file already exists in RegScale.

    :param str filename: The name of the file to check.
    :param list existing_files: A list of files already existing in RegScale.
    :return: True if the file exists, False otherwise.
    :rtype: bool
    """
    return any(f.trustedDisplayName == filename for f in existing_files)


def upload_file_to_regscale(
    file_path: str,
    parent_id: int,
) -> None:
    """
    Uploads a single file to RegScale.

    :param str file_path: The full path to the file to upload.
    :param int parent_id: The parent ID in RegScale to associate the file with.
    """
    api = Api()
    File.upload_file_to_regscale(
        file_name=file_path,
        parent_id=parent_id,
        parent_module=SecurityPlan.get_module_slug(),
        api=api,
    )


def safe_get_first_key(dictionary: dict) -> Optional[str]:
    """Safely get the first key of a dictionary.
    :param dict dictionary: The dictionary to get the first key from.
    :return: The first key of the dictionary, or None if the dictionary is empty.
    :rtype: Optional[str]
    """
    try:
        return next(iter(dictionary))
    except StopIteration:
        return None


def parse_version(version_str: str) -> float:
    """Parse version string to a float, safely.
    :param str version_str: The version string to parse.
    :return: The version number as a float, or 0 if the version string is not a valid number.
    :rtype: float
    """
    try:
        if not version_str:
            return 0
        return float(version_str)
    except ValueError:
        return 0


def get_max_version(entries: List[Dict]) -> Optional[str]:
    """Find the maximum version from a list of entries.
    :param List[Dict] entries: The list of entries to find the maximum version from.
    :return: The maximum version from the entries, or None if no valid versions are found.
    :rtype: Optional[str]
    """
    max_version = None
    for entry in entries:
        version_str = entry.get("Version", "")
        version_num = parse_version(version_str)
        if version_num is not None:
            max_version = max(max_version, version_str, key=parse_version)
    logger.debug(f"Version: {max_version}")
    return max_version


def process_objective(
    objective: ControlObjective,
    processed_objective_ids: set,
    existing_objectives_by_objective_id: Dict,
    control: SecurityControl,
    part_statement: Optional[str],
    status: Optional[str],
    origination: Optional[str] = None,
    imp_objectives: List[ImplementationObjective] = None,
):
    """
    Process a single control objective.

    :param ControlObjective objective: The objective to process.
    :param set processed_objective_ids: Set of already processed objective IDs.
    :param Dict existing_objectives_by_objective_id: Dictionary of existing objectives by ID.
    :param SecurityControl control: The security control.
    :param Optional[str] part_statement: The statement for this part, may be None.
    :param Optional[str] status: The implementation status for this objective.
    :param Optional[str] origination: The implementation origination for this objective.
    :param List[ImplementationObjective] imp_objectives: List to collect implementation objectives.
    :return: None
    """
    logger.debug(f"Processing objective: {objective.id} - {objective.name}")

    # Skip if already processed
    if objective.id in processed_objective_ids:
        logger.debug(f"Objective {objective.id} already processed")
        return

    processed_objective_ids.add(objective.id)
    existing_objective = existing_objectives_by_objective_id.get(objective.id)

    statement = part_statement if part_statement is not None else ""

    # Update existing objective if found
    if existing_objective is not None:
        logger.debug(f"Updating existing objective: {existing_objective.id}")
        existing_objective.status = status
        existing_objective.statement = statement
        if origination is not None:
            existing_objective.responsibility = origination
        existing_objective.save()
    # Create new objective if implementation objectives list provided
    elif imp_objectives is not None:
        logger.debug(f"Creating new objective for {objective.id}")
        imp_obj = ImplementationObjective(
            objectiveId=objective.id,
            status=status,
            statement=statement,
            responsibility=origination,
        )
        imp_objectives.append(imp_obj)
