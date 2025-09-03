"""
This module is used to parse a DOCX file containing FedRAMP Security Controls and their implementation statuses.
"""

import logging
import re
import sys
from typing import Dict, Union, Any, List, Optional

import docx
from lxml import etree
from rapidfuzz import fuzz

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCHEMA = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"  # noqa
TEXT_ELEMENT = ".//{%s}%s" % (SCHEMA, "t")
CHECKBOX_ELEMENT = ".//{%s}%s" % (SCHEMA, "checkBox")
NA_STATUS = "Not Applicable"

# define our statuses we are looking for in the document
STATUSES = [
    "Implemented",
    "Partially Implemented",
    "Planned",
    "In Remediation",
    "Inherited",
    "Alternative Implementation",
    NA_STATUS,
    "Archived",
    "Risk Accepted",
]
LOWER_STATUSES = [status.lower() for status in STATUSES]

ORIGINATIONS = [
    "Service Provider Corporate",
    "Service Provider System Specific",
    "Service Provider Hybrid (Corporate and System Specific)",
    "Configured by Customer (Customer System Specific)",
    "Provided by Customer (Customer System Specific)",
    "Shared (Service Provider and Customer Responsibility)",
    "Inherited from pre-existing FedRAMP Authorization",
]
LOWER_ORIGINATIONS = [origin.lower() for origin in ORIGINATIONS]
DEFAULT_ORIGINATION = "Service Provider Corporate"
POSITIVE_KEYWORDS = [
    "yes",
    "true",
    "1",
    "☒",
    "True",
    "Yes",
    "☑",
    "☑️",
    "✓",
    "✔",
    "✔️",
    "✅",
    "⬜",
    "▣",
    "■",
    "□",
    "⊠",
    "⊗",
    "×",
    "checked",
    "selected",
    "chosen",
]

# Define your keywords or phrases that map to each status
STATUS_KEYWORDS = {
    "Implemented": ["implemented", "complete", "done", "yes", "☒", "1"],
    "Partially Implemented": [
        "partially implemented",
        "incomplete",
        "partially done",
        "partial",
        "In process",
        "in process",
        "☒",
        "1",
    ],
    "Planned": ["planned", "scheduled", "Planned", "☒", "1"],
    "Alternative Implementation": [
        "alternative implementation",
        "alternative",
        "Equivalent",
        "☒",
        "1",
    ],
    NA_STATUS: ["not applicable", "irrelevant", "not relevant", "no", "☒", "1"],
}
DEFAULT_STATUS = "Not Implemented"
CONTROL_ORIGIN_KEY = "Control Origination"
CONTROL_SUMMARY_KEY = "Control Summary Information"

STATEMENT_CHECK = "What is the solution and how is it implemented".lower()
DEFAULT_PART = "Default Part"


