"""AWS compute resource collectors."""

import logging
from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import boto3

from regscale.integrations.commercial.aws.inventory.base import BaseCollector

logger = logging.getLogger("regscale")


class ComputeCollector(BaseCollector):
    """Collector for AWS compute resources."""

    def __init__(self, session: "boto3.Session", region: str):
        """
        Initialize the compute collector.

        :param boto3.Session session: AWS session
        :param str region: AWS region
        """
        super().__init__(session, region)
        self.ec2_client = self._get_client("ec2")
        self.logger = logging.getLogger("regscale")

    @staticmethod
    def _collect_instance_ami_mapping(paginator) -> Dict[str, str]:
        """
        Collect mapping of instance IDs to their AMI IDs.

        :param paginator: EC2 describe_instances paginator
        :return: Dictionary mapping instance IDs to AMI IDs
        :rtype: Dict[str, str]
        """
        instance_ami_map = {}
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    if image_id := instance.get("ImageId"):
                        instance_ami_map[instance["InstanceId"]] = image_id
        return instance_ami_map

    def _get_ami_details(self, ami_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get details for a list of AMI IDs.

        :param ami_ids: List of AMI IDs to describe
        :return: Dictionary of AMI details keyed by AMI ID
        :rtype: Dict[str, Dict[str, Any]]
        """
        ami_details = {}
        for i in range(0, len(ami_ids), 100):
            batch = ami_ids[i : i + 100]
            try:
                ami_response = self.ec2_client.describe_images(ImageIds=batch)
                for image in ami_response.get("Images", []):
                    ami_details[image["ImageId"]] = {
                        "Name": image.get("Name"),
                        "Description": image.get("Description"),
                        "Architecture": image.get("Architecture"),
                        "RootDeviceType": image.get("RootDeviceType"),
                        "VirtualizationType": image.get("VirtualizationType"),
                        "PlatformDetails": image.get("PlatformDetails"),
                        "UsageOperation": image.get("UsageOperation"),
                    }
            except Exception as e:
                self.logger.warning(f"Error describing AMIs {batch}: {str(e)}")
        return ami_details

    def _build_instance_data(self, instance: Dict[str, Any], ami_details: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build instance data dictionary with AMI details.

        :param instance: Raw instance data
        :param ami_details: Dictionary of AMI details
        :return: Processed instance data
        :rtype: Dict[str, Any]
        """
        instance_data = {
            "Region": self.region,
            "InstanceId": instance.get("InstanceId"),
            "InstanceType": instance.get("InstanceType"),
            "LaunchTime": instance.get("LaunchTime"),
            "State": instance.get("State", {}).get("Name"),
            "Platform": instance.get("Platform"),
            "PlatformDetails": instance.get("PlatformDetails"),
            "PrivateIpAddress": instance.get("PrivateIpAddress"),
            "PublicIpAddress": instance.get("PublicIpAddress"),
            "Tags": instance.get("Tags", []),
            "VpcId": instance.get("VpcId"),
            "SubnetId": instance.get("SubnetId"),
            "ImageId": instance.get("ImageId"),
            "Architecture": instance.get("Architecture"),
            "CpuOptions": instance.get("CpuOptions", {}),
            "BlockDeviceMappings": instance.get("BlockDeviceMappings", []),
        }

        if image_id := instance.get("ImageId"):
            if ami_info := ami_details.get(image_id):
                instance_data["ImageInfo"] = ami_info

        return instance_data

    def get_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        Get information about EC2 instances in the region.

        :return: List of EC2 instance information
        :rtype: List[Dict[str, Any]]
        """
        instances = []
        try:
            paginator = self.ec2_client.get_paginator("describe_instances")

            # Collect instance to AMI mapping
            instance_ami_map = self._collect_instance_ami_mapping(paginator)

            # Get AMI details
            unique_amis = list(set(instance_ami_map.values()))
            ami_details = self._get_ami_details(unique_amis) if unique_amis else {}

            # Collect instance information
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        instance_data = self._build_instance_data(instance, ami_details)
                        instances.append(instance_data)

        except Exception as e:
            self.logger.error(f"Error getting EC2 instances in region {self.region}: {str(e)}")
            self.logger.error(f"{str(e)}", exc_info=True)

        return instances

    def get_lambda_functions(self) -> List[Dict[str, Any]]:
        """
        Get information about Lambda functions.

        :return: List of Lambda function information
        :rtype: List[Dict[str, Any]]
        """
        functions = []
        try:
            lambda_client = self._get_client("lambda")
            paginator = lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    functions.append(
                        {
                            "Region": self.region,
                            "FunctionName": function.get("FunctionName"),
                            "Runtime": function.get("Runtime"),
                            "Handler": function.get("Handler"),
                            "CodeSize": function.get("CodeSize"),
                            "Description": function.get("Description"),
                            "Timeout": function.get("Timeout"),
                            "MemorySize": function.get("MemorySize"),
                            "LastModified": function.get("LastModified"),
                            "Role": function.get("Role"),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "Lambda functions")
        return functions

    def get_ecs_clusters(self) -> List[Dict[str, Any]]:
        """
        Get information about ECS clusters and services.

        :return: List of ECS cluster information
        :rtype: List[Dict[str, Any]]
        """
        clusters = []
        try:
            ecs = self._get_client("ecs")
            cluster_arns = ecs.list_clusters().get("clusterArns", [])

            for cluster_arn in cluster_arns:
                cluster_info = ecs.describe_clusters(clusters=[cluster_arn])["clusters"][0]
                services = []

                # Get services for each cluster
                service_paginator = ecs.get_paginator("list_services")
                for service_page in service_paginator.paginate(cluster=cluster_arn):
                    service_arns = service_page.get("serviceArns", [])
                    if service_arns:
                        service_details = ecs.describe_services(cluster=cluster_arn, services=service_arns).get(
                            "services", []
                        )
                        services.extend(service_details)

                clusters.append(
                    {
                        "Region": self.region,
                        "ClusterName": cluster_info.get("clusterName"),
                        "ClusterArn": cluster_info.get("clusterArn"),
                        "Status": cluster_info.get("status"),
                        "RegisteredContainerInstancesCount": cluster_info.get("registeredContainerInstancesCount"),
                        "RunningTasksCount": cluster_info.get("runningTasksCount"),
                        "PendingTasksCount": cluster_info.get("pendingTasksCount"),
                        "ActiveServicesCount": cluster_info.get("activeServicesCount"),
                        "Services": [
                            {
                                "ServiceName": service.get("serviceName"),
                                "ServiceArn": service.get("serviceArn"),
                                "Status": service.get("status"),
                                "DesiredCount": service.get("desiredCount"),
                                "RunningCount": service.get("runningCount"),
                                "PendingCount": service.get("pendingCount"),
                                "LaunchType": service.get("launchType"),
                            }
                            for service in services
                        ],
                    }
                )
        except Exception as e:
            self._handle_error(e, "ECS clusters")
        return clusters

    def collect(self) -> Dict[str, Any]:
        """
        Collect all compute resources.

        :return: Dictionary containing all compute resource information
        :rtype: Dict[str, Any]
        """
        return {
            "EC2Instances": self.get_ec2_instances(),
            "LambdaFunctions": self.get_lambda_functions(),
            "ECSClusters": self.get_ecs_clusters(),
        }
