"""
Wiz V2 Utils
"""

import codecs
import csv
import datetime
import json
import logging
import time
import traceback
from contextlib import closing
from typing import Dict, List, Any, Optional, Union
from zipfile import ZipFile

import cachetools
import requests
from pydantic import ValidationError
from rich.progress import Progress, TaskID

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    error_and_exit,
    check_file_path,
    get_current_datetime,
    create_progress_object,
)
from regscale.core.utils.date import datetime_obj
from regscale.integrations.commercial.cpe import extract_product_name_and_version
from regscale.integrations.commercial.wizv2.constants import (
    BEARER,
    CHECK_INTERVAL_FOR_DOWNLOAD_REPORT,
    CONTENT_TYPE,
    CPE_PART_TO_CATEGORY_MAPPING,
    CREATE_REPORT_QUERY,
    DOWNLOAD_QUERY,
    MAX_RETRIES,
    RATE_LIMIT_MSG,
    REPORTS_QUERY,
    RERUN_REPORT_QUERY,
)
from regscale.models.integration_models.wizv2 import ComplianceReport, ComplianceCheckStatus
from regscale.integrations.commercial.wizv2.variables import WizVariables
from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
from regscale.models import (
    File,
    Sbom,
    SecurityControl,
    SecurityPlan,
    Catalog,
    ControlImplementation,
    Assessment,
    regscale_models,
    ControlImplementationStatus,
    ImplementationObjective,
)
from regscale.models.regscale_models.compliance_settings import ComplianceSettings
from regscale.utils import PaginatedGraphQLClient
from regscale.utils.decorators import deprecated

logger = logging.getLogger("regscale")
compliance_job_progress = create_progress_object()


def is_report_expired(report_run_at: str, max_age_days: int) -> bool:
    """
    Check if a report is expired based on its run date

    :param str report_run_at: Report run date in ISO format
    :param int max_age_days: Maximum age in days
    :return: True if report is expired, False otherwise
    :rtype: bool
    """
    try:
        run_date = datetime_obj(report_run_at)
        if not run_date:
            return True

        # Convert to naive datetime for comparison
        run_date_naive = run_date.replace(tzinfo=None)
        current_date = datetime.datetime.now()
        age_in_days = (current_date - run_date_naive).days

        return age_in_days >= max_age_days
    except (ValueError, TypeError):
        # If we can't parse the date, consider it expired
        return True


def get_notes_from_wiz_props(wiz_entity_properties: Dict, external_id: str) -> str:
    """
    Get notes from wiz properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :param str external_id: External ID
    :return: Notes
    :rtype: str
    """
    # Define property mappings with display names and keys
    property_mappings = [
        ("External ID", lambda: external_id, lambda x: x),
        ("Cloud Platform", "cloudPlatform", str),
        ("Provider Unique ID", "providerUniqueId", str),
        ("cloudProviderURL", "cloudProviderURL", lambda x: f'<a href="{x}" target="_blank">{x}</a>'),
        ("Vertex ID", "_vertexID", str),
        ("Severity Name", "severity_name", str),
        ("Severity Description", "severity_description", str),
    ]

    notes = []
    for display_name, key_or_func, formatter in property_mappings:
        # Handle external_id special case
        if callable(key_or_func):
            value = key_or_func()
        else:
            value = wiz_entity_properties.get(key_or_func)

        if value:
            formatted_value = formatter(value)
            notes.append(f"{display_name}: {formatted_value}")

    return "<br>".join(notes)


def handle_management_type(wiz_entity_properties: Dict) -> str:
    """
    Handle management type
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Management type
    :rtype: str
    """
    return "External/Third Party Managed" if wiz_entity_properties.get("isManaged") else "Internally Managed"


@cachetools.cached(cachetools.TTLCache(maxsize=1024, ttl=3600))
def create_asset_type(asset_type: str) -> str:
    """
    Create asset type if it does not exist and reformat the string to Title Case ie
        ( "ASSET_TYPE" or "asset_type" -> "Asset Type")
    :param asset_type str Asset_type
    :return: Asset type
    :rtype: str
    """
    asset_type = asset_type.title().replace("_", " ")
    meta_data_list = regscale_models.Metadata.get_metadata_by_module_field(module="assets", field="Asset Type")
    if not any(meta_data.value == asset_type for meta_data in meta_data_list):
        regscale_models.Metadata(
            field="Asset Type",
            module="assets",
            value=asset_type,
        ).create()
    return asset_type


def map_category(node: dict[str, Any]) -> regscale_models.AssetCategory:
    """
    Map the asset category based on the given node. The node should be a CloudResoruce response from
    the Wiz inventory query.

    If the CloudResource type or any of the technologies deploymentModel entries match those in the
    config parameter wizHardwareAssetTypes, "Hardware" will be returned, otherwise "Software".

    :param dict[str, Any] node: A single node results from the Wiz CloudResource invenotty query.
        It should have a 'type' key with the string asset type and a 'graphEntity' eky with a dict
        which, in turn, has a 'technologies' key whose value is a dict with a 'deploymentModel' key
        with a string value.
    :return: RegScale AssetCategory
    :rtype: regscale_models.AssetCategory
    """

    # First check if there is a CPE which can tell us the category directly.
    cpe = node.get("graphEntity", {}).get("properties", {}).get("cpe", "")
    cpe_part = extract_product_name_and_version(cpe).get("part", "")
    if cpe_part and cpe_part.lower() in CPE_PART_TO_CATEGORY_MAPPING:
        return CPE_PART_TO_CATEGORY_MAPPING[cpe_part]

    # Then try mapping by the configured Wiz hardware asset and technology deployment model types.
    asset_type = node.get("type", "")
    if WizVariables.useWizHardwareAssetTypes:
        if asset_type in WizVariables.wizHardwareAssetTypes:
            return regscale_models.AssetCategory.Hardware
        if (graph_entity := node.get("graphEntity", {})) and (techs := graph_entity.get("technologies", [])):
            for tech in techs:
                # We double check just in case we get an explicit None for the technologies.
                if tech and tech.get("deploymentModel", None) in WizVariables.wizHardwareAssetTypes:
                    return regscale_models.AssetCategory.Hardware
        else:
            logger.debug("No graphEntity set for node %r, default to Software.", node)

    # Finally try matching the asset type directly by name.
    if hasattr(regscale_models.AssetCategory, asset_type):
        if asset_category := getattr(regscale_models.AssetCategory, asset_type):
            return asset_category
        logger.debug("Unknown AssetType %r for node %r. Defaulting to Software.", asset_type, node)

    # If all else fails, default to software.
    return regscale_models.AssetCategory.Software


