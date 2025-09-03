"""Data model that will be used to validate the input data and that it has the required headers before proceeding."""

import logging
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import pandas as pd
    from regscale.models import Mapping

import json
from pathlib import Path

from regscale.exceptions.validation_exception import ValidationException

logger = logging.getLogger("regscale")
JSON = ".json"
XLSX = ".xlsx"
XLSM = ".xlsm"
CSV = ".csv"
XML = ".xml"
NESSUS = ".nessus"


class ImportValidater:
    """
    Data importer that validates the input data

    :param list required_headers: List of required headers (columns)
    :param Union[str, Path] file_path: Path to the file to import
    :raises ValidationException: If the file type is not supported
    """

    _supported_types = [CSV, XLSX, XLSM, JSON, XML, NESSUS]
    xml_tag = "record"
    keys: Optional[list] = []
    key: Optional[str] = ""
    required_headers: list
    parsed_headers: list
    data: Union["pd.DataFrame", list]
    mapping: "Mapping"
    worksheet_name: Optional[str] = None
    skip_rows: Optional[int] = None
    file_path: Path
    file_type: str
    mapping_file_path: Path
    disable_mapping: bool

    def __init__(
        self,
        required_headers: list,
        file_path: Union[str, Path],
        mapping_file_path: Union[str, Path],
        disable_mapping: bool = False,
        xml_tag: Optional[str] = None,
        key: Optional[str] = None,
        keys: Optional[list] = None,
        worksheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
        prompt: bool = True,
        ignore_unnamed: bool = False,
        warn_extra_headers: bool = True,
    ):
        self.ignore_unnamed = ignore_unnamed
        self.prompt = prompt
        self.required_headers = required_headers
        file_path = self._convert_str_to_path(file_path)
        self.mapping_file_path = self._convert_str_to_path(mapping_file_path)
        self.file_path = file_path
        self.file_type = file_path.suffix
        if not self.mapping_file_path.suffix:
            self.mapping_file_path = Path(self.mapping_file_path / f"{self.file_type[1:]}_mapping.json")
        self.disable_mapping = disable_mapping
        self.xml_tag = xml_tag
        self.key = key
        self.keys = keys
        self.worksheet_name = worksheet_name
        self.skip_rows = skip_rows
        self.warn_extra_headers = warn_extra_headers
        if self.file_type not in self._supported_types:
            raise ValidationException(
                f"Unsupported file type: {self.file_type}, supported types are: {', '.join(self._supported_types)}",
            )
        self._parse_headers()

    @staticmethod
    def _convert_str_to_path(file_path: Union[str, Path]) -> Path:
        """
        Converts a string to a Path object

        :param Union[str, Path] file_path: File path as a string
        :returns: Path object
        :rtype: Path
        """
        if isinstance(file_path, Path):
            return file_path
        return Path(file_path)

    def import_data(self) -> Union["pd.DataFrame", list, dict]:
        """
        Imports the data from the file and returns it

        :returns: Imported data
        :rtype: Union[pd.DataFrame, list, dict]
        """
        if self.file_type == CSV:
            return self.import_csv(self.file_path)
        elif self.file_type == XLSX or self.file_type == XLSM:
            return self.import_xlsx(self.file_path)
        elif self.file_type == JSON:
            return self.import_json(self.file_path)
        elif self.file_type in (XML, NESSUS):
            return self.import_xml(self.file_path, self.xml_tag)

    def _parse_headers(self):
        """
        Parses the headers from the file based on the file type and returns them

        :returns: List of headers
        :rtype: list
        """
        self.data = self.import_data()
        if self.file_type in [CSV, XLSX, XLSM]:
            self.parsed_headers = self.data.columns  # type: ignore
        elif self.file_type == XML:
            self.parsed_headers = list(self.data.keys())
        elif self.file_type == JSON and not self.parsed_headers:
            raise ValidationException(f"Unable to parse headers from JSON file: {self.file_path}")

    def validate_headers(self, headers: Union[list, "pd.Index"]) -> None:
        """
        Validates that all required headers are present

        :param Union[list, pd.Index] headers: List of headers from the file
        """
        import re
        from pandas import Index

        from regscale.models import Mapping

        if isinstance(headers, Index):
            headers = [str(header) for header in headers]  # Convert pd.Index to list of strings

        if not self.ignore_unnamed and any(re.search(r"unnamed", header, re.IGNORECASE) for header in headers):  # type: ignore
            raise ValidationException(
                f"Unable to parse headers from the file. Please ensure the headers are named in {self.file_path}"
                f"\n{', '.join(headers)}"
            )

        if not self.prompt:
            # Let's not prompt the user to find the header, and just raise a validation exception
            missing_headers = [header for header in self.required_headers if header not in headers]
            extra_headers = [header for header in headers if header not in self.required_headers]
            if missing_headers:
                raise ValidationException(
                    f"{', '.join([f'`{header}`' for header in missing_headers])} header(s) not found in {self.file_path}"
                )
            if extra_headers and self.warn_extra_headers:
                logger.warning("Extra headers found in the file: %s", ", ".join(extra_headers))

        if self.disable_mapping:
            logger.debug("Mapping is disabled, using headers as is.")
            self.mapping = Mapping(
                mapping={header: header for header in headers},
                expected_field_names=self.required_headers,
                file_path_for_prompt=self.file_path,
            )
        else:
            logger.debug(f"Mapping is enabled, validating headers for {self.file_path}")
            self.mapping = Mapping.from_file(
                file_path=self.mapping_file_path,
                expected_field_names=self.required_headers,
                mapping={"mapping": {header: header for header in headers}},
                parsed_headers=[header for header in headers],  # this converts the pd.Index to a list
                file_path_for_prompt=self.file_path,
            )

    def import_csv(self, file_path: Union[str, Path]) -> "pd.DataFrame":
        """
        Imports a CSV file and validates headers

        :param file_path: Path to the CSV file
        :returns: DataFrame with the imported data
        :rtype: pd.DataFrame
        """
        import pandas

        try:
            if self.skip_rows:
                df = pandas.read_csv(file_path, skiprows=self.skip_rows - 1, on_bad_lines="warn")
            else:
                df = pandas.read_csv(file_path, on_bad_lines="warn")

            # Check if the DataFrame is empty or has no columns
            if df.empty or len(df.columns) == 0:
                raise ValidationException(
                    f"The CSV file '{file_path}' appears to be empty or has no parseable columns. "
                    f"Please check that:\n"
                    f"1. The file contains data\n"
                    f"2. The file has proper column headers\n"
                    f"3. The skip_rows parameter ({self.skip_rows}) is correct for this file format"
                )

            if self.ignore_unnamed:
                df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        except pandas.errors.EmptyDataError as e:
            raise ValidationException(
                f"The CSV file '{file_path}' is empty or contains no data. "
                f"Please verify the file contains valid CSV data with headers. "
                f"If using skip_rows ({self.skip_rows}), ensure there are enough rows in the file."
            ) from e
        except pandas.errors.ParserError as e:
            raise ValidationException(f"Unable to parse the {CSV} file: {file_path}. Error: {e}") from e

        self.validate_headers(df.columns)
        df = df.fillna("")
        return df

    def import_xlsx(self, file_path: Union[str, Path]) -> "pd.DataFrame":
        """
        Imports an XLSX file and validates headers

        :param Union[str, Path] file_path: Path to the XLSX file
        :returns: DataFrame with the imported data
        :rtype: pd.DataFrame
        """
        import pandas

        try:
            if self.skip_rows and self.worksheet_name:
                df = pandas.read_excel(file_path, sheet_name=self.worksheet_name, skiprows=self.skip_rows - 1)
            elif self.worksheet_name:
                df = pandas.read_excel(file_path, sheet_name=self.worksheet_name)
            elif self.skip_rows:
                df = pandas.read_excel(file_path, skiprows=self.skip_rows - 1)
            else:
                df = pandas.read_excel(file_path)
        except Exception as e:
            raise ValidationException(f"Unable to parse the {XLSX} file: {file_path}\nDetails: {e}")
        self.validate_headers(df.columns)
        df = df.fillna("")
        return df

    def _handle_keys(self, data: dict) -> list:
        """
        Handles the keys for JSON data

        :param dict data: JSON data

        :returns: List of keys
        :rtype: list
        """
        if self.keys:
            value = data
            # iterate each key and see if it is in the data
            for key in self.keys:
                value = value.get(key, {})
            if isinstance(value, dict):
                return list(value.keys())
            elif isinstance(value, list):
                if value:
                    return list(value[0].keys())
                else:
                    raise ValidationException(
                        f"JSON file must contain a key '{self.keys[-1]}' with a list of dictionaries"
                    )

        return data.get(self.key) or data.get(self.keys[0])

    def import_json(self, file_path: Union[str, Path]) -> list:
        """
        Imports a JSON file and validates keys (treated as headers)

        :param file_path: Path to the JSON file
        :raises ValidationException: If the JSON file is empty or not a list of dictionaries
        :returns: List of dictionaries with the imported data
        :rtype: list
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list) and not self.key and not self.keys and data:
            # Assuming JSON is a list of dictionaries
            self.validate_headers(data[0].keys())
            self.parsed_headers = list(data[0].keys())
        elif isinstance(data, list) and self.keys and data:
            # Assuming JSON is a list of dictionaries
            self.validate_headers(self._handle_keys(data[0]))
            self.parsed_headers = list(self._handle_keys(data[0]))
        elif isinstance(data, dict) and (self.key or self.keys):
            if self.keys:
                self.validate_headers(self._handle_keys(data))
                self.parsed_headers = self._handle_keys(data)
            elif findings := data.get(self.key):
                self.validate_headers(findings[0].keys())
                self.parsed_headers = list(findings[0].keys())
        elif isinstance(data, dict):
            self.validate_headers(list(data.keys()))
            self.parsed_headers = list(data.keys())
        else:
            raise ValidationException(f"Unable to parse headers from JSON file: {file_path}")

        return data

    def _remove_at_prefix(self, xml_data: Union[list, dict]) -> Union[list, dict]:
        """
        Recursively remove the '@' prefix from keys in a dictionary

        :param Union[list, dict] xml_data: Parsed XML data, either a dictionary or a list of dictionaries
        :returns: Dictionary with '@' prefix removed or list of dictionaries with '@' prefix removed
        :rtype: Union[list, dict]
        """
        if isinstance(xml_data, dict):
            return {k.lstrip("@"): self._remove_at_prefix(v) for k, v in xml_data.items()}
        elif isinstance(xml_data, list):
            return [self._remove_at_prefix(i) for i in xml_data]
        else:
            return xml_data

    def import_xml(self, file_path: Union[str, Path], record_tag: Optional[str] = None) -> dict:
        """
        Imports an XML file and validates keys (treated as headers)

        :param Union[str, Path] file_path: Path to the XML file
        :param str record_tag: The XML tag that represents a record, defaults to "record"
        :raises ValidationException: If the XML file contains no records
        :returns: Dictionary with the imported data
        :rtype: dict
        """
        import xmltodict

        if isinstance(file_path, str):
            file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            xml_content = file.read()
        try:
            if dict_content := xmltodict.parse(xml_content):
                if record_tag:
                    dict_content = dict_content.get(record_tag)
                dict_content = self._remove_at_prefix(dict_content)
                self.validate_headers(list(dict_content.keys()))
                return dict_content
            else:
                raise ValidationException("XML file contains no records.")
        except xmltodict.expat.ExpatError as e:
            raise ValidationException(
                f"Error parsing {self.file_type.strip('.')} file: {file_path}.\nDetails: {e.args[0]}"
            ) from e
