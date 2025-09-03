"""Module to parse the back-matter and resources from an SSP and post the items into RegScale"""

# flake8: noqa: C901
import base64
import json
import mimetypes
from io import BytesIO
from typing import Any, List, Optional

from lxml.etree import Element

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.reporting import log_error, log_event
from regscale.models.regscale_models import File, Link, Reference

logger = create_logger()
RESOURCE = "Resources"
NS_TITLE = "ns1:title"
NS_CAPTION = "ns1:caption"
NS_DESC = "ns1:description"
NS_PROP = 'ns1:prop[@name="type"]'

TYPE_MAPPING = [
    ("Acronym", "acronyms"),
    ("Administrator Guide", "administrators-guide"),
    ("Agreement", "agreement"),
    ("Artifact", "artifact"),
    ("Citation", "citations"),
    ("Evidence", "evidence"),
    ("Guidance", "external-guidance"),
    ("Image", "image"),
    ("Interview Notes", "interview-notes"),
    ("Law", "law"),
    ("Logo", "logo"),
    ("Plan", "plan"),
    ("Policy", "policy"),
    ("Procedure", "procedure"),
    ("Questionnaire", "questionnaire"),
    ("Raw Data", "raw-data"),
    ("Regulation", "regulation"),
    ("Report", "report"),
    ("Rules of Behavior", "rules-of-behavior"),
    ("Screenshot", "screen-shot"),
    ("Standard", "standard"),
    ("System Guide", "system-guide"),
    ("Tool Output", "tool-output"),
    ("User Guide", "users-guide"),
]


def parse_backmatter(resource_elem: Any, back_matter: Any, root: Any, ns: dict, ssp_id: int, events_list: list) -> dict:
    """
    A function to parse a <resource> element from an SSP and post it to RegScale

    :param Any resource_elem: The data element that is being passed to be parsed into a resource
    :param Any back_matter: The back-matter element of the SSP
    :param Any root: The root element of the xml document
    :param dict ns: Namespace dict to use for xpath element selection
    :param int ssp_id: SSP ID in RegScale
    :param list events_list: List of events to send to logs
    :return: dictionary containing the results of the resource uploads
    :rtype: dict
    """
    app = Application()
    api = Api()
    results = {
        "filesUploaded": 0,
        "linksCreated": 0,
        "referencesCreated": 0,
    }
    # remove resources that do not have a uuid
    resources = {
        resource.attrib["uuid"]: resource_to_dict(resource)
        for resource in resource_elem
        if resource.attrib.get("uuid") is not None
    }
    # iterate the resources and put them in the right list
    for uuid, resource in resources.items():
        # check for references of the uuid elsewhere
        matching_elements = root.xpath(f".//*[@uuid='{uuid}']", namespaces=ns)

        # Exclude back-matter from results
        if filtered_elements := [el for el in matching_elements if back_matter not in el.iterancestors()]:
            resource["references"] = filtered_elements

        if resource["hasBase64"]:
            upload = File.upload_file_to_regscale(
                file_name=resource["base64_filename"],
                parent_id=ssp_id,
                parent_module="securityplans",
                api=api,
                file_data=base64.b64decode(resource["base64_data"]),
                return_object=True,
            )
            if upload:
                results["filesUploaded"] += 1
                events_list.append(
                    log_event(
                        record_type="File",
                        event_msg=f"File {resource['base64_filename']} uploaded successfully.",
                        model_layer=RESOURCE,
                    )
                )
            else:
                events_list.append(
                    log_error(
                        record_type="File",
                        event_msg=f"File {resource['base64_filename']} failed to upload.",
                        model_layer=RESOURCE,
                    )
                )
        # if there is no base64, then there should be a link
        other_attributes = None
        if "title_rlink_href" in resource:
            other_attributes = None
            try:
                if "title_prop" in resource:
                    other_attributes = ", ".join(
                        [
                            f"{key}: {value}"
                            for key, value in resource["title_prop"].items()
                            if resource.get("title_prop")
                        ]
                    )
            except KeyError:
                other_attributes = None
            link_to_post = Link(
                title=resource.get("title") or uuid,
                url=resource["title_rlink_href"],
                parentID=ssp_id,
                parentModule="securityplans",
                createdById=app.config["userId"],
                externalId=uuid,
                otherAttributes=other_attributes,
            )
            if _ := Link.insert_link(app, link_to_post):
                results["linksCreated"] += 1
                events_list.append(
                    log_event(
                        record_type="Link",
                        event_msg=f"Link {resource['title_rlink_href']} created successfully.",
                        model_layer=RESOURCE,
                    )
                )
            else:
                events_list.append(
                    log_error(
                        record_type="Link",
                        event_msg=f"Link {resource['title_rlink_href']} failed to be created.",
                        model_layer=RESOURCE,
                    )
                )

        if references := resource.get("references"):
            for reference in references:
                if post_dict_reference(
                    api=api,
                    ssp_id=ssp_id,
                    reference_data=reference_to_dict(reference, ns),
                    resource_uuid=uuid,
                    resource=resource,
                ):
                    results["referencesCreated"] += 1
                    events_list.append(
                        log_event(
                            record_type="Reference",
                            event_msg=f"Reference {reference.attrib['uuid']} created successfully.",
                            model_layer=RESOURCE,
                        )
                    )
                else:
                    events_list.append(
                        log_error(
                            record_type="Reference",
                            event_msg=f"Reference {reference.attrib['uuid']} failed to be created.",
                            model_layer=RESOURCE,
                        )
                    )

    return results