def convert_first_seen_to_days(first_seen: str) -> int:
    """
    Converts the first seen date to days
    :param str first_seen: First seen date
    :returns: Days
    :rtype: int
    """
    first_seen_date = datetime_obj(first_seen)
    if not first_seen_date:
        return 0
    first_seen_date_naive = first_seen_date.replace(tzinfo=None)
    return (datetime.datetime.now() - first_seen_date_naive).days


def fetch_report_by_id(
    report_id: str, parent_id: int, report_file_name: str = "evidence_report", report_file_extension: str = "csv"
):
    """
    Fetch report by id and add it to evidence

    :param str report_id: Wiz report ID
    :param int parent_id: RegScale Parent ID
    :param str report_file_name: Report file name, defaults to "evidence_report"
    :param str report_file_extension: Report file extension, defaults to "csv"
    :rtype: None
    """

    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file_path = f"artifacts/{report_file_name}_{current_datetime}.{report_file_extension}"
    variables = {"reportId": report_id}
    api_endpoint_url = WizVariables.wizUrl
    token = WizVariables.wizAccessToken
    if not token:
        error_and_exit("Wiz Access Token is missing. Authenticate with Wiz first.")
    client = PaginatedGraphQLClient(
        endpoint=api_endpoint_url,
        query=DOWNLOAD_QUERY,
        headers={
            "Content-Type": "application/json",
            "Authorization": BEARER + token,
        },
    )
    downloaded_report = client.fetch_results(variables=variables)
    logger.debug(f"Download Report result: {downloaded_report}")
    if "errors" in downloaded_report:
        logger.error(f"Error fetching report: {downloaded_report['errors']}")
        logger.error(f"Raw Response Data: {downloaded_report}")
        return

    if download_url := downloaded_report.get("report", {}).get("lastRun", {}).get("url"):
        logger.info(f"Download URL: {download_url}")
        download_file(url=download_url, local_filename=report_file_path)
        api = Api()
        _ = File.upload_file_to_regscale(
            file_name=str(report_file_path),
            parent_id=parent_id,
            parent_module="evidence",
            api=api,
        )
        logger.info("File uploaded successfully")
    else:
        logger.error("Could not retrieve the download URL.")


def download_file(url, local_filename="artifacts/test_report.csv"):
    """
    Download a file from a URL and save it to the local file system.

    :param url: The URL of the file to download.
    :param local_filename: The local path where the file should be saved.
    :return: None
    """

    check_file_path("artifacts")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check if the request was successful
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                file.write(chunk)
    logger.info(f"File downloaded successfully and saved to {local_filename}")


def fetch_sbom_report(
    report_id: str,
    parent_id: str,
    report_file_name: str = "sbom_report",
    report_file_extension: str = "zip",
    standard="CycloneDX",
):
    """
    Fetch report by id and add it to evidence

    :param str report_id: Wiz report ID
    :param str parent_id: RegScale Parent ID
    :param str report_file_name: Report file name, defaults to "evidence_report"
    :param str report_file_extension: Report file extension, defaults to "zip"
    :param str standard: SBOM standard, defaults to "CycloneDX"
    :rtype: None
    """

    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file_path = f"artifacts/{report_file_name}_{current_datetime}.{report_file_extension}"
    variables = {"reportId": report_id}
    api_endpoint_url = WizVariables.wizUrl
    token = WizVariables.wizAccessToken
    if not token:
        error_and_exit("Wiz Access Token is missing. Authenticate with Wiz first.")
    client = PaginatedGraphQLClient(
        endpoint=api_endpoint_url,
        query=DOWNLOAD_QUERY,
        headers={
            "Content-Type": "application/json",
            "Authorization": BEARER + token,
        },
    )
    download_report = client.fetch_results(variables=variables)
    logger.debug(f"Download Report result: {download_report}")
    if "errors" in download_report:
        logger.error(f"Error fetching report: {download_report['errors']}")
        logger.error(f"Raw Response Data: {download_report}")
        return
    report_data = None
    if download_url := download_report.get("report", {}).get("lastRun", {}).get("url"):
        logger.info(f"Download URL: {download_url}")
        download_file(url=download_url, local_filename=report_file_path)
        with ZipFile(report_file_path, "r") as zObject:
            for filename in zObject.namelist():
                with zObject.open(filename) as json_f:
                    file_name = ".".join(filename.split(".")[:-1])
                    report_data = json.load(json_f)
                    sbom_standard = report_data.get("bomFormat", standard)
                    standard_version = report_data.get("specVersion", 1.5)
                    Sbom(
                        name=file_name,
                        tool="Wiz",
                        parentId=int(parent_id),
                        parentModule=SecurityPlan.get_module_slug(),
                        results=json.dumps(report_data),
                        standardVersion=standard_version,
                        sbomStandard=sbom_standard,
                    ).create_or_update(
                        bulk_update=True
                    )  # need put in for this endpoint to update SBOMS

        logger.info("SBOM attached successfully!")
    else:
        logger.error("Could not retrieve the download URL.")


