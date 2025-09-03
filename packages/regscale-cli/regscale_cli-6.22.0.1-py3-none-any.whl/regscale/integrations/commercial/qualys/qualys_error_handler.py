#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qualys Error Handler

This module provides comprehensive error handling for Qualys API responses
and XML parsing. It handles various error codes and conditions that can be
returned by the Qualys API.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple, Union, Any
import xmltodict
from requests import Response

logger = logging.getLogger("regscale")


class QualysErrorCode:
    """Qualys API error codes and their meanings"""

    # Authentication errors
    INVALID_LOGIN = "999"
    AUTHENTICATION_FAILED = "1001"
    INVALID_USERNAME_PASSWORD = "1002"
    ACCOUNT_DISABLED = "1003"

    # Authorization errors
    INSUFFICIENT_PRIVILEGES = "2001"
    FEATURE_NOT_ENABLED = "2002"
    API_ACCESS_DISABLED = "2003"

    # Request errors
    INVALID_REQUEST = "3001"
    MISSING_REQUIRED_PARAMETER = "3002"
    INVALID_PARAMETER_VALUE = "3003"
    REQUEST_TOO_LARGE = "3004"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "4001"
    CONCURRENT_LIMIT_EXCEEDED = "4002"

    # Server errors
    INTERNAL_SERVER_ERROR = "5001"
    SERVICE_UNAVAILABLE = "5002"
    TIMEOUT = "5003"
    DATABASE_ERROR = "5004"

    # Data errors
    NO_DATA_FOUND = "6001"
    DATA_PROCESSING_ERROR = "6002"
    INVALID_DATA_FORMAT = "6003"