def post_dict_reference(
    api: Api, ssp_id: int, reference_data: dict, resource: dict, resource_uuid: str
) -> Optional[Reference]:
    """
    A function to post a reference to RegScale

    :param Api api: Api object
    :param int ssp_id: ID of the SSP to post the reference to
    :param dict reference_data: Reference to parse and post to RegScale
    :param dict resource: Resource that the reference is associated with
    :param str resource_uuid: UUID of the resource that the reference is associated with
    :return: Reference object if successful, None otherwise
    :rtype: Optional[Reference]
    """
    reference_to_post = Reference(
        createdById=api.config["userId"],
        identificationNumber=resource_uuid,
        title=reference_data.get("title"),
        parentId=ssp_id,
        parentModule="securityplans",
        referenceType="Other",
        link=resource.get("base64_filename") or resource.get("title_rlink_href"),
    )
    return reference_to_post.create_new_references(return_object=True)


def reference_to_dict(reference: Element, ns: dict) -> dict:
    """
    Function to convert a reference, lxml Element, into a dictionary

    :param Element reference: reference to parse
    :param dict ns: Namespace dict to use for xpath element selection
    :return: dictionary of the provided reference
    :rtype: dict
    """
    ref = {}
    # DESCRIPTION
    if reference.find(NS_DESC, namespaces=ns) is not None:
        ref["description"] = ""
        for p in reference.find(NS_DESC, namespaces=ns).findall("ns1:p", namespaces=ns):
            ref["description"] = ref["description"] + p.text + " "

    # TITLE (RegScale required)
    if reference.find(NS_TITLE, namespaces=ns) is not None:  # first check for title element
        ref["title"] = reference.find(NS_TITLE, namespaces=ns).text
    elif reference.find(NS_CAPTION, namespaces=ns) is not None:  # if not that, use caption for title
        ref["title"] = reference.find(NS_CAPTION, namespaces=ns).text
    elif reference.find(NS_DESC, namespaces=ns) is not None:  # if no caption, use description up to 50 char
        ref["title"] = ref["description"][:50]
    else:  # if all else fails, just make it "Untitled
        ref["title"] = "Untitled"

    # TYPE (RegScale required)
    if reference.find(NS_PROP, namespaces=ns) is not None:
        ref["referenceType"] = apply_type_mapping(
            TYPE_MAPPING,
            reference.find(NS_PROP, namespaces=ns)[0].text,
        )
    else:
        ref["referenceType"] = "Other"

    return ref


def apply_type_mapping(mapping: List[tuple], value: str) -> Any:
    """
    A function to apply a mapping to a value

    :param List[tuple] mapping: List of mapping pair tuples - (new, original)
    :param str value: Thing to be mapped to a new value
    :return: The new value
    :rtype: Any
    """
    for new, original in mapping:
        if value == original:
            value = new
            break
        else:
            value = "Other"
    return value