@deprecated("Use the 'fetch_report_by_id' command instead.")
def fetch_report_id(query: str, variables: Dict, url: str) -> str:
    """
    Fetch report ID from Wiz

    :param str query: Query string
    :param Dict variables: Variables
    :param str url: Wiz URL
    :return str: Wiz ID
    :rtype str: str
    """
    try:
        resp = send_request(
            query=query,
            variables=variables,
            api_endpoint_url=url,
        )
        if "error" in resp.json().keys():
            error_and_exit(f'Wiz Error: {resp.json()["error"]}')
        return resp.json()["data"]["createReport"]["report"]["id"]
    except (requests.RequestException, AttributeError, TypeError) as rex:
        logger.error("Unable to pull report id from requests object\n%s", rex)
    return ""


def get_framework_names(wiz_frameworks: List) -> List:
    """
    Get the names of frameworks and replace spaces with underscores.

    :param List wiz_frameworks: List of Wiz frameworks.
    :return List: List of framework names.
    :rtype List: list
    """
    return [framework["name"].replace(" ", "_") for framework in wiz_frameworks]


def check_reports_for_frameworks(reports: List, frames: List) -> bool:
    """
    Check if any reports contain the given frameworks.

    :param List reports: List of reports.
    :param List frames: List of framework names.
    :return bool: Boolean indicating if any report contains a framework.
    :rtype bool: bool
    """
    return any(frame in item["name"] for item in reports for frame in frames)


def create_report_if_needed(
    wiz_project_id: str, frames: List, wiz_frameworks: List, reports: List, snake_framework: str
) -> List:
    """
    Create a report if needed and return report IDs.

    :param str wiz_project_id: Wiz Project ID.
    :param List frames: List of framework names.
    :param List wiz_frameworks: List of Wiz frameworks.
    :param List reports: List of reports.
    :param str snake_framework: Framework name with spaces replaced by underscores.
    :return List: List of Wiz report IDs.
    :rtype List: list
    """
    if not check_reports_for_frameworks(reports, frames):
        selected_frame = snake_framework
        selected_index = frames.index(selected_frame)
        wiz_framework = wiz_frameworks[selected_index]
        wiz_report_id = create_compliance_report(
            wiz_project_id=wiz_project_id,
            report_name=f"{selected_frame}_project_{wiz_project_id}",
            framework_id=wiz_framework.get("id"),
        )
        logger.info(f"Wiz compliance report created with ID {wiz_report_id}")
        return [wiz_report_id]
    logger.debug(f"Returning report ids for these reports {(report['name'] for report in reports)}")
    reports = [report["id"] for report in reports if any(frame in report["name"] for frame in frames)]
    return reports


def fetch_and_process_report_data(wiz_report_ids: List) -> List:
    """
    Fetch and process report data from report IDs.

    :param List wiz_report_ids: List of Wiz report IDs.
    :return List: List of processed report data.
    :rtype List: List
    """
    report_data = []
    for wiz_report in wiz_report_ids:
        download_url = get_report_url_and_status(wiz_report)
        logger.debug(f"Download url: {download_url}")
        with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
            logger.info("Download URL fetched. Streaming and parsing report")
            reader = csv.DictReader(codecs.iterdecode(data.iter_lines(), encoding="utf-8"), delimiter=",")
            for row in reader:
                report_data.append(row)
    return report_data


def get_or_create_report_id(
    project_id: str,
    frameworks: List[str],
    wiz_frameworks: List[Dict],
    existing_reports: List[Dict],
    target_framework: str,
) -> str:
    """
    Get an existing report ID or create a new one for the target framework.

    :param project_id: Project identifier
    :param frameworks: List of framework names
    :param wiz_frameworks: List of framework details with IDs
    :param existing_reports: List of existing reports
    :param target_framework: Target framework name with underscores
    :return: Single report ID
    """
    app = Application()
    report_age_days = app.config.get("wizReportAge", 15)
    report_name = f"{target_framework}_project_{project_id}"

    # Check for existing report with exact name
    for report in existing_reports:
        if report.get("name") == report_name:
            logger.info(f"Found existing report '{report_name}' with ID {report['id']}")

            # Check if report is expired based on wizReportAge
            run_at = report.get("lastRun", {}).get("runAt")

            if run_at and is_report_expired(run_at, report_age_days):
                logger.info(
                    f"Report '{report_name}' is expired (older than {report_age_days} days), will create new report"
                )
                break
            else:
                logger.info(f"Report '{report_name}' is still valid, using existing report")
                return report["id"]

    # Create new report if no valid existing report found
    try:
        framework_index = frameworks.index(target_framework)
        framework_id = wiz_frameworks[framework_index].get("id")

        report_id = create_compliance_report(
            wiz_project_id=project_id, report_name=report_name, framework_id=framework_id
        )
        logger.info(f"Created new report '{report_name}' with ID {report_id}")
        return report_id
    except ValueError:
        logger.error(f"Framework '{target_framework}' not found in frameworks list")
        raise


def fetch_report_data(report_id: str) -> List[Dict]:
    """
    Fetch and process data for a single report ID.

    :param report_id: Report identifier
    :return: List of report data rows
    """
    try:
        download_url = get_report_url_and_status(report_id)
        logger.debug(f"Fetching report {report_id} from: {download_url}")

        with closing(requests.get(url=download_url, stream=True, timeout=10)) as response:
            response.raise_for_status()
            logger.info(f"Streaming and parsing report {report_id}...")

            reader = csv.DictReader(codecs.iterdecode(response.iter_lines(), encoding="utf-8"), delimiter=",")
            logger.info(f"Report {report_id} fetched successfully.")
            return list(reader)
    except requests.RequestException as e:
        error_and_exit(f"Failed to fetch report {report_id}: {str(e)}")
    except csv.Error as e:
        error_and_exit(f"Failed to parse CSV for report {report_id}: {str(e)}")


