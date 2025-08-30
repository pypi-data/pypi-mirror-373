"""XML Utility functions"""

from urllib.parse import urljoin

from lxml import etree

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger


def extract_markup_content(element: etree._Element) -> str:
    """
    Extract the text content from an XML element, including text content from child elements

    :param etree._Element element: The XML element to extract text content from
    :return: String of text content
    :rtype: str
    """
    # List of tags to look for in the content
    markup_tags = [
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ol",
        "ul",
        "pre",
        "table",
        "li",
    ]
    # Initialize a list to store the extracted text content
    content = []
    # Iterate through all the child elements, including text and specific tags
    for child in element.iter():
        # Extract the local name (i.e., the tag name without the namespace) of each child element
        tag_without_namespace = etree.QName(child.tag).localname
        # If the child's tag is one of the specified markup tags, add its text content
        if tag_without_namespace in markup_tags and child.text:
            content.append(child.text.strip())
        # If the child has a tail (text following a tag), add it as well
        if child.tail and child.tail.strip():
            content.append(child.tail.strip())
    # Join the content with newlines and return
    return "\n".join(content).replace("  ", " ").replace("  ", " ")


# Joshua you may or may not agree with putting here. Expect I may need to update SSP from different places. We can talk!
def update_ssp(ssp_updates_dict: dict, ssp_id: int) -> None:
    """
    This function will attempt to PUT any key-value pairs found in the dict as updates to an existing SSP in RegScale
    It assumes that each key corresponds to a valid SSP field. First retrieves existing SSP using ID, then overwrites
    fields as found in updates before submitting as a PUT to update the record.

    :param dict ssp_updates_dict: Object to update SSP with
    :param int ssp_id: SSP ID to update in RegScale
    :rtype: None
    """
    app = Application()
    api = Api()
    config = app.config
    logger = create_logger()
    headers = {"accept": "*/*", "Authorization": config["token"]}
    headers_json = {
        "accept": "*/*",
        "Content-Type": "application/json-patch+json",
        "Authorization": config["token"],
    }

    response = api.get(url=urljoin(config["domain"], f"/api/securityplans/{ssp_id}"), headers=headers)
    if response.ok:
        existing_ssp = response.json()
        for key, value in ssp_updates_dict.items():
            existing_ssp[key] = value
        ssp_json = existing_ssp
        response = api.put(
            url=urljoin(config["domain"], f"/api/securityplans/{ssp_id}"),
            json=ssp_json,
            headers=headers_json,
        )
        if response.ok:
            logger.info(f"Successfully updated SSP {ssp_id} with additional data.")
        else:
            logger.error("Problems updating SSP with latest additional data.")