def resource_to_dict(resource: Element) -> dict:
    """
    Recursive function to convert a lxml Element into a dictionary

    :param Element resource: The lxml Element to convert to a dict
    :return: Dictionary representation of the Element
    :rtype: dict
    """
    resource_dict = {"hasBase64": False}  # Initialize dictionary for each resource

    for child in resource:
        tag = str(child.tag).split("}")[-1]  # Convert tag to string and then strip namespace

        if tag == "title":
            resource_dict["title"] = child.text

        elif tag == "description":
            for p_tag in child.findall(".//p"):
                resource_dict["title_description"] = p_tag.text

        elif tag == "prop":
            name = child.get("name")
            value = child.get("value")
            if name and value:
                resource_dict["title_prop"] = {"name": name, "value": value}

        elif tag == "rlink":
            href = child.get("href")
            media_type = child.get("media-type")
            if href:
                resource_dict["title_rlink_href"] = href
            if media_type:
                resource_dict["title_media-type"] = media_type

        elif tag == "base64":
            resource_dict["hasBase64"] = True
            base64_data = child.text.strip()  # Get base64 content and strip whitespace
            filename = child.get("filename")
            media_type = child.get("media-type")
            resource_dict["base64_data"] = base64_data
            if filename:
                resource_dict["base64_filename"] = filename
            if media_type:
                resource_dict["base64_media-type"] = media_type

    return resource_dict


def parse_title(resource: Any, ref: dict, ns: dict, resource_elem: Any) -> str:
    """
    Function to parse the title of a resource

    :param Any resource: The resource to parse
    :param dict ref: Reference dictionary
    :param dict ns: Namespace dictionary
    :param Any resource_elem: The resource element to parse
    :return: The title of the resource
    :rtype: str
    """
    if resource.find(NS_TITLE, namespaces=ns) is not None:  # first check for title element
        return resource.find(NS_TITLE, namespaces=ns).text
    elif resource.find(NS_CAPTION, namespaces=ns) is not None:  # if not that, use caption for title
        return resource.find(NS_CAPTION, namespaces=ns).text
    elif resource_elem.find(NS_CAPTION, namespaces=ns) is not None:  # also check referring element for caption
        return resource_elem.find(NS_CAPTION, namespaces=ns).text
    elif resource.find(NS_DESC, namespaces=ns) is not None:  # if no caption, use description up to to 50 char
        return ref["description"][:50]
    else:  # if all else fails, just make it "Untitled
        return "Untitled"


def record_resource(resource_elem: Any, root: Any, ns: dict, ssp_id: int, tags: Optional[Any] = None) -> None:
    """
    A function to parse a <resource> element from an SSP and post it to RegScale

    :param Any resource_elem: The data element that is being passed to be parsed into a resource
    :param Any root: The root element of the xml document
    :param dict ns: Namespace dict to use for xpath element selection
    :param int ssp_id: SSP ID in RegScale
    :param Optional[Any] tags: Optional string of semicolon-delimited tags to identify specific critical assets like network diagrams, defaults to None
    :rtype: None
    """
    api = Api()
    object_uuid = resource_elem.attrib[
        "uuid"
    ]  # the id of the object that the back-matter resource is intended to describe
    resource_link_id = resource_elem.find("ns1:link", namespaces=ns).attrib["href"].replace("#", "")  # get uuid URI

    # find the <resource> assembly whose uuid matches the URI
    query_string = f"/ns1:system-security-plan/ns1:back-matter/ns1:resource[@uuid='{resource_link_id}']"
    resource = root.xpath(query_string, namespaces=ns)[0]

    ref = {}

    # DESCRIPTION
    if resource.find(NS_DESC, namespaces=ns) is not None:
        ref["description"] = ""
        for p in resource.find(NS_DESC, namespaces=ns).findall("ns1:p", namespaces=ns):
            ref["description"] = ref["description"] + p.text + " "

    # TITLE (RegScale required)
    ref["title"] = parse_title(resource, ref, ns, resource_elem)

    # TYPE (RegScale required)
    if resource.find(NS_PROP, namespaces=ns) is not None:
        ref["referenceType"] = apply_type_mapping(TYPE_MAPPING, resource.find(NS_PROP, namespaces=ns)[0].text)
    else:
        ref["referenceType"] = "Other"
    # PARENT
    ref["parentID"] = ssp_id
    ref["parentModule"] = "securityplans"
    if object_uuid is not None:
        ref["identificationNumber"] = object_uuid

    # RLINKS
    for rlink in resource.findall("ns1:rlink", namespaces=ns):
        new_reference = ref  # start a new instance of a reference with the shared default values
        new_reference["link"] = rlink.attrib["href"]
        post_reference(new_reference)

    # BASE64
    for base64elem in resource.findall("ns1:base64", namespaces=ns):
        new_reference = ref  # start a new instance of a reference with the shared default values
        new_reference["link"] = base64elem.attrib["filename"]
        post_reference(new_reference)
        file_metadata = {
            "trustedDisplayName": base64elem.attrib["filename"],
            "filesize": len(base64elem.text) * 0.75 - (base64elem.text[len(base64elem.text) - 2 :].count("=")),
        }
        if "media-type" in base64elem.attrib:
            file_metadata["mimeType"] = base64elem.attrib["media-type"]
        else:
            file_metadata["mimeType"], _ = mimetypes.guess_type(file_metadata["trustedDisplayName"])
        if tags:
            file_metadata["tags"] = tags
        file_metadata["parentId"] = (ssp_id,)
        file_metadata["ParentModule"] = ("securityplans",)
        file_response = File.upload_file_to_regscale(
            file_name=file_metadata["trustedDisplayName"],
            parent_id=ssp_id,
            parent_module="securityplans",
            api=api,
            file_data=base64.b64decode(base64elem.text),
        )
        logger.info(file_response)
        # upload_base64_file(file_metadata, base64elem.text, ssp_id)