# Usage example
def process_single_report(
    project_id: str,
    frameworks: List[str],
    wiz_frameworks: List[Dict],
    existing_reports: List[Dict],
    target_framework: str,
) -> List[Dict]:
    """Process a single report and return its data.
    :param project_id: Project identifier
    :param frameworks: List of framework names
    :param wiz_frameworks: List of framework details with IDs
    :param existing_reports: List of existing reports
    :param target_framework: Target framework name with underscores
    :return: List of report data rows
    """
    report_id = get_or_create_report_id(
        project_id=project_id,
        frameworks=frameworks,
        wiz_frameworks=wiz_frameworks,
        existing_reports=existing_reports,
        target_framework=target_framework,
    )
    return fetch_report_data(report_id)


def fetch_framework_report(wiz_project_id: str, snake_framework: str) -> List[Any]:
    """
    Fetch Framework Report from Wiz.

    :param str wiz_project_id: Wiz Project ID.
    :param str snake_framework: Framework name with spaces replaced by underscores.
    :return: List containing the framework report data.
    :rtype: List[Any]
    """
    wiz_frameworks = fetch_frameworks()
    frames = get_framework_names(wiz_frameworks)
    reports = list(query_reports(wiz_project_id))

    report_data = process_single_report(
        project_id=wiz_project_id,
        frameworks=frames,
        wiz_frameworks=wiz_frameworks,
        existing_reports=reports,
        target_framework=snake_framework,
    )

    return report_data


def fetch_frameworks() -> list:
    """
    Fetch frameworks from Wiz

    :raises General Error: If error in API response
    :return: List of frameworks
    :rtype: list
    """
    query = """
        query SecurityFrameworkAutosuggestOptions($policyTypes: [SecurityFrameworkPolicyType!],
        $onlyEnabledPolicies: Boolean) {
      securityFrameworks(
        first: 500
        filterBy: {policyTypes: $policyTypes, enabled: $onlyEnabledPolicies}
      ) {
        nodes {
          id
          name
        }
      }
    }
    """
    variables = {
        "policyTypes": "CLOUD",
    }
    resp = send_request(
        query=query,
        variables=variables,
        api_endpoint_url=WizVariables.wizUrl,
    )
    logger.debug(f"Response: {resp}")
    if resp and resp.ok:
        data = resp.json()
        return data.get("data", {}).get("securityFrameworks", {}).get("nodes")
    else:
        error_and_exit(f"Wiz Error: {resp.status_code if resp else None} - {resp.text if resp else 'No response'}")


def query_reports(wiz_project_id: str) -> list:
    """
    Query Report table from Wiz

    :return: list object from an API response from Wiz
    :rtype: list
    """

    # The variables sent along with the above query
    variables = {"first": 100, "filterBy": {"projectId": f"{wiz_project_id}"}}

    res = send_request(
        query=REPORTS_QUERY,
        variables=variables,
        api_endpoint_url=WizVariables.wizUrl,
    )
    result = []
    try:
        if "errors" in res.json().keys():
            error_and_exit(f'Wiz Error: {res.json()["errors"]}')
        json_result = res.json()
        logger.debug("JSON Result: %s", json_result)
        result = json_result.get("data", {}).get("reports", {}).get("nodes")
    except requests.JSONDecodeError:
        error_and_exit(f"Unable to fetch reports from Wiz: {res.status_code}, {res.reason}")
    return result


def send_request(
    query: str,
    variables: Dict,
    api_endpoint_url: Optional[str] = None,
) -> requests.Response:
    """
    Send a graphQL request to Wiz.

    :param str query: Query to use for GraphQL
    :param Dict variables:
    :param Optional[str] api_endpoint_url: Wiz GraphQL URL Default is None
    :raises ValueError: Value Error if the access token is missing from wizAccessToken in init.yaml
    :return requests.Response: response from post call to provided api_endpoint_url
    :rtype requests.Response: requests.Response
    """
    logger.debug("Sending a request to Wiz API")
    api = Api()
    payload = {"query": query, "variables": variables}
    if api_endpoint_url is None:
        api_endpoint_url = WizVariables.wizUrl
    if WizVariables.wizAccessToken:
        return api.post(
            url=api_endpoint_url,
            headers={
                "Content-Type": CONTENT_TYPE,
                "Authorization": BEARER + WizVariables.wizAccessToken,
            },
            json=payload,
        )
    raise ValueError("An access token is missing.")


def create_compliance_report(
    report_name: str,
    wiz_project_id: str,
    framework_id: str,
) -> str:
    """Create Wiz compliance report

    :param str report_name: Report name
    :param str wiz_project_id: Wiz Project ID
    :param str framework_id: Wiz Framework ID
    :return str: Compliance Report id
    :rtype str: str
    """
    report_variables = {
        "input": {
            "name": report_name,
            "type": "COMPLIANCE_ASSESSMENTS",
            "csvDelimiter": "US",
            "projectId": wiz_project_id,
            "complianceAssessmentsParams": {
                "securityFrameworkIds": [framework_id],
            },
            "emailTargetParams": None,
            "exportDestinations": None,
            "columnSelection": [
                "Assessed At",
                "Category",
                "Cloud Provider",
                "Cloud Provider ID",
                "Compliance Check Name (Wiz Subcategory)",
                "Created At",
                "Framework",
                "Ignore Reason",
                "Issue/Finding ID",
                "Native Type",
                "Object Type",
                "Policy Description",
                "Policy ID",
                "Policy Name",
                "Policy Short Name",
                "Policy Type",
                "Projects",
                "Remediation Steps",
                "Resource Cloud Platform",
                "Resource Group Name",
                "Resource ID",
                "Resource Name",
                "Resource Region",
                "Result",
                "Severity",
                "Subscription",
                "Subscription Name",
                "Subscription Provider ID",
                "Subscription Status",
                "Tags",
                "Updated At",
            ],
        }
    }

    return fetch_report_id(CREATE_REPORT_QUERY, report_variables, url=WizVariables.wizUrl)


