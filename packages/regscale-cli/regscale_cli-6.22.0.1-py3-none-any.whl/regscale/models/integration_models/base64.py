"""Standard imports"""

import base64

from pydantic import ValidationError


class Base64String(str):
    """Base64 String"""

    @classmethod
    def __get_validators__(cls):
        """Get validators"""
        yield cls.validate_base64_str

    @classmethod
    def validate_base64_str(cls, input_string: str, field: str):
        """Validate base64 string"""
        try:
            base64.b64decode(input_string)
            return input_string
        except Exception as exc:
            raise ValidationError(f"{field} is not a valid base64 string") from exc
