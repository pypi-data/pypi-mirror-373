"""Base classes for AWS resource collection."""

import logging
from typing import Any, Dict, TYPE_CHECKING

from botocore.exceptions import ClientError

if TYPE_CHECKING:
    import boto3

logger = logging.getLogger("regscale")


class BaseCollector:
    """Base class for AWS resource collectors."""

    def __init__(self, session: "boto3.Session", region: str):
        """
        Initialize the base collector.

        :param boto3.Session session: AWS session to use for API calls
        :param str region: AWS region to collect from
        """
        self.session = session
        self.region = region

    def _get_client(self, service_name: str) -> Any:
        """
        Get a boto3 client for the specified service.

        :param str service_name: Name of the AWS service
        :return: Boto3 client for the service
        :rtype: Any
        """
        return self.session.client(service_name)

    def _handle_error(self, error: Exception, resource_type: str) -> None:
        """
        Handle and log AWS API errors.

        :param Exception error: The error that occurred
        :param str resource_type: Type of resource being collected
        """
        if isinstance(error, ClientError):
            if error.response["Error"]["Code"] == "AccessDeniedException":
                logger.warning(f"Access denied to {resource_type} in {self.region}")
            else:
                logger.error(f"Error collecting {resource_type} in {self.region}: {error}")
                logger.debug(error, exc_info=True)
        else:
            logger.error(f"Unexpected error collecting {resource_type} in {self.region}: {error}")
            logger.debug(error, exc_info=True)

    def collect(self) -> Dict[str, Any]:
        """
        Collect resources. Must be implemented by subclasses.

        :return: Dictionary containing resource information
        :rtype: Dict[str, Any]
        :raises NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement collect()")