def get_report_url_and_status(report_id: str) -> str:
    """
    Generate Report URL from Wiz report

    :param str report_id: Wiz report ID
    :raises: requests.RequestException if download failed and exceeded max # of retries
    :return: URL of report
    :rtype: str
    """
    for attempt in range(MAX_RETRIES):
        if attempt:
            logger.info(
                "Report %s is still updating, waiting %.2f seconds", report_id, CHECK_INTERVAL_FOR_DOWNLOAD_REPORT
            )
            time.sleep(CHECK_INTERVAL_FOR_DOWNLOAD_REPORT)

        response = download_report({"reportId": report_id})
        if not response or not response.ok:
            raise requests.RequestException("Failed to download report")

        response_json = response.json()
        if errors := response_json.get("errors"):
            message = errors[0]["message"]
            if RATE_LIMIT_MSG in message:
                rate = errors[0]["extensions"]["retryAfter"]
                logger.warning("Sleeping %i seconds due to rate limit", rate)
                time.sleep(rate)
                continue

            logger.error(errors)
        else:
            status = response_json.get("data", {}).get("report", {}).get("lastRun", {}).get("status")
            if status == "COMPLETED":
                return response_json["data"]["report"]["lastRun"]["url"]
            elif status == "EXPIRED":
                logger.warning("Report %s is expired, rerunning report...", report_id)
                rerun_expired_report({"reportId": report_id})
                return get_report_url_and_status(report_id)

    raise requests.RequestException("Download failed, exceeding the maximum number of retries")


def download_report(variables: Dict) -> requests.Response:
    """
    Return a download URL for a provided Wiz report id

    :param Dict variables: Variables for Wiz request
    :return: response from Wiz API
    :rtype: requests.Response
    """
    response = send_request(DOWNLOAD_QUERY, variables=variables)
    return response


def rerun_expired_report(variables: Dict) -> requests.Response:
    """
    Rerun a report

    :param Dict variables: Variables for Wiz request
    :return: Response object from Wiz API
    :rtype: requests.Response
    """
    response = send_request(RERUN_REPORT_QUERY, variables=variables)
    return response


# Compliance functions moved to wiz_compliance.py
# This is a deprecated function - use WizComplianceIntegration instead
def _sync_compliance(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    catalog_id: Optional[int] = None,
    framework: Optional[str] = "NIST800-53R5",
    update_control_status: bool = True,
) -> List[ComplianceReport]:
    """
    Sync compliance posture from Wiz to RegScale

    :param str wiz_project_id: Wiz Project ID
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param Optional[int] catalog_id: Catalog ID, defaults to None
    :param Optional[str] framework: Framework, defaults to NIST800-53R5
    :param bool update_control_status: Update control implementation status based on compliance results, defaults to True
    :return: List of ComplianceReport objects
    :rtype: List[ComplianceReport]
    """

    logger.info("Syncing compliance from Wiz with project ID %s", wiz_project_id)
    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    with compliance_job_progress:
        report_job = compliance_job_progress.add_task("[#f68d1f]Fetching Wiz compliance report...", total=1)
        fetch_regscale_data_job = compliance_job_progress.add_task(
            "[#f68d1f]Fetching RegScale Catalog info for framework...", total=1
        )
        framework_mapping = {
            "CSF": "NIST CSF v1.1",
            "NIST800-53R5": "NIST SP 800-53 Revision 5",
            "NIST800-53R4": "NIST SP 800-53 Revision 4",
        }
        sync_framework = framework_mapping.get(framework)
        snake_framework = sync_framework.replace(" ", "_")
        logger.debug(f"{snake_framework=}")
        logger.info("Fetching Wiz compliance report for project ID %s...", wiz_project_id)
        report_data = fetch_framework_report(wiz_project_id, snake_framework)
        report_models = []
        compliance_job_progress.update(report_job, completed=True, advance=1)

        if catalog_id:
            logger.info("Fetching all Controls for catalog #%s...", catalog_id)
            catalog = Catalog.get_with_all_details(catalog_id=catalog_id)
            controls = catalog.get("controls") if catalog else []
        else:
            # get all of the ControlImplementations for the security plan and get the controls from them
            logger.info("Fetching all Controls for %s #%d...", regscale_module, regscale_id)
            controls = SecurityControl.get_controls_by_parent_id_and_module(
                parent_module=regscale_module, parent_id=regscale_id, return_dicts=True
            )
        logger.info("Received %d control(s) from RegScale.", len(controls))

        passing_controls = {}
        failing_controls = {}
        controls_to_reports = {}

        compliance_job_progress.update(fetch_regscale_data_job, completed=True, advance=1)
        logger.info("Analyzing ComplianceReport for framework %s from Wiz...", sync_framework)
        running_compliance_job = compliance_job_progress.add_task(
            "[#f68d1f]Building compliance posture from wiz report...",
            total=len(report_data),
        )
        for row in report_data:
            try:
                cr = ComplianceReport(**row)
                if cr.framework == sync_framework:
                    check_compliance(
                        cr,
                        controls,
                        passing_controls,
                        failing_controls,
                        controls_to_reports,
                    )
                    report_models.append(cr)
            except ValidationError:
                error_message = traceback.format_exc()
                logger.error(f"Error creating ComplianceReport: {error_message}")
            finally:
                compliance_job_progress.update(running_compliance_job, advance=1)
        try:
            controls_with_data = len(controls_to_reports)
            logger.info(f"Creating assessments for {controls_with_data} controls with compliance data")
            if controls_with_data == 0:
                logger.warning("No controls have compliance data from Wiz")
                return report_models

            saving_regscale_data_job = compliance_job_progress.add_task(
                "[#f68d1f]Saving RegScale data...", total=controls_with_data
            )
            create_assessment_from_compliance_report(
                controls_to_reports=controls_to_reports,
                regscale_id=regscale_id,
                regscale_module=regscale_module,
                controls=controls,
                progress=compliance_job_progress,
                task=saving_regscale_data_job,
                update_control_status=update_control_status,
            )
            logger.info("Completed saving RegScale data.")
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error creating ControlImplementations from compliance report: {error_message}")
            # Re-raise the exception so it's not silently swallowed
            raise
        return report_models


