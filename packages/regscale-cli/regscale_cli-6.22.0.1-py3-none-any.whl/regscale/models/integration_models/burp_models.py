#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pydantic models for Burp Scans"""

# standard python imports
import base64
import json
from typing import List, Optional, Union, Any

from pydantic import BaseModel

from regscale.models.integration_models.base64 import Base64String


class BurpResponse(BaseModel):
    """Response information"""

    base64: Optional[bool] = None
    dataString: Optional[Union[Base64String, str]] = None

    def convert_to_response(self) -> Optional[str]:
        """
        Convert base64 encoded response to a requests Response object

        :return: Base64 decoded response as a string
        :rtype: Optional[str]
        """
        try:
            bytes_data = base64.b64decode(self.dataString)
            if bytes_data:
                # Decode bytes to string
                res = bytes_data.decode("utf-8")
        except Exception:
            res = None
        return res

    def convert_to_json(self) -> Optional[dict]:
        """
        Convert base64 encoded response to a JSON object

        :return: Base64 decoded response as a JSON object or None
        :rtype: Optional[dict]
        """
        res = self.convert_to_response()
        data = None
        if res:
            # Find the start and end of the JSON data
            start = res.find("{")  # +1 to include the closing brace

            # Extract the JSON data and convert it to a Python dictionary
            try:
                data = json.loads(res[start:])
            except json.decoder.JSONDecodeError:
                data = None
        return data

    @classmethod
    def is_base64(cls, sb: Any) -> bool:
        """
        Check if string is base64 encoded

        :param Any sb: String to check
        :raises ValueError: If argument is not a string or bytes
        :return: True if base64 encoded
        :rtype: bool
        """
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, "ascii")
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            # If this works, there's base64-encoded data here.
            _ = base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
            return False
        return True


class Host(BaseModel):
    """Host information"""

    ip: str
    hostname: str


class IssueDetailItem(BaseModel):
    """Issue Detail Item information"""

    issueDetailItem: Optional[str] = None


class BurpRequest(BurpResponse):
    """Request information"""

    method: str


class RequestResponse(BaseModel):
    """Request Response information"""

    request: Optional[BurpRequest] = None
    response: Optional[BurpResponse] = None


class Issue(BaseModel):
    """Issue information"""

    serialNumber: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    host: Optional[Host] = None
    path: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[str] = None
    background: Optional[str] = None
    remediation_background: Optional[str] = None
    detail: Optional[str] = None
    detail_items: Optional[List[IssueDetailItem]] = None
    request_response: Optional[RequestResponse] = None
    remediation_detail: Optional[str] = None
    references: Optional[str] = None
    vulnerability_classifications: Optional[str] = None
    cwes: Optional[List[str]] = None
    links: Optional[List[str]] = None
