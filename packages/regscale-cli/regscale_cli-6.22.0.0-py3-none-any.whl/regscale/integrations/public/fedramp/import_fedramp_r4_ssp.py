"""Import FedRAMP Revision 4 SSP XML into RegScale"""

# flake8: noqa
from datetime import datetime
from typing import Any, Dict, Tuple, Generator, Optional

from lxml import etree
from pydantic import ValidationError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.integrations.public.fedramp.metadata import parse_metadata
from regscale.integrations.public.fedramp.reporting import write_events
from regscale.integrations.public.fedramp.system_characteristics import (
    parse_minimum_ssp,
    parse_system_characteristics,
)
from regscale.integrations.public.fedramp.system_control_implementations import (
    fetch_implementations,
)
from regscale.integrations.public.fedramp.system_implementation import (
    parse_system_implementation,
)
from regscale.core.app.utils.app_utils import (
    get_file_name,
)
from regscale.core.app.utils.regscale_utils import create_new_data_submodule
from regscale.models.regscale_models import File, SecurityPlan

logger = create_logger()


def parse_and_load_xml_rev4(
    context: Any, file_path: str, catalogue_id: int, filename: str = "Sample.xml"
) -> Generator[Tuple[str, Dict, Dict], None, None]:
    """
     Parse and load XML Rev4

    :param Any context: Flask app context
    :param str file_path: Path to XML file
    :param int catalogue_id: Catalogue ID user selected
    :param str filename: Name of file that will be uploaded to RegScale
    :yields Generator[Tuple[str, Dict, Dict]]: Tuple of filename and upload results
    :return: Tuple of filename and upload results
    :rtype: Generator[Tuple[str, Dict, Dict]]
    """
    # Process with app request context to yield partial content to the browser
    # with context:
    logger.info(f"Parsing and loading file {file_path}.")
    events_list = []  # will store events as they take place throughout the import process
    app = Application()
    api = Api()
    events_list = []  # will store events as they take place throughout the import process

    ns = {
        "ns1": "http://csrc.nist.gov/ns/oscal/1.0",
        "oscal": "http://csrc.nist.gov/ns/oscal/1.0",
        "fedramp": "https://fedramp.gov/ns/oscal",
    }
    if context is not None:
        yield "<div>Creating Security Plan...</div>"
    tree = etree.parse(file_path)
    root = tree.getroot()
    ssp_uuid = root.attrib["uuid"]
    new_ssp = {"uuid": ssp_uuid}

    # Create fedramp traversal object.
    trv = FedrampTraversal(
        api=api,
        root=root,
        namespaces=ns,
    )
    # --- Set the catalogue_id on the traversal object.
    trv.catalogue_id = catalogue_id

    # 0. Create the EMPTY SSP that we need for later posts.
    ssp_id = parse_minimum_ssp(api=api, root=root, new_ssp=new_ssp, ns=ns, events_list=events_list)
    logger.info(f"Created new SSP in RegScale with ID {ssp_id}.")
    # --- Set the ssp_id on the traversal object.
    trv.ssp_id = ssp_id

    # -- validate oscal ssp via API call
    validatefile = "artifacts/validation-results.csv"
    now = datetime.now()
    validatefile = validatefile.replace(".", "-SSP-{0}_".format(ssp_id) + now.strftime("%Y%m%d."))

    logger.info("Validating OSCAL file... please stand by.")
    valid_msg = validate_oscal(trv, file_path)
    validate_list = valid_msg
    logger.info(valid_msg)
    logger.info("Validation complete.")

    write_events(validate_list, validatefile)
    attach_artifact_to_ssp(trv=trv, file_path=validatefile, tags="imported-oscal-validation-report,")

    trv.log_info(
        {
            "record_type": "oscal",
            "event_msg": f"OSCAL validation of file '{get_file_name(file_path)}' ran successfully."
            "Validation result file in RegScale.",
        }
    )

    # 1. Parse the <metadata> tag
    parse_metadata(trv, app)
    if context is not None:
        yield "<div>Parsing metadata...</div>"

    # upload xml file & data submodules in the SSP
    attach_artifact_to_ssp(trv=trv, file_path=file_path, tags="system-security-plan,")

    # 2. Parse the <system-characteristics> tag
    parse_system_characteristics(ssp_id=ssp_id, root=root, ns=ns, events_list=events_list)
    logger.info("System characteristics parsed successfully.")

    # 3. Parse the <system-implementation> tag!
    if context is not None:
        yield "<div>Creating control implementations (this may take several minutes)...</div>"
    parse_system_implementation(trv)
    if context is not None:
        yield "<div>Control implementations created.</div>"

    # 4. TODO <control-implementation>
    # parse_control_implementation()

    # 5. Parse <back-matter>
    # parse_back_matter()

    # Write the events.
    resultfile = "artifacts/import-results.csv"
    now = datetime.now()
    resultfile = resultfile.replace(".", "-SSP-{0}_".format(ssp_id) + now.strftime("%Y%m%d."))

    logger.info("Uploading SSP to RegScale...")
    if context is not None:
        yield "<div>Uploading source SSP to RegScale...</div>"

    try:
        ssp = SecurityPlan(**new_ssp)
    except ValidationError as exc:
        logger.error(f"Failed to validate: {exc}")
        return resultfile, {
            "status": "failed",
        }
    # you can create a new ssp without the userId populated, but we normally use the userId from init.yaml
    ssp.systemOwnerId = app.config["userId"]
    ssp.id = ssp_id
    ssp.uuid = ssp_uuid
    new_ssp = ssp.update_ssp(api=api, return_id=False)
    new_ssp_id = new_ssp.id
    oscal_implementations = fetch_implementations(trv=trv, root=root, ssp=new_ssp)

    upload_results = {
        "ssp_id": new_ssp_id,
        "implementations_loaded": len(oscal_implementations),
        "ssp_title": new_ssp.systemName,
    }
    logger.info(f"Finished uploading SSP {ssp_id}")

    final_list = [*events_list, *trv.errors, *trv.infos]
    write_events(final_list, resultfile)

    # upload privacyImpactAssessment. If is None then dont.
    logger.info(f"Uploading validation results for import SSP {new_ssp_id}")
    attach_artifact_to_ssp(trv=trv, file_path=resultfile, tags="imported-security-plan-report,")
    if context is None:
        return resultfile, upload_results, oscal_implementations
    else:
        yield resultfile, upload_results, oscal_implementations