def check_compliance(
    cr: ComplianceReport,
    controls: List[Dict],
    passing: Dict,
    failing: Dict,
    controls_to_reports: Dict,
) -> None:
    """
    Check compliance report for against controls

    :param ComplianceReport cr: Compliance Report
    :param List[Dict] controls: Controls List
    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :param Dict controls_to_reports: Controls to reports
    :return: None
    :rtype: None
    """
    for control in controls:
        if f"{control.get('controlId').lower()} " in cr.compliance_check.lower():
            _add_controls_to_controls_to_report_dict(control, controls_to_reports, cr)
            if cr.result == ComplianceCheckStatus.PASS.value:
                if control.get("controlId").lower() not in passing:
                    passing[control.get("controlId").lower()] = control
            else:
                if control.get("controlId").lower() not in failing:
                    failing[control.get("controlId").lower()] = control
    _clean_passing_list(passing, failing)


def _add_controls_to_controls_to_report_dict(control: Dict, controls_to_reports: Dict, cr: ComplianceReport) -> None:
    """
    Add controls to dict to process assessments from later

    :param Dict control: Control
    :param Dict controls_to_reports: Controls to reports
    :param ComplianceReport cr: Compliance Report
    :return: None
    :rtype: None
    """
    if control.get("controlId").lower() not in controls_to_reports.keys():
        controls_to_reports[control.get("controlId").lower()] = [cr]
    else:
        controls_to_reports[control.get("controlId").lower()].append(cr)


def _clean_passing_list(passing: Dict, failing: Dict) -> None:
    """
    Clean passing list. Ensures that controls that are passing are not also failing

    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :return: None
    :rtype: None
    """
    for control_id in failing:
        if control_id in passing:
            passing.pop(control_id, None)


def create_assessment_from_compliance_report(
    controls_to_reports: Dict,
    regscale_id: int,
    regscale_module: str,
    controls: List,
    progress: Progress,
    task: TaskID,
    update_control_status: bool = True,
) -> None:
    """
    Create assessment from compliance report

    :param Dict controls_to_reports: Controls to reports
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param List controls: Controls
    :param Progress progress: Progress object, used for progress bar updates
    :param TaskID task: Task ID, used for progress bar updates
    :param bool update_control_status: Update control implementation status based on compliance results, defaults to True
    :return: None
    :rtype: None
    """
    implementations = ControlImplementation.get_all_by_parent(parent_module=regscale_module, parent_id=regscale_id)
    total_controls = len(controls_to_reports)
    processed_count = 0

    for control_id, reports in controls_to_reports.items():
        try:
            processed_count += 1
            logger.debug(f"Processing control {control_id} ({processed_count}/{total_controls})")

            control_record_id = None
            for control in controls:
                if control.get("controlId").lower() == control_id:
                    control_record_id = control.get("id")
                    break

            filtered_results = [x for x in implementations if x.controlID == control_record_id]

            start_time = time.time()
            create_report_assessment(
                filtered_results,
                reports,
                control_id,
                update_control_status=update_control_status,
            )
            end_time = time.time()
            logger.debug(f"Assessment creation for {control_id} took {end_time - start_time:.2f} seconds")

            progress.update(task, advance=1)
            logger.debug(f"Updated progress: {processed_count}/{total_controls}")

        except Exception as e:
            logger.error(f"Error processing control {control_id}: {e}")
            # Still update progress even if there's an error
            progress.update(task, advance=1)


def create_report_assessment(
    filtered_results: List,
    reports: List,
    control_id: str,
    update_control_status: bool = True,
) -> None:
    """
    Create a single aggregated report assessment per control

    :param List filtered_results: Filtered results
    :param List reports: List of ComplianceReport objects for this control
    :param str control_id: Control ID
    :param bool update_control_status: Update control implementation status based on compliance results, defaults to True
    :return: None
    :rtype: None
    """
    logger.debug(f"Creating assessment for control {control_id} with {len(reports)} reports")

    implementation = filtered_results[0] if len(filtered_results) > 0 else None
    if not implementation or not reports:
        logger.debug(
            f"Skipping control {control_id}: implementation={bool(implementation)}, reports={len(reports) if reports else 0}"
        )
        return

    # Aggregate results: Fail if ANY asset fails, Pass only if ALL pass
    overall_result = "Pass"
    pass_count = 0
    fail_count = 0

    # Collect detailed results for comprehensive reporting
    asset_details = []

    for report in reports:
        if report.result == ComplianceCheckStatus.FAIL.value:
            overall_result = "Fail"
            fail_count += 1
        else:
            pass_count += 1

        # Collect asset details for the report
        asset_details.append(
            {
                "resource_name": report.resource_name,
                "resource_id": report.resource_id,
                "cloud_provider": report.cloud_provider,
                "subscription": report.subscription,
                "result": report.result,
                "policy_short_name": report.policy_short_name,
                "compliance_check": report.compliance_check,
                "severity": report.severity,
                "assessed_at": report.assessed_at,
            }
        )

    # Create comprehensive HTML summary
    html_summary = _create_aggregated_assessment_report(
        control_id=control_id,
        overall_result=overall_result,
        pass_count=pass_count,
        fail_count=fail_count,
        asset_details=asset_details,
        total_assets=len(reports),
    )

    # Create single assessment for this control
    assessment = Assessment(
        leadAssessorId=implementation.createdById,
        title=f"Wiz compliance assessment for {control_id}",
        assessmentType="Control Testing",
        plannedStart=get_current_datetime(),
        plannedFinish=get_current_datetime(),
        actualFinish=get_current_datetime(),
        assessmentResult=overall_result,
        assessmentReport=html_summary,
        status="Complete",
        parentId=implementation.id,
        parentModule="controls",
        isPublic=True,
    ).create()

    # Update implementation status once with aggregated result (if enabled)
    if update_control_status:
        update_implementation_status(
            implementation=implementation,
            result=overall_result,
        )
        logger.debug(f"Updated implementation status for {control_id}: {overall_result}")
    else:
        logger.debug(f"Skipping implementation status update for {control_id} (disabled via parameter)")

    logger.info(
        f"Created aggregated assessment for {control_id}: {assessment.id} "
        f"(Result: {overall_result}, Assets: {len(reports)}, Pass: {pass_count}, Fail: {fail_count})"
    )