def post_reference(reference_dict: dict) -> None:
    """
    A function to post a reference to RegScale

    :param dict reference_dict: Reference object to post to RegScale
    :rtype: None
    """
    app = Application()
    api = Api()
    headers_json = {
        "accept": "*/*",
        "Content-Type": "application/json-patch+json",
        "Authorization": app.config["token"],
    }
    ssp_json = json.dumps(reference_dict)
    response = api.post(
        url=app.config["domain"] + "/api/references",
        data=ssp_json,
        headers=headers_json,
    )
    if response.status_code == 200:
        ref_id = json.loads(response.text)["id"]
        ref_title = reference_dict["title"]
        log_event(
            record_type="Resource",
            model_layer="Back-matter",
            event_msg=f"Successfully posted reference #: {ref_id} - {ref_title}.",
        )
    else:
        log_error(
            record_type="Resource",
            model_layer="Back-matter",
            event_msg="Problem posting reference.",
        )


def upload_base64_file(file_metadata: dict, filestring: str, ssp_id: int) -> None:
    """
    A function to upload a base64 file to RegScale

    :param dict file_metadata: Metadata for the file to be uploaded
    :param str filestring: The base64 string of the file to be uploaded
    :param int ssp_id: The ID of the SSP to upload the file to
    :rtype: None
    """
    app = Application()
    api = Api()
    decoded_file = base64.b64decode(filestring)
    files = {"file": (file_metadata["trustedDisplayName"], BytesIO(decoded_file))}
    data = {"id": ssp_id, "module": "securityplans"}
    response = api.post(
        url=app.config["domain"] + "/files/file",
        files=files,
        data=data,
    )
    if response.status_code == 200:
        logger.info("File uploaded successfully!")
        logger.debug("Response content:", response.text)
        response_data = json.loads(response.text)

        file_metadata["fullPath"] = (response_data["fullPath"],)
        file_metadata["fileHash"] = (response_data["fileHash"],)
        file_metadata["shaHash"] = (response_data["shaHash"],)
        file_metadata["uploadDate"] = (response_data["uploadDate"],)

        file_metadata_json = json.dumps(file_metadata)
        response = api.post(
            url=app.config["domain"] + "/files",
            data=file_metadata_json,
        )
        if response.status_code == 200:
            logger.info("File entered to database")
            logger.debug(response.text)
        else:
            logger.debug(response.status_code)
            logger.debug(response.text)

    elif response.status_code == 401:
        logger.info("401: Unauthorized")
    else:
        logger.info("File upload failed. Status code:", response.status_code)
        logger.debug("Response content:", response.text)