def validate_oscal(trv: FedrampTraversal, file_path: str) -> Optional[list[str]]:
    """
    Function to validate the SSP XML file against NIST OSCAL constraints

    :param FedrampTraversal trv: FedrampTraversal object
    :param str file_path: Path to the file to validate
    :raises ValueError: If the file size is over 100 MB
    :return: List of validation results
    :rtype: Optional[list[str]]
    """
    api = trv.api
    file_data = [bytes]

    file_path, file_size = File._check_compression(file_path=file_path, size_limit_mb=100, file_data=file_data)
    if file_size > 104857600:
        mb_size = file_size / 1024 / 1024
        limit_size = 104857600 / 1024 / 1024
        raise ValueError(f"File size is {mb_size} MB. This is over the max file size of {limit_size} MB")

    file_headers = {
        "Authorization": api.config["token"],
        "accept": "multipart/form-data, text/xml, text/html, application/json, text/plain, */*",
    }
    file_type_header = "multipart/form-data"
    data = open(file_path, "rb").read()
    if not data:
        logger.info("unable to read file!")

    files = [
        (
            "file",
            (
                file_path,
                data or open(file_path, "rb").read(),
                file_type_header,
            ),
        )
    ]

    url = f"{api.config['domain']}/api/oscal/ValidateNIST"
    file_res = api.post(
        url=url,
        headers=file_headers,
        files=files,
    )

    if not file_res.ok:
        api.logger.warning(f"{file_res.status_code} - {file_res.reason}")
        return None
    else:
        retstr = file_res.text
        retstr = retstr.replace("\x1b[97m[\x1b[0;91mERROR\x1b[0;97m] \x1b", "")
        retstr = retstr.rsplit("[m[")
        return retstr


def attach_artifact_to_ssp(trv: FedrampTraversal, file_path: str, tags: str) -> None:
    """
    Function to attach the XML file to the SSP's data and file submodules in RegScale

    :param FedrampTraversal trv: FedrampTraversal object
    :param str file_path: Path to the file to upload
    :param str tags: Tags to attach to the file during upload
    :rtype: None
    """

    # upload xml file to SSP
    if File.upload_file_to_regscale(
        file_name=file_path,
        parent_id=trv.ssp_id,
        parent_module="securityplans",
        api=trv.api,
        tags=tags,
        return_object=True,
    ):
        trv.log_info(
            {
                "record_type": "file",
                "event_msg": f"Uploaded file '{get_file_name(file_path)}' to SSP# {get_file_name(file_path)}"
                "File module in RegScale.",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": "file",
                "event_msg": f"Failed to upload file '{get_file_name(file_path)}' to SSP# {trv.ssp_id} "
                "File module in RegScale.",
            }
        )
    if create_new_data_submodule(parent_id=trv.ssp_id, parent_module="securityplans", file_path=file_path):
        trv.log_info(
            {
                "record_type": "Data",
                "event_msg": f"Uploaded file '{get_file_name(file_path)}' to SSP# {get_file_name(file_path)}"
                "Data module in RegScale.",
            }
        )
    else:
        trv.log_error(
            {
                "record_type": "Data",
                "event_msg": f"Failed to upload file '{get_file_name(file_path)}' to SSP# {trv.ssp_id} "
                " Data module in RegScale.",
            }
        )