class AppendixAParser:
    """
    A class to parse a DOCX file containing FedRAMP Security Controls and their implementation statuses.
    """

    def __init__(self, filename: str):
        self.controls_implementations = {}
        self.control_id = ""
        self.doc = docx.Document(filename)
        self.header_row_text = ""
        self.cell_data_status = None
        self.processed_texts = []
        self.joined_processed_texts = ""
        self.xml = None
        self.text_elements = None
        self.checkbox_states = None
        self.cell_data = {}
        self.parts = self.generate_parts_full_alphabet()
        self.parts_set = {p.lower() for p in self.parts}

    def fetch_controls_implementations(self) -> Dict:
        """
        Fetch the implementation statuses of the controls from the DOCX file.
        :return: A dictionary containing the control IDs and their implementation statuses.
        :rtype: Dict

        """
        return self.get_implementation_statuses()

    @staticmethod
    def score_similarity(string1: str, string2: str) -> int:
        """
        Score the similarity between two strings using the RapidFuzz library.
        :param str string1: The first string to compare.
        :param str string2: The second string to compare.
        :return: The similarity score between the two strings.
        :rtype: int
        """
        # Scoring the similarity
        score = fuzz.ratio(string1.lower(), string2.lower())

        # Optionally, convert to a percentage
        percentage = score  # fuzz.ratio already gives a score out of 100

        return round(percentage)

    @staticmethod
    def determine_origination(text: str) -> Optional[str]:
        """
        Determine the origination from the text. Multiple originations may be found and
        returned as a comma-separated string.

        :param str text: The text to analyze for origination values
        :return: Comma-separated string of origination values or None if none found
        :rtype: Optional[str]
        """
        if CONTROL_ORIGIN_KEY not in text:
            return None

        # Clean and standardize the text for processing
        lower_text = AppendixAParser._clean_text_for_processing(text)

        # Find all matching originations
        found_originations = AppendixAParser._find_originations_in_text(lower_text)

        if found_originations:
            return ",".join(found_originations)
        return None

    @staticmethod
    def _clean_text_for_processing(text: str) -> str:
        """
        Clean and standardize text for processing.

        :param str text: The text to clean
        :return: Cleaned and standardized text
        :rtype: str
        """
        tokens = text.split()
        rejoined_text = " ".join(tokens)  # this removes any newlines or spaces
        rejoined_text = rejoined_text.replace("( ", "(")
        rejoined_text = rejoined_text.replace(" )", ")")
        return rejoined_text.lower()

    @staticmethod
    def _find_originations_in_text(lower_text: str) -> List[str]:
        """
        Find all originations in the text.

        :param str lower_text: The lowercase text to search for originations
        :return: List of found originations
        :rtype: List[str]
        """
        # Common checkbox characters in various fonts and styles
        checkbox_chars = ["☒", "☑", "☑️", "✓", "✔", "✔️", "✅", "⬜", "▣", "■", "□", "⊠", "⊗", "×"]

        found_originations = []

        for origin in ORIGINATIONS:
            if AppendixAParser._check_origin_with_keywords(origin, lower_text):
                found_originations.append(origin)
                continue

            if AppendixAParser._check_origin_with_checkbox_chars(origin, lower_text, checkbox_chars):
                found_originations.append(origin)
                continue

            if AppendixAParser._check_origin_with_text_patterns(origin, lower_text):
                found_originations.append(origin)

        return found_originations

    @staticmethod
    def _check_origin_with_keywords(origin: str, lower_text: str) -> bool:
        """
        Check if origin is indicated with known keywords.

        :param str origin: The origin to check for
        :param str lower_text: The text to search in
        :return: True if origin is found with keywords, False otherwise
        :rtype: bool
        """
        for keyword in POSITIVE_KEYWORDS:
            # Check with space between checkbox and origin
            valid_option_with_space = f"{keyword} {origin}".lower()
            # Check without space between checkbox and origin
            valid_option_without_space = f"{keyword}{origin}".lower()

            if valid_option_with_space in lower_text or valid_option_without_space in lower_text:
                return True
        return False

    @staticmethod
    def _check_origin_with_checkbox_chars(origin: str, lower_text: str, checkbox_chars: List[str]) -> bool:
        """
        Check if origin is indicated with checkbox characters.

        :param str origin: The origin to check for
        :param str lower_text: The text to search in
        :param List[str] checkbox_chars: List of checkbox characters to check for
        :return: True if origin is found with checkbox characters, False otherwise
        :rtype: bool
        """
        for char in checkbox_chars:
            # Check with and without space
            if f"{char} {origin}".lower() in lower_text or f"{char}{origin}".lower() in lower_text:
                return True
        return False

    @staticmethod
    def _check_origin_with_text_patterns(origin: str, lower_text: str) -> bool:
        """
        Check if origin is indicated with text patterns.

        :param str origin: The origin to check for
        :param str lower_text: The text to search in
        :return: True if origin is found with text patterns, False otherwise
        :rtype: bool
        """
        # Look for patterns like "X is checked" or "X is selected"
        check_patterns = [
            f"{origin.lower()} is checked",
            f"{origin.lower()} is selected",
            f"{origin.lower()} (checked)",
            f"{origin.lower()} (selected)",
            f"selected: {origin.lower()}",
        ]
        return any(pattern in lower_text for pattern in check_patterns)

    @staticmethod
    def determine_status(text: str) -> str:
        """
        Determine the implementation status from the text.
        :param str text: The text to analyze for implementation status
        :return: The determined implementation status
        :rtype: str
        """
        # Tokenize the input text
        tokens = text.split()

        # Convert tokens to a single lowercased string for comparison
        token_string = " ".join(tokens).lower()

        matches = []

        # Common checkbox characters in various fonts and styles
        checkbox_chars = ["☒", "☑", "☑️", "✓", "✔", "✔️", "✅", "⬜", "▣", "■", "□", "⊠", "⊗", "×"]

        # Search for keywords in the tokenized text to determine the status
        for status, keywords in STATUS_KEYWORDS.items():
            for keyword in keywords:
                # Check patterns with space: "1 keyword" or "☒ keyword" or any other checkbox char
                if f"1 {keyword}" in token_string or any(
                    f"{char} {keyword}" in token_string for char in checkbox_chars
                ):
                    matches.append(status)
                    break

                # Check patterns without space: "1keyword" or "☒keyword" or any other checkbox char
                elif f"1{keyword}" in token_string or any(
                    f"{char}{keyword}" in token_string for char in checkbox_chars
                ):
                    matches.append(status)
                    break

                # Also check for direct True/Yes values next to keywords
                elif any(pos + keyword in token_string for pos in ["true", "yes"]):
                    matches.append(status)
                    break

        # Determine the status to return
        if len(matches) > 1:
            # More than one match found
            # Not applicable takes precedence over planned/partially implemented (only 2 valid multi select statuses for fedramp)
            if NA_STATUS in matches:
                return NA_STATUS
            else:
                return matches[0]
        elif matches:
            return matches[0]  # Return the first match if only one
        else:
            # Extra fallback for unusual checkbox patterns
            # Look for any checkbox-like character anywhere in the text without keywords
            for status, keywords in STATUS_KEYWORDS.items():
                for keyword in keywords:
                    # Skip the checkbox characters themselves (already checked above)
                    if keyword in checkbox_chars:
                        continue

                    # Check if any checkbox character is present in the text alongside common implementation terms
                    if any(char in token_string for char in checkbox_chars) and keyword in token_string:
                        return status

            return DEFAULT_STATUS  # No matches found

    @staticmethod
    def _process_text_element(input_text: str) -> Union[Dict, str]:
        """
        Process a text element from a DOCX cell, checking for structured checkbox information.
        :param str input_text: The text content of the element.
        :return: The processed text or a dictionary containing checkbox information.
        :rtype: Union[Dict, str]
        """
        # Check if the text contains structured checkbox information
        checkbox_info = re.findall(r"\[(.*?): (True|False)\]", input_text)
        if checkbox_info:
            return {item[0].strip(): item[1] == "True" for item in checkbox_info}
        else:
            return input_text

    @staticmethod
    def _get_checkbox_state(checkbox_element: Any) -> bool:
        """
        Get the state of a checkbox element from a DOCX cell.
        :param Any checkbox_element: The checkbox element from the DOCX cell.
        :return: The state of the checkbox.
        :rtype: bool
        """
        # Try different methods to determine checkbox state
        methods = [
            AppendixAParser._check_direct_val_attribute,
            AppendixAParser._check_checked_element,
            AppendixAParser._check_default_element,
            AppendixAParser._check_child_elements,
            AppendixAParser._check_attributes,
            AppendixAParser._check_namespace_attributes,
        ]

        for method in methods:
            result = method(checkbox_element)
            if result is not None:
                return result

        # If none of the methods worked, return False
        return False

    @staticmethod
    def _check_direct_val_attribute(element: Any) -> Optional[bool]:
        """Check if element has a direct 'val' attribute."""
        val = "{%s}%s" % (SCHEMA, "val")
        state = element.get(val)
        if state is not None:
            return state == "1"
        return None

    @staticmethod
    def _check_checked_element(element: Any) -> Optional[bool]:
        """Check if element has a 'checked' child with a 'val' attribute."""
        val = "{%s}%s" % (SCHEMA, "val")
        checked = "{%s}%s" % (SCHEMA, "checked")
        return AppendixAParser._check_element_with_val(element, checked, val)

    @staticmethod
    def _check_default_element(element: Any) -> Optional[bool]:
        """Check if element has a 'default' child with a 'val' attribute."""
        val = "{%s}%s" % (SCHEMA, "val")
        default = "{%s}%s" % (SCHEMA, "default")
        return AppendixAParser._check_element_with_val(element, default, val)

    @staticmethod
    def _check_element_with_val(parent: Any, child_tag: str, val_tag: str) -> Optional[bool]:
        """
        Check if a child element has a 'val' attribute.

        :param Any parent: The parent element
        :param str child_tag: The child element tag
        :param str val_tag: The value attribute tag
        :return: True if val is "1", False if val is not "1", None if element or val not found
        :rtype: Optional[bool]
        """
        child_element = parent.find(child_tag)
        if child_element is not None:
            state = child_element.get(val_tag)
            if state is not None:
                return state == "1"
        return None

    @staticmethod
    def _check_child_elements(element: Any) -> Optional[bool]:
        """Check all child elements for a 'val' attribute."""
        val = "{%s}%s" % (SCHEMA, "val")
        try:
            for child in element.getchildren():
                if child.get(val) is not None:
                    return child.get(val) == "1"
        except (AttributeError, TypeError):
            pass
        return None

    @staticmethod
    def _check_attributes(element: Any) -> Optional[bool]:
        """Check all attributes for check-related names."""
        try:
            for attr_name, attr_value in element.attrib.items():
                if "checked" in attr_name.lower() or "val" in attr_name.lower() or "state" in attr_name.lower():
                    return attr_value in ["1", "true", "checked", "on"]
        except (AttributeError, TypeError):
            pass
        return None

    @staticmethod
    def _check_namespace_attributes(element: Any) -> Optional[bool]:
        """Check attributes in all namespaces."""
        try:
            for ns, uri in element.nsmap.items():
                for attr_name in ["val", "checked", "state", "default"]:
                    attr_with_ns = "{%s}%s" % (uri, attr_name)
                    if element.get(attr_with_ns) is not None:
                        return element.get(attr_with_ns) in ["1", "true", "checked", "on"]
        except (AttributeError, TypeError):
            pass
        return None

    def get_implementation_statuses(self) -> Dict:
        """
        Get the implementation statuses of the controls from the DOCX file.
        :return: A dictionary containing the control IDs and their implementation statuses.
        :rtype: Dict
        """
        for table in self.doc.tables:
            for i, row in enumerate(table.rows):
                self._handle_row(i, row)

        logger.debug(f"Found {len(self.controls_implementations.items())} Controls")
        return self.controls_implementations

    def _handle_row(self, i: int, row: Any):
        """
        Handle a row in the DOCX table.
        :param int i: The index of the row.
        :param Any row: The row element from the DOCX table.
        """
        self.header_row_text = " ".join([c.text.strip() for c in row.cells]) if i == 0 else self.header_row_text
        if CONTROL_SUMMARY_KEY.lower() in self.header_row_text.lower():
            self.control_id = self.header_row_text.split(" ")[0] if self.header_row_text else None
            if self.control_id not in self.controls_implementations:
                self.controls_implementations[self.control_id] = {}

        cells = row.cells
        cell_count = len(cells)
        self.handle_row_parts(cells, cell_count)
        for cell_index, cell in enumerate(row.cells):
            self._handle_cell(cell)

    def handle_row_parts(self, cells: Any, cell_count: int) -> None:
        """
        Handle the parts of the control implementation.
        :param Any cells: The cells in the DOCX row.
        :param int cell_count: The number of cells in the row.
        :return: None
        :rtype: None
        """
        check = "what is the solution and how is it implemented".lower()
        if check not in self.header_row_text.lower():
            return
        control_dict = self.controls_implementations.get(self.control_id, {})
        self.handle_part(cells, cell_count, control_dict, check)

    def handle_part(self, cells: Any, cell_count: int, control_dict: Dict, check: str):
        """
        Handle the parts of the control implementation.
        :param Any cells: The cells in the DOCX row.
        :param int cell_count: The number of cells in the row.
        :param Dict control_dict: The dictionary containing the control implementation data.
        :param str check: The check string to exclude from the part value.
        """
        part_list = control_dict.get("parts", [])

        if cell_count > 1:
            self._handle_multicolumn_part(cells, part_list, check)
        else:
            self._handle_single_column_part(cells[0], part_list, check)

        control_dict["parts"] = part_list

    def _handle_multicolumn_part(self, cells: Any, part_list: List, check: str):
        """
        Handle a part with multiple columns.

        :param Any cells: The cells in the row.
        :param List part_list: List to add parts to.
        :param str check: The check string to exclude from part value.
        """
        name = self.get_cell_text(cells[0]) if cells[0].text else DEFAULT_PART
        value = self.get_cell_text(cells[1])
        val_dict = {"name": name, "value": value}
        if check not in value.lower() and val_dict not in part_list:
            part_list.append(val_dict)

    def _handle_single_column_part(self, cell: Any, part_list: List, check: str):
        """
        Handle a part with a single column.

        :param Any cell: The cell to process.
        :param List part_list: List to add parts to.
        :param str check: The check string to exclude from part value.
        """
        value = self.get_cell_text(cell)
        value_lower = value.lower()

        # Find part name using regex pattern
        name = self._extract_part_name(value_lower)

        val_dict = {"name": name, "value": value}
        if check.lower() not in value_lower and val_dict not in part_list:
            part_list.append(val_dict)

    def _extract_part_name(self, text: str) -> str:
        """
        Extract part name from text using regex.

        :param str text: The text to extract from.
        :return: The extracted part name or default part name.
        :rtype: str
        """
        pattern = re.compile(r"\b(" + "|".join(re.escape(part) for part in self.parts_set) + r")\b", re.IGNORECASE)
        match = pattern.search(text)
        return match.group(1) if match else DEFAULT_PART

    def set_cell_text(self, cell: Any):
        """
        Set the text content of the cell and process it.
        :param Any cell: The cell element from the DOCX table.
        """
        processed_texts = ""
        self.xml = etree.fromstring(cell._element.xml)
        self.text_elements = self.xml.findall(TEXT_ELEMENT)
        self.checkbox_states = self.xml.findall(CHECKBOX_ELEMENT)
        for element in self.text_elements:
            if element.text:
                processed_texts += self._process_text_element(element.text)
        self.joined_processed_texts = re.sub(r"\.(?!\s|\d|$)", ". ", processed_texts)

    def get_cell_text(self, cell: Any) -> str:
        """
        Get the text content of the cell.
        :param Any cell: The cell element from the DOCX table.
        :return: The text content of the cell.
        :rtype: str
        """
        processed_texts = ""
        xml = etree.fromstring(cell._element.xml)
        text_elements = xml.findall(TEXT_ELEMENT)
        for element in text_elements:
            if element.text:
                processed_texts += self._process_text_element(element.text)
        return re.sub(r"\.(?!\s|\d|$)", ". ", processed_texts)

    def _handle_cell(self, cell: Any):
        """
        Handle a cell in the DOCX table.
        :param Any cell: The cell element from the DOCX table.
        """
        self.set_cell_text(cell)
        self.cell_data = {}
        self._handle_params()
        self.cell_data_status = None
        self._handle_checkbox_states()
        self._handle_implementation_status()
        self._handle_implementation_origination()
        self._handle_implementation_statement()
        # Comment out the implementation parts handling as it requires parameters not available in this context
        # We'll rely on the handle_row_parts method to handle parts instead
        # self._handle_implementation_parts(cell_index, cells)
        self._handle_responsibility()

    def _handle_params(self):
        """
        Handle the parameters of the control implementation.
        """
        if (
            CONTROL_SUMMARY_KEY.lower() in self.header_row_text.lower()
            and "parameter" in self.joined_processed_texts.lower()
            and self.control_id in self.controls_implementations
        ):
            control_dict = self.controls_implementations[self.control_id]
            if "parameters" not in control_dict:
                control_dict["parameters"] = []
            # split the first occurrence of : to get the parameter name and value
            parts = self.joined_processed_texts.split(":", 1)
            param_text = self.joined_processed_texts
            param = {"name": "Default Name", "value": "Default Value"}
            if len(parts) == 2:
                param["name"] = parts[0].strip().replace("Parameter", "")
                param["value"] = parts[1].strip()
                if param not in control_dict["parameters"]:
                    control_dict["parameters"].append(param)
            else:
                param["value"] = param_text.replace("parameters", "").strip()
                if param not in control_dict["parameters"]:
                    control_dict["parameters"].append(param)

    def _handle_implementation_origination(self):
        """
        Handle the origination of the control implementation.
        """
        origination_values = []

        # Check if we're in a Control Summary section and have Control Origination text
        if (
            CONTROL_SUMMARY_KEY.lower() in self.header_row_text.lower()
            and CONTROL_ORIGIN_KEY.lower() in self.joined_processed_texts.lower()
            and self.control_id in self.controls_implementations
            and self.controls_implementations[self.control_id] is not None
        ):
            # Method 1: Check cell_data for origination values based on checkbox states
            for key, value in self.cell_data.items():
                if value and any(origin.lower() in key.lower() for origin in ORIGINATIONS):
                    # Find the matching origination from the known list
                    for origin in ORIGINATIONS:
                        if origin.lower() in key.lower():
                            logger.debug(f"Found origination from checkbox: {origin}")
                            if origin not in origination_values:
                                origination_values.append(origin)
                            break

            # Method 2: Try determine_origination as backup
            if orig := self.determine_origination(self.joined_processed_texts):
                logger.debug(f"Found origination from text: {orig}")
                # Handle multiple comma-separated values in the determine_origination result
                for origin in orig.split(","):
                    if origin.strip() and origin.strip() not in origination_values:
                        origination_values.append(origin.strip())

            # Save all origination values as comma-delimited string
            if origination_values:
                control_dict = self.controls_implementations[self.control_id]
                control_dict["origination"] = ",".join(origination_values)
                logger.debug(f"Setting origination for {self.control_id}: {control_dict['origination']}")
            elif DEFAULT_ORIGINATION:
                # Set default if none found
                control_dict = self.controls_implementations[self.control_id]
                control_dict["origination"] = DEFAULT_ORIGINATION
                logger.debug(f"Setting default origination for {self.control_id}: {DEFAULT_ORIGINATION}")

    def _handle_implementation_status(self):
        """
        Handle the implementation status of the control.
        """
        if (
            self.cell_data_status
            and self.cell_data_status.lower() in LOWER_STATUSES
            and CONTROL_SUMMARY_KEY in self.header_row_text
        ):
            # logger.debug(header_row_text)
            if self.control_id in self.controls_implementations:
                control_dict = self.controls_implementations[self.control_id]
                control_dict["status"] = self.cell_data_status
        elif status := self.determine_status(self.joined_processed_texts):
            if status.lower() in LOWER_STATUSES and CONTROL_SUMMARY_KEY in self.header_row_text:
                if self.control_id in self.controls_implementations:
                    control_dict = self.controls_implementations[self.control_id]
                    control_dict["status"] = status

    def _handle_implementation_statement(self):
        """
        Handle the implementation statement of the control.
        """

        value_check = f"{self.control_id} What is the solution and how is it implemented?"
        if (
            STATEMENT_CHECK in self.header_row_text.lower()
            and value_check.lower() != self.joined_processed_texts.lower()
            and self.control_id in self.controls_implementations
        ):
            control_dict = self.controls_implementations.get(self.control_id, {})
            imp_list = control_dict.get("statement", [])
            if (
                self.joined_processed_texts.strip() != ""
                and STATEMENT_CHECK not in self.joined_processed_texts.strip().lower()
            ):
                imp_list.append(self.joined_processed_texts.strip())
            control_dict["statement"] = imp_list

    @staticmethod
    def generate_parts_full_alphabet() -> List[str]:
        """
        Generates a list of strings in the format "part {letter}"
        for each letter of the alphabet from 'a' to 'z'.

        :return: A list of strings in the format "part {letter}"
        :rtype: List[str]
        """
        # Use chr to convert ASCII codes to letters: 97 is 'a', 122 is 'z'
        parts = [f"part {chr(letter)}" for letter in range(97, 122 + 1)]
        return parts

    def _handle_implementation_parts(self, cell_index: int, cells: Any):
        """
        Handle the implementation statement of the control.
        """
        value_check = f"{self.control_id} What is the solution and how is it implemented?"
        generic_value_check = "What is the solution and how is it implemented".lower()

        # Skip processing if conditions aren't met
        if not self._should_process_parts(value_check, generic_value_check):
            return

        part_value = self.joined_processed_texts.strip()
        control_dict = self.controls_implementations.get(self.control_id, {})
        part_list = control_dict.get("parts", [])

        # Check if this is a part declaration
        if not self._is_part_declaration(part_value):
            return

        part_name = part_value.strip() or DEFAULT_PART
        part_value = self._combine_part_text(part_name, part_value, cell_index, cells)

        # Build the part dictionary
        self.build_part_dict(
            part_name=part_name,
            part_value=part_value,
            control_dict=control_dict,
            part_list=part_list,
            generic_value_check=generic_value_check,
        )

    def _should_process_parts(self, value_check: str, generic_value_check: str) -> bool:
        """
        Determine if parts processing should continue.

        :param str value_check: Value check string for this specific control
        :param str generic_value_check: Generic value check string
        :return: True if processing should continue, False otherwise
        :rtype: bool
        """
        return (
            generic_value_check in self.header_row_text.lower()
            and value_check.lower() != self.joined_processed_texts.lower()
            and self.control_id in self.controls_implementations
        )

    def _is_part_declaration(self, part_value: str) -> bool:
        """
        Check if the value is a part declaration.

        :param str part_value: The value to check
        :return: True if it's a part declaration, False otherwise
        :rtype: bool
        """
        return any(
            [
                part_value.strip().lower() == p.lower() or part_value.strip().lower() == f"{p.lower()}:"
                for p in self.parts
            ]
        )

    def _combine_part_text(self, part_name: str, part_value: str, cell_index: int, cells: Any) -> str:
        """
        Combine part text from potentially multiple cells.

        :param str part_name: Name of the part
        :param str part_value: Current value text
        :param int cell_index: Current cell index
        :param Any cells: All cells in the row
        :return: Combined part text
        :rtype: str
        """
        next_cell_text = self.get_cell_text(cells[cell_index + 1])

        if ":" not in part_value:
            # If part_value doesn't have a colon, add the next cell's text after a colon
            return ": ".join([part_value.strip(), next_cell_text.strip()])
        else:
            # If part_value already has a colon, just add the next cell's text
            return " ".join([part_value.strip(), next_cell_text.strip()])

    def build_part_dict(
        self, part_name: str, part_value: str, control_dict: Dict, part_list: List, generic_value_check: str
    ):
        """
        Build a dictionary for a part of the control implementation.
        :param str part_name: The name of the part.
        :param str part_value: The value of the part.
        :param Dict control_dict: The dictionary containing the control implementation data.
        :param List part_list: The list of parts in the control implementation.
        :param str generic_value_check: The generic value check string.
        """
        if part_value.lower().startswith("part"):
            self._handle_part_value_starting_with_part(part_name, part_value, part_list, generic_value_check)
        elif generic_value_check not in part_value.lower():
            # For values that don't start with "part" but are valid
            pdict = {
                "name": DEFAULT_PART,
                "value": part_value.strip(),
            }
            self.add_to_list(new_dict=pdict, the_list=part_list)

        control_dict["parts"] = part_list

    def _handle_part_value_starting_with_part(
        self, part_name: str, part_value: str, part_list: List, generic_value_check: str
    ):
        """
        Handle part values that start with "part".

        :param str part_name: The name of the part
        :param str part_value: The value of the part
        :param List part_list: The list to add parts to
        :param str generic_value_check: The generic value check string
        """
        parts = part_value.split(":", 1)
        part_dict = {"name": part_name, "value": DEFAULT_PART}

        if len(parts) == 2 and parts[1].strip() != "":
            # If part value has a colon and content after it
            part_dict["name"] = parts[0].strip()
            part_dict["value"] = parts[1].strip()
            logger.debug(f"Part: {part_dict}")
            self.add_to_list(new_dict=part_dict, the_list=part_list)
        elif part_value.strip() != "" and generic_value_check not in part_value.lower():
            # If part value has no colon but is not empty and not the generic check
            part_dict["value"] = part_value.strip()
            self.add_to_list(new_dict=part_dict, the_list=part_list)

    @staticmethod
    def add_to_list(new_dict: Dict, the_list: List):
        """
        Add a value to a list in the control dictionary.
        :param Dict new_dict: The new dictionary to add to the list.
        :param List the_list: The list to add the dictionary to.
        """
        if new_dict not in the_list:
            the_list.append(new_dict)

    def _handle_responsibility(self):
        """
        Handle the responsible roles of the control.
        """
        if (
            CONTROL_SUMMARY_KEY.lower() in self.header_row_text.lower()
            and self.control_id in self.controls_implementations
            and self.joined_processed_texts.lower().startswith("responsible role:")
        ):
            control_dict = self.controls_implementations.get(self.control_id, {})
            parts = self.joined_processed_texts.split(":")
            if len(parts) == 2:
                control_dict["responsibility"] = parts[1].strip()

    def _handle_checkbox_states(self):
        """
        Handle the checkbox states in the DOCX table.
        """
        try:
            # Get checkbox states
            updated_checkbox_states = []
            for checkbox in self.checkbox_states:
                try:
                    is_checked = self._get_checkbox_state(checkbox)
                    updated_checkbox_states.append(is_checked)
                    logger.debug(f"Checkbox state: {is_checked}")
                except Exception as e:
                    # If we can't determine the state, assume it's not checked
                    logger.debug(f"Error getting checkbox state: {e}")
                    updated_checkbox_states.append(False)

            # Log total checkboxes found
            logger.debug(f"Found {len(updated_checkbox_states)} checkbox states: {updated_checkbox_states}")

            # First handle any dictionary items in processed_texts
            for item in self.processed_texts:
                if isinstance(item, dict):
                    self.cell_data.update(item)

            # Handle text items with corresponding checkbox states
            text_items = [item for item in self.processed_texts if not isinstance(item, dict)]

            # Match checkbox states to text items
            for i, item in enumerate(text_items):
                if i < len(updated_checkbox_states):
                    self.cell_data[item.strip()] = updated_checkbox_states[i]
                else:
                    # If we have more text items than checkbox states, assume unchecked
                    self.cell_data[item.strip()] = False

            # Also check for checkbox character directly in text
            for key in list(self.cell_data.keys()):
                # If text contains a checkbox character and state is False, try to determine true state from text
                if not self.cell_data[key]:
                    checkbox_chars = ["☒", "☑", "☑️", "✓", "✔", "✔️", "✅", "⬜", "▣", "■", "□", "⊠", "⊗", "×"]
                    if any(char in key for char in checkbox_chars):
                        self.cell_data[key] = True

            # Update cell data status
            self._get_cell_data_status()

        except Exception as e:
            logger.debug(f"Error in _handle_checkbox_states: {e}")
            # Ensure we don't leave checkbox_states empty
            if not hasattr(self, "cell_data") or self.cell_data is None:
                self.cell_data = {}

    def _get_cell_data_status(self):
        """
        Get the status of the cell data.
        """
        if self.cell_data != {}:
            for k, v in self.cell_data.items():
                if v:
                    self.cell_data_status = k