class QualysErrorHandler:
    """Handler for Qualys API errors and XML parsing issues"""

    ERROR_CODE_MESSAGES = {
        QualysErrorCode.INVALID_LOGIN: "Invalid login credentials",
        QualysErrorCode.AUTHENTICATION_FAILED: "Authentication failed",
        QualysErrorCode.INVALID_USERNAME_PASSWORD: "Invalid username or password",
        QualysErrorCode.ACCOUNT_DISABLED: "Account is disabled",
        QualysErrorCode.INSUFFICIENT_PRIVILEGES: ("Insufficient privileges for this operation"),
        QualysErrorCode.FEATURE_NOT_ENABLED: "Required feature is not enabled",
        QualysErrorCode.API_ACCESS_DISABLED: "API access is disabled",
        QualysErrorCode.INVALID_REQUEST: "Invalid request format",
        QualysErrorCode.MISSING_REQUIRED_PARAMETER: "Missing required parameter",
        QualysErrorCode.INVALID_PARAMETER_VALUE: "Invalid parameter value",
        QualysErrorCode.REQUEST_TOO_LARGE: "Request is too large",
        QualysErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
        QualysErrorCode.CONCURRENT_LIMIT_EXCEEDED: ("Concurrent request limit exceeded"),
        QualysErrorCode.INTERNAL_SERVER_ERROR: "Internal server error",
        QualysErrorCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
        QualysErrorCode.TIMEOUT: "Request timeout",
        QualysErrorCode.DATABASE_ERROR: "Database error",
        QualysErrorCode.NO_DATA_FOUND: "No data found",
        QualysErrorCode.DATA_PROCESSING_ERROR: "Data processing error",
        QualysErrorCode.INVALID_DATA_FORMAT: "Invalid data format",
    }

    RETRY_CODES = {
        QualysErrorCode.RATE_LIMIT_EXCEEDED,
        QualysErrorCode.CONCURRENT_LIMIT_EXCEEDED,
        QualysErrorCode.SERVICE_UNAVAILABLE,
        QualysErrorCode.TIMEOUT,
        QualysErrorCode.DATABASE_ERROR,
    }

    FATAL_CODES = {
        QualysErrorCode.INVALID_LOGIN,
        QualysErrorCode.AUTHENTICATION_FAILED,
        QualysErrorCode.INVALID_USERNAME_PASSWORD,
        QualysErrorCode.ACCOUNT_DISABLED,
        QualysErrorCode.INSUFFICIENT_PRIVILEGES,
        QualysErrorCode.API_ACCESS_DISABLED,
    }

    @staticmethod
    def validate_response(response: Response) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate a Qualys API response and check for errors.

        :param Response response: HTTP response from Qualys API
        :return: Tuple of (is_valid, error_message, parsed_data)
        :rtype: Tuple[bool, Optional[str], Optional[Dict[str, Any]]]
        """
        if not response:
            return False, "No response received from Qualys API", None

        if not response.ok:
            return False, f"HTTP {response.status_code}: {response.text}", None

        if not response.text:
            return False, "Empty response from Qualys API", None

        # Try to parse the XML response
        try:
            parsed_data = xmltodict.parse(response.text)

            # Check for Qualys-specific errors in the parsed data
            error_info = QualysErrorHandler._check_qualys_errors(parsed_data)
            if error_info:
                return False, error_info, parsed_data

            return True, None, parsed_data

        except Exception as e:
            logger.error(f"Failed to parse Qualys response as XML: {e}")
            return False, f"XML parsing error: {e}", None

    @staticmethod
    def _check_qualys_errors(parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Check parsed XML data for Qualys-specific error conditions.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :return: Error message if found, None otherwise
        :rtype: Optional[str]
        """
        # Check for SIMPLE_RETURN error format
        simple_return_error = QualysErrorHandler._check_simple_return_errors(parsed_data)
        if simple_return_error:
            return simple_return_error

        # Check for HOST_LIST_VM_DETECTION_OUTPUT errors
        detection_error = QualysErrorHandler._check_detection_output_errors(parsed_data)
        if detection_error:
            return detection_error

        # Check for other common error patterns
        return QualysErrorHandler._check_common_error_patterns(parsed_data)

    @staticmethod
    def _check_simple_return_errors(parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Check for SIMPLE_RETURN error format.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :return: Error message if found, None otherwise
        :rtype: Optional[str]
        """
        if "SIMPLE_RETURN" not in parsed_data:
            return None

        simple_return = parsed_data["SIMPLE_RETURN"]
        response = simple_return.get("RESPONSE", {})

        if "TEXT" not in response:
            return None

        error_text = response["TEXT"]
        logger.error(f"Qualys API error: {error_text}")

        if "CODE" in response:
            error_code = response["CODE"]
            return QualysErrorHandler._format_error_message(error_code, error_text)

        return f"Qualys API error: {error_text}"

    @staticmethod
    def _check_detection_output_errors(parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Check for HOST_LIST_VM_DETECTION_OUTPUT errors.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :return: Error message if found, None otherwise
        :rtype: Optional[str]
        """
        if "HOST_LIST_VM_DETECTION_OUTPUT" not in parsed_data:
            return None

        output = parsed_data["HOST_LIST_VM_DETECTION_OUTPUT"]
        response = output.get("RESPONSE", {})

        # Check for error text in the response
        if "TEXT" in response and "error" in str(response["TEXT"]).lower():
            error_text = response["TEXT"]
            logger.error(f"Qualys detection output error: {error_text}")
            return f"Qualys detection error: {error_text}"

        # Check for warning messages (non-fatal)
        QualysErrorHandler._log_warnings_if_present(response)
        return None

    @staticmethod
    def _log_warnings_if_present(response: Dict[str, Any]) -> None:
        """
        Log warning messages if present in response.

        :param Dict[str, Any] response: Response data
        """
        if "WARNING" not in response:
            return

        warning = response["WARNING"]
        if isinstance(warning, dict) and "TEXT" in warning:
            warning_text = warning["TEXT"]
            logger.warning(f"Qualys API warning: {warning_text}")

    @staticmethod
    def _check_common_error_patterns(parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Check for other common error patterns.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :return: Error message if found, None otherwise
        :rtype: Optional[str]
        """
        error_patterns = [
            ("ERROR", "error"),
            ("FAULT", "fault"),
            ("EXCEPTION", "exception"),
        ]

        for pattern_key, pattern_name in error_patterns:
            error_message = QualysErrorHandler._check_error_pattern(parsed_data, pattern_key, pattern_name)
            if error_message:
                return error_message

        return None

    @staticmethod
    def _check_error_pattern(parsed_data: Dict[str, Any], pattern_key: str, pattern_name: str) -> Optional[str]:
        """
        Check for a specific error pattern in parsed data.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :param str pattern_key: Key to look for in the data
        :param str pattern_name: Human-readable name for the pattern
        :return: Error message if found, None otherwise
        :rtype: Optional[str]
        """
        if pattern_key not in parsed_data:
            return None

        error_data = parsed_data[pattern_key]

        if isinstance(error_data, dict) and "TEXT" in error_data:
            error_text = error_data["TEXT"]
            logger.error(f"Qualys {pattern_name} error: {error_text}")
            return f"Qualys {pattern_name} error: {error_text}"

        return None

    @staticmethod
    def _format_error_message(error_code: str, error_text: str) -> str:
        """
        Format an error message with code and description.

        :param str error_code: Qualys error code
        :param str error_text: Error text from API
        :return: Formatted error message
        :rtype: str
        """
        code_description = QualysErrorHandler.ERROR_CODE_MESSAGES.get(error_code, "Unknown error code")
        return f"Qualys Error {error_code}: {code_description} - {error_text}"

    @staticmethod
    def should_retry(error_code: str) -> bool:
        """
        Determine if a request should be retried based on the error code.

        :param str error_code: Qualys error code
        :return: True if the request should be retried
        :rtype: bool
        """
        return error_code in QualysErrorHandler.RETRY_CODES

    @staticmethod
    def is_fatal_error(error_code: str) -> bool:
        """
        Determine if an error is fatal and should stop processing.

        :param str error_code: Qualys error code
        :return: True if the error is fatal
        :rtype: bool
        """
        return error_code in QualysErrorHandler.FATAL_CODES

    @staticmethod
    def parse_xml_safely(xml_content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse XML content with comprehensive error handling.

        :param str xml_content: XML content to parse
        :return: Tuple of (success, parsed_data, error_message)
        :rtype: Tuple[bool, Optional[Dict[str, Any]], Optional[str]]
        """
        if not xml_content:
            return False, None, "Empty XML content"

        if not xml_content.strip():
            return False, None, "XML content contains only whitespace"

        try:
            # First try with xmltodict for better structure
            parsed_data = xmltodict.parse(xml_content)

            # Check for Qualys-specific errors
            error_info = QualysErrorHandler._check_qualys_errors(parsed_data)
            if error_info:
                return False, parsed_data, error_info

            return True, parsed_data, None

        except xmltodict.expat.ExpatError as e:
            logger.error(f"XML parsing error (expat): {e}")
            return False, None, f"XML parsing error: {e}"

        except ET.ParseError as e:
            logger.error(f"XML parsing error (ElementTree): {e}")
            return False, None, f"XML parsing error: {e}"

        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            return False, None, f"Unexpected XML parsing error: {e}"

    @staticmethod
    def extract_error_details(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed error information from parsed Qualys response.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :return: Dictionary containing error details
        :rtype: Dict[str, Any]
        """
        error_details = QualysErrorHandler._create_empty_error_details()

        # Check SIMPLE_RETURN format
        QualysErrorHandler._extract_simple_return_details(parsed_data, error_details)

        # Check for other error formats if no SIMPLE_RETURN error found
        if not error_details["has_error"]:
            QualysErrorHandler._extract_other_error_formats(parsed_data, error_details)

        return error_details

    @staticmethod
    def _create_empty_error_details() -> Dict[str, Any]:
        """
        Create an empty error details dictionary with default values.

        :return: Dictionary with default error detail values
        :rtype: Dict[str, Any]
        """
        return {
            "has_error": False,
            "error_code": None,
            "error_message": None,
            "error_type": None,
            "retry_after": None,
            "additional_info": {},
        }

    @staticmethod
    def _extract_simple_return_details(parsed_data: Dict[str, Any], error_details: Dict[str, Any]) -> None:
        """
        Extract error details from SIMPLE_RETURN format.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :param Dict[str, Any] error_details: Error details dictionary to update
        """
        if "SIMPLE_RETURN" not in parsed_data:
            return

        simple_return = parsed_data["SIMPLE_RETURN"]
        response = simple_return.get("RESPONSE", {})

        if "TEXT" not in response:
            return

        error_details["has_error"] = True
        error_details["error_message"] = response["TEXT"]
        error_details["error_type"] = "SIMPLE_RETURN"

        if "CODE" in response:
            error_details["error_code"] = response["CODE"]

        # Extract retry-after information if available
        QualysErrorHandler._extract_retry_after_info(response, error_details)

    @staticmethod
    def _extract_retry_after_info(response: Dict[str, Any], error_details: Dict[str, Any]) -> None:
        """
        Extract retry-after information from response.

        :param Dict[str, Any] response: Response data
        :param Dict[str, Any] error_details: Error details dictionary to update
        """
        if "ITEM_LIST" not in response:
            return

        item_list = response["ITEM_LIST"]
        if not isinstance(item_list, dict) or "ITEM" not in item_list:
            return

        item = item_list["ITEM"]
        if not isinstance(item, dict) or "VALUE" not in item:
            return

        try:
            error_details["retry_after"] = int(item["VALUE"])
        except (ValueError, TypeError):
            pass

    @staticmethod
    def _extract_other_error_formats(parsed_data: Dict[str, Any], error_details: Dict[str, Any]) -> None:
        """
        Extract error details from other error formats.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :param Dict[str, Any] error_details: Error details dictionary to update
        """
        error_keys = ["ERROR", "FAULT", "EXCEPTION"]

        for error_key in error_keys:
            if QualysErrorHandler._extract_error_format_details(parsed_data, error_details, error_key):
                break  # Stop after finding the first error

    @staticmethod
    def _extract_error_format_details(
        parsed_data: Dict[str, Any], error_details: Dict[str, Any], error_key: str
    ) -> bool:
        """
        Extract error details for a specific error format.

        :param Dict[str, Any] parsed_data: Parsed XML data
        :param Dict[str, Any] error_details: Error details dictionary to update
        :param str error_key: Error key to look for
        :return: True if error was found and extracted, False otherwise
        :rtype: bool
        """
        if error_key not in parsed_data:
            return False

        error_info = parsed_data[error_key]
        error_details["has_error"] = True
        error_details["error_type"] = error_key

        if not isinstance(error_info, dict):
            return True

        if "TEXT" in error_info:
            error_details["error_message"] = error_info["TEXT"]
        if "CODE" in error_info:
            error_details["error_code"] = error_info["CODE"]

        # Store additional error information
        QualysErrorHandler._store_additional_error_info(error_info, error_details)
        return True

    @staticmethod
    def _store_additional_error_info(error_info: Dict[str, Any], error_details: Dict[str, Any]) -> None:
        """
        Store additional error information excluding standard fields.

        :param Dict[str, Any] error_info: Error information from parsed data
        :param Dict[str, Any] error_details: Error details dictionary to update
        """
        excluded_keys = {"TEXT", "CODE"}

        for key, value in error_info.items():
            if key not in excluded_keys:
                error_details["additional_info"][key] = value

    @staticmethod
    def log_error_details(error_details: Dict[str, Any]) -> None:
        """
        Log detailed error information.

        :param Dict[str, Any] error_details: Error details dictionary
        """
        if not error_details.get("has_error"):
            return

        error_code = error_details.get("error_code")
        error_message = error_details.get("error_message")
        error_type = error_details.get("error_type")
        retry_after = error_details.get("retry_after")

        log_message = f"Qualys API Error ({error_type})"

        if error_code:
            code_description = QualysErrorHandler.ERROR_CODE_MESSAGES.get(error_code, "Unknown error code")
            log_message += f" - Code {error_code}: {code_description}"

        if error_message:
            log_message += f" - Message: {error_message}"

        if retry_after:
            log_message += f" - Retry after: {retry_after} seconds"

        logger.error(log_message)

        # Log additional information if available
        additional_info = error_details.get("additional_info", {})
        if additional_info:
            logger.debug(f"Additional error information: {additional_info}")
