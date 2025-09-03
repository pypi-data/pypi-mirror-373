"""AWS storage resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class StorageCollector(BaseCollector):
    """Collector for AWS storage resources."""

    def get_s3_buckets(self) -> List[Dict[str, Any]]:
        """
        Get information about S3 buckets.

        :return: List of S3 bucket information
        :rtype: List[Dict[str, Any]]
        """
        buckets = []
        try:
            s3 = self._get_client("s3")
            response = s3.list_buckets()

            for bucket in response.get("Buckets", []):
                try:
                    location = s3.get_bucket_location(Bucket=bucket["Name"])
                    region = location.get("LocationConstraint") or "us-east-1"

                    # Only include buckets in the target region
                    if region == self.region:
                        buckets.append(
                            {
                                "Region": self.region,
                                "Name": bucket["Name"],
                                "CreationDate": str(bucket["CreationDate"]),
                                "Location": region,
                            }
                        )
                except Exception as e:
                    self._handle_error(e, f"S3 bucket {bucket['Name']}")
        except Exception as e:
            self._handle_error(e, "S3 buckets")
        return buckets

    def get_ebs_volumes(self) -> List[Dict[str, Any]]:
        """
        Get information about EBS volumes.

        :return: List of EBS volume information
        :rtype: List[Dict[str, Any]]
        """
        volumes = []
        try:
            ec2 = self._get_client("ec2")
            paginator = ec2.get_paginator("describe_volumes")

            for page in paginator.paginate():
                for volume in page.get("Volumes", []):
                    attachments = volume.get("Attachments", [])
                    volumes.append(
                        {
                            "Region": self.region,
                            "VolumeId": volume.get("VolumeId"),
                            "Size": volume.get("Size"),
                            "VolumeType": volume.get("VolumeType"),
                            "State": volume.get("State"),
                            "CreateTime": str(volume.get("CreateTime")),
                            "Encrypted": volume.get("Encrypted"),
                            "KmsKeyId": volume.get("KmsKeyId"),
                            "Attachments": [
                                {
                                    "InstanceId": att.get("InstanceId"),
                                    "State": att.get("State"),
                                    "Device": att.get("Device"),
                                }
                                for att in attachments
                            ],
                            "Tags": volume.get("Tags", []),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "EBS volumes")
        return volumes

    def collect(self) -> Dict[str, Any]:
        """
        Collect all storage resources.

        :return: Dictionary containing all storage resource information
        :rtype: Dict[str, Any]
        """
        return {"S3Buckets": self.get_s3_buckets(), "EBSVolumes": self.get_ebs_volumes()}
