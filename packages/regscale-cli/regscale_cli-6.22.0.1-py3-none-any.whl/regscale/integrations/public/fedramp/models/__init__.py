"""Provide bases for OSCAL SSP models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from lxml import etree
from pydantic import BaseModel

from regscale.core.app.logz import create_logger

logger = create_logger()

EXAMPLE_MAPPINGS = [
    {
        "xpath": "/ssp:system-security-plan/ssp:metadata/ssp:system-name",
        "model": "SystemName",
    },
    {
        "xpath": "/ssp:system-security-plan/system-implementation/leveraged-authorization",
        "model": "LeveragedAuthorizations",
    },
]
# SystemNameProcessor


class XMLProcessor(ABC):
    """Parse an XML Element into a RegScale SSP JSON object."""

    def __init__(
        self,
        xpath: str,
        model: Type[BaseModel],
        root: Optional[etree._Element] = None,
        document: Optional[etree._ElementTree] = None,
        document_path: Optional[str] = None,
    ):
        if document_path and not document and not root:
            document = etree.parse(document_path)
            root = document.getroot()
        if document and not root:
            root = document.getroot()
        self.xpath = xpath
        self.model = model
        self.root = root
        self.document = document
        self.document_path = document_path

    @abstractmethod
    def extract_xpath(self) -> Type[BaseModel]:
        """Extract the XML Element from the document."""
        pass


# for mapping in EXAMPLE_MAPPINGS:
#     globals()[f"{mapping['model']}Processor"] = type(XMLProcessor)(
#         mapping["model"] + "Processor",
#         (XMLProcessor,),
#         {"xpath": mapping["xpath"], "model": mapping["model"]},
#     )
