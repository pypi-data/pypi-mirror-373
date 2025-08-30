"""AWS resource inventory collection module."""

import os
from typing import Dict, Any, Optional

from regscale.integrations.commercial.aws.inventory.base import BaseCollector
from regscale.integrations.commercial.aws.inventory.resources.compute import ComputeCollector
from regscale.integrations.commercial.aws.inventory.resources.containers import ContainerCollector
from regscale.integrations.commercial.aws.inventory.resources.database import DatabaseCollector
from regscale.integrations.commercial.aws.inventory.resources.integration import IntegrationCollector
from regscale.integrations.commercial.aws.inventory.resources.networking import NetworkingCollector
from regscale.integrations.commercial.aws.inventory.resources.security import SecurityCollector
from regscale.integrations.commercial.aws.inventory.resources.storage import StorageCollector


class AWSInventoryCollector:
    """Collects inventory of AWS resources."""

    def __init__(
        self,
        region: str = os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ):
        """
        Initialize the AWS inventory collector.

        :param str region: AWS region to collect inventory from
        :param str aws_access_key_id: Optional AWS access key ID
        :param str aws_secret_access_key: Optional AWS secret access key
        :param str aws_session_token: Optional AWS session ID
        """
        import boto3

        self.region = region
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region,
            aws_session_token=aws_session_token,
        )

        # Initialize collectors
        self.compute = ComputeCollector(self.session, self.region)
        self.storage = StorageCollector(self.session, self.region)
        self.database = DatabaseCollector(self.session, self.region)
        self.networking = NetworkingCollector(self.session, self.region)
        self.security = SecurityCollector(self.session, self.region)
        self.integration = IntegrationCollector(self.session, self.region)
        self.containers = ContainerCollector(self.session, self.region)

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect all AWS resources.

        :return: Dictionary containing all AWS resource information
        :rtype: Dict[str, Any]
        """
        inventory = {}
        collectors = [
            self.compute,
            self.storage,
            self.database,
            self.networking,
            self.security,
            self.integration,
            self.containers,
        ]

        for collector in collectors:
            try:
                resources = collector.collect()
                inventory.update(resources)
            except Exception as e:
                from regscale.core.app.utils.app_utils import create_logger

                # Handle or log the exception as needed
                create_logger().error(f"Error collecting resource(s) from {collector.__class__.__name__}: {e}")

        return inventory


def collect_all_inventory(
    region: str = os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Collect inventory of all AWS resources.

    :param str region: AWS region to collect inventory from
    :param str aws_access_key_id: Optional AWS access key ID
    :param str aws_secret_access_key: Optional AWS secret access key
    :param str aws_session_token: Optional AWS session ID
    :return: Dictionary containing all AWS resource information
    :rtype: Dict[str, Any]
    """
    collector = AWSInventoryCollector(region, aws_access_key_id, aws_secret_access_key, aws_session_token)
    return collector.collect_all()


if __name__ == "__main__":
    collect_all_inventory(
        region="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    )