def _create_aggregated_assessment_report(
    control_id: str, overall_result: str, pass_count: int, fail_count: int, asset_details: List[Dict], total_assets: int
) -> str:
    """
    Create a comprehensive HTML assessment report for aggregated compliance results

    :param str control_id: Control identifier
    :param str overall_result: Overall Pass/Fail result
    :param int pass_count: Number of passing assets
    :param int fail_count: Number of failing assets
    :param List[Dict] asset_details: Detailed information about each asset
    :param int total_assets: Total number of assets assessed
    :return: HTML formatted assessment report
    :rtype: str
    """
    # Create summary section
    summary_html = f"""
    <div style="margin-bottom: 20px; padding: 15px; border: 2px solid {'#d32f2f' if overall_result == 'Fail' else '#2e7d32'}; border-radius: 5px; background-color: {'#ffebee' if overall_result == 'Fail' else '#e8f5e8'};">
        <h3 style="margin: 0 0 10px 0; color: {'#d32f2f' if overall_result == 'Fail' else '#2e7d32'};">
            Assessment Summary for Control {control_id}
        </h3>
        <p><strong>Overall Result:</strong> <span style="color: {'#d32f2f' if overall_result == 'Fail' else '#2e7d32'}; font-weight: bold;">{overall_result}</span></p>
        <p><strong>Total Assets Assessed:</strong> {total_assets}</p>
        <p><strong>Passing Assets:</strong> <span style="color: #2e7d32;">{pass_count}</span></p>
        <p><strong>Failing Assets:</strong> <span style="color: #d32f2f;">{fail_count}</span></p>
        <p><strong>Assessment Date:</strong> {get_current_datetime()}</p>
    </div>
    """

    # Create detailed asset results table
    if asset_details:
        table_rows = []
        for asset in asset_details:
            result_color = "#d32f2f" if asset["result"] == "Fail" else "#2e7d32"
            table_rows.append(
                f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('resource_name', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('resource_id', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('cloud_provider', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('subscription', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; color: {result_color}; font-weight: bold;">{asset.get('result', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('policy_short_name', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('compliance_check', 'N/A')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{asset.get('severity', 'N/A')}</td>
                </tr>
            """
            )

        asset_table_html = f"""
        <div style="margin-top: 20px;">
            <h4>Detailed Asset Results</h4>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Resource Name</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Resource ID</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Cloud Provider</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Subscription</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Result</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Policy</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Compliance Check</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ddd; text-align: left;">Severity</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
        """
    else:
        asset_table_html = "<p><em>No asset details available.</em></p>"

    # Combine summary and details
    return summary_html + asset_table_html


def update_implementation_status(implementation: ControlImplementation, result: str) -> ControlImplementation:
    """
    Update implementation status based on the report result

    :param ControlImplementation implementation: Control Implementation object
    :param str result: Report result
    :return: Updated Control Implementation object
    :rtype: ControlImplementation
    """
    objectives = ImplementationObjective.get_all_by_parent(
        parent_module=implementation.get_module_slug(),
        parent_id=implementation.id,
    )
    if objectives:
        for objective in objectives:
            objective.status = report_result_to_implementation_status(result)
            objective.save()
            logger.debug(f"Updated status for {objective.id}: {objective.status}")
    else:
        implementation.objectives = []
    implementation.status = report_result_to_implementation_status(result)
    implementation.save()
    logger.info(f"Updated implementation status for {implementation.id}: {implementation.status}")


def get_wiz_compliance_settings():
    """
    Get Wiz compliance settings for status mapping

    :return: Compliance settings instance or None
    :rtype: Optional[ComplianceSettings]
    """
    try:
        settings = ComplianceSettings.get_by_current_tenant()
        wiz_compliance_setting = next((comp for comp in settings if comp.title == "Wiz Compliance Setting"), None)
        if not wiz_compliance_setting:
            logger.debug("No Wiz Compliance Setting found, using default implementation status mapping")
        else:
            logger.debug("Using Wiz Compliance Setting for implementation status mapping")
        return wiz_compliance_setting
    except Exception as e:
        logger.debug(f"Error getting Wiz Compliance Setting: {e}")
        return None


def report_result_to_implementation_status(result: str) -> str:
    """
    Convert report result to implementation status using compliance settings if available

    :param str result: Report result
    :return: Implementation status
    :rtype: str
    """
    compliance_settings = get_wiz_compliance_settings()

    if compliance_settings:
        try:
            # Get implementation status labels from compliance settings
            status_labels = compliance_settings.get_field_labels("implementationStatus")

            # Map compliance check result to implementation status
            result_lower = result.lower()
            for label in status_labels:
                label_lower = label.lower()
                if result_lower == ComplianceCheckStatus.PASS.value.lower():
                    if label_lower in ["implemented", "complete", "compliant"]:
                        return label
                elif result_lower == ComplianceCheckStatus.FAIL.value.lower():
                    if label_lower in ["inremediation", "in remediation", "remediation", "failed", "non-compliant"]:
                        return label
                else:  # Not implemented or other status
                    if label_lower in ["notimplemented", "not implemented", "pending", "planned"]:
                        return label

            logger.debug(f"No matching compliance setting found for result: {result}")
        except Exception as e:
            logger.debug(f"Error using compliance settings for implementation status mapping: {e}")

    # Fallback to default mapping
    if result == ComplianceCheckStatus.PASS.value:
        return ControlImplementationStatus.Implemented.value
    elif result == ComplianceCheckStatus.FAIL.value:
        return ControlImplementationStatus.InRemediation.value
    else:
        return ControlImplementationStatus.NotImplemented.value


def create_vulnerabilities_from_wiz_findings(
    wiz_project_id: str,
    regscale_plan_id: int,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    filter_by_override: Optional[str] = None,
) -> int:
    """
    Create vulnerabilities from Wiz findings using the WizVulnerabilityIntegration class.

    This function properly uses the ScannerIntegration framework to create vulnerabilities
    and associated mappings, following the established patterns.

    :param str wiz_project_id: Wiz project ID to scan
    :param int regscale_plan_id: RegScale security plan ID
    :param Optional[str] client_id: Wiz client ID (optional, uses WizVariables if not provided)
    :param Optional[str] client_secret: Wiz client secret (optional, uses WizVariables if not provided)
    :param Optional[str] filter_by_override: Optional filter override for findings
    :return: Number of vulnerabilities processed
    :rtype: int
    """
    # Import here to avoid circular imports
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration

    try:
        logger.info(f"Starting vulnerability creation for Wiz project {wiz_project_id}")

        # Create the integration instance
        wiz_integration = WizVulnerabilityIntegration(plan_id=regscale_plan_id)

        # Authenticate if credentials provided
        if client_id and client_secret:
            wiz_integration.authenticate(client_id=client_id, client_secret=client_secret)
        elif not WizVariables.wizAccessToken:
            # Try to authenticate with stored credentials
            wiz_integration.authenticate()

        # Set up any filter overrides
        if filter_by_override:
            try:
                filter_dict = json.loads(filter_by_override)
                logger.info(f"Using filter override: {filter_dict}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid filter override JSON: {filter_by_override}")
                filter_dict = {}
        else:
            filter_dict = {"projectId": wiz_project_id}

        # Use the sync_findings class method which handles the complete workflow:
        # 1. Creates ScanHistory
        # 2. Fetches findings from Wiz
        # 3. Creates vulnerabilities and vulnerability mappings
        # 4. Creates associated issues (if configured)
        # 5. Closes outdated vulnerabilities
        # 6. Updates scan history with results
        vulnerabilities_processed = WizVulnerabilityIntegration.sync_findings(
            plan_id=regscale_plan_id,
            wiz_project_id=wiz_project_id,
            filter_by_override=json.dumps(filter_dict) if filter_dict else None,
        )

        logger.info(f"Successfully processed {vulnerabilities_processed} vulnerabilities from Wiz")
        return vulnerabilities_processed

    except Exception as e:
        logger.error(f"Error creating vulnerabilities from Wiz findings: {e}", exc_info=True)
        raise


def create_single_vulnerability_from_wiz_data(
    wiz_finding_data: Dict[str, Any],
    asset_id: str,
    regscale_plan_id: int,
    scan_history_id: Optional[int] = None,
) -> Optional[regscale_models.Vulnerability]:
    """
    Create a single vulnerability from Wiz finding data.

    This is a lower-level function for creating individual vulnerabilities when you have
    specific Wiz finding data and want more control over the process.

    :param Dict[str, Any] wiz_finding_data: Raw Wiz finding data
    :param str asset_id: Asset identifier for the vulnerability
    :param int regscale_plan_id: RegScale security plan ID
    :param Optional[int] scan_history_id: Scan history ID (creates new if not provided)
    :return: Created vulnerability or None if creation failed
    :rtype: Optional[regscale_models.Vulnerability]
    """
    # Import here to avoid circular imports
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration
    from regscale.integrations.commercial.wizv2.constants import WizVulnerabilityType

    try:
        # Create integration instance
        wiz_integration = WizVulnerabilityIntegration(plan_id=regscale_plan_id)

        # Create or get scan history
        if scan_history_id:
            scan_history = regscale_models.ScanHistory.get_by_id(scan_history_id)
            if not scan_history:
                logger.error(f"Scan history with ID {scan_history_id} not found")
                return None
        else:
            scan_history = wiz_integration.create_scan_history()

        # Parse the Wiz finding data into an IntegrationFinding
        integration_finding = wiz_integration.parse_finding(wiz_finding_data, WizVulnerabilityType.VULNERABILITY)

        if not integration_finding:
            logger.warning("Failed to parse Wiz finding data into IntegrationFinding")
            return None

        # Set the asset identifier
        integration_finding.asset_identifier = asset_id

        # Get the asset
        asset = wiz_integration.get_asset_by_identifier(asset_id)
        if not asset:
            logger.error(f"Asset with identifier {asset_id} not found")
            return None

        # Handle the vulnerability creation using the integration framework
        vulnerability_id = wiz_integration.handle_vulnerability(
            finding=integration_finding,
            asset=asset,
            scan_history=scan_history,
        )

        if vulnerability_id:
            vulnerability = regscale_models.Vulnerability.get_by_id(vulnerability_id)
            logger.info(f"Successfully created vulnerability {vulnerability_id}")
            return vulnerability
        else:
            logger.warning("Failed to create vulnerability")
            return None

    except Exception as e:
        logger.error(f"Error creating single vulnerability: {e}", exc_info=True)
        return None
