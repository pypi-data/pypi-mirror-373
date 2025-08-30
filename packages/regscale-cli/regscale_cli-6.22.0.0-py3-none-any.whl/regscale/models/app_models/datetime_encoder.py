"""
This module provides a custom JSON encoder for handling datetime objects.
"""

import datetime
import json
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts datetime objects to ISO format strings.
    """

    def default(self, obj: Any) -> Any:
        """
        Override the default method to handle datetime objects.
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)
