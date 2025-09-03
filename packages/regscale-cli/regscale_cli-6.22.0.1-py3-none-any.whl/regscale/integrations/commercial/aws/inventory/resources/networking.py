"""AWS networking resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class NetworkingCollector(BaseCollector):
    """Collector for AWS networking resources."""

    def get_vpcs(self) -> List[Dict[str, Any]]:
        """
        Get information about VPCs.

        :return: List of VPC information
        :rtype: List[Dict[str, Any]]
        """
        vpcs = []
        try:
            ec2 = self._get_client("ec2")
            paginator = ec2.get_paginator("describe_vpcs")

            for page in paginator.paginate():
                for vpc in page.get("Vpcs", []):
                    # Get subnets for this VPC
                    subnets = []
                    subnet_paginator = ec2.get_paginator("describe_subnets")
                    for subnet_page in subnet_paginator.paginate(
                        Filters=[{"Name": "vpc-id", "Values": [vpc["VpcId"]]}]
                    ):
                        subnets.extend(subnet_page.get("Subnets", []))

                    # Get security groups for this VPC
                    security_groups = []
                    sg_paginator = ec2.get_paginator("describe_security_groups")
                    for sg_page in sg_paginator.paginate(Filters=[{"Name": "vpc-id", "Values": [vpc["VpcId"]]}]):
                        security_groups.extend(sg_page.get("SecurityGroups", []))

                    vpcs.append(
                        {
                            "Region": self.region,
                            "VpcId": vpc.get("VpcId"),
                            "CidrBlock": vpc.get("CidrBlock"),
                            "State": vpc.get("State"),
                            "IsDefault": vpc.get("IsDefault"),
                            "Tags": vpc.get("Tags", []),
                            "Subnets": [
                                {
                                    "SubnetId": subnet.get("SubnetId"),
                                    "CidrBlock": subnet.get("CidrBlock"),
                                    "AvailabilityZone": subnet.get("AvailabilityZone"),
                                    "State": subnet.get("State"),
                                    "Tags": subnet.get("Tags", []),
                                }
                                for subnet in subnets
                            ],
                            "SecurityGroups": [
                                {
                                    "GroupId": sg.get("GroupId"),
                                    "GroupName": sg.get("GroupName"),
                                    "Description": sg.get("Description"),
                                    "IpPermissions": sg.get("IpPermissions", []),
                                    "IpPermissionsEgress": sg.get("IpPermissionsEgress", []),
                                    "Tags": sg.get("Tags", []),
                                }
                                for sg in security_groups
                            ],
                        }
                    )
        except Exception as e:
            self._handle_error(e, "VPCs")
        return vpcs

    def get_elastic_ips(self) -> List[Dict[str, Any]]:
        """
        Get information about Elastic IPs.

        :return: List of Elastic IP information
        :rtype: List[Dict[str, Any]]
        """
        eips = []
        try:
            ec2 = self._get_client("ec2")
            addresses = ec2.describe_addresses().get("Addresses", [])

            for addr in addresses:
                eips.append(
                    {
                        "Region": self.region,
                        "PublicIp": addr.get("PublicIp"),
                        "AllocationId": addr.get("AllocationId"),
                        "InstanceId": addr.get("InstanceId"),
                        "NetworkInterfaceId": addr.get("NetworkInterfaceId"),
                        "NetworkInterfaceOwner": addr.get("NetworkInterfaceOwnerId"),
                        "PrivateIpAddress": addr.get("PrivateIpAddress"),
                        "Tags": addr.get("Tags", []),
                    }
                )
        except Exception as e:
            self._handle_error(e, "Elastic IPs")
        return eips

    def get_load_balancers(self) -> List[Dict[str, Any]]:
        """
        Get information about Load Balancers (ALB/NLB).

        :return: List of Load Balancer information
        :rtype: List[Dict[str, Any]]
        """
        lbs = []
        try:
            elb = self._get_client("elbv2")
            paginator = elb.get_paginator("describe_load_balancers")

            for page in paginator.paginate():
                for lb in page.get("LoadBalancers", []):
                    # Get target groups for this LB
                    target_groups = []
                    tg_paginator = elb.get_paginator("describe_target_groups")
                    for tg_page in tg_paginator.paginate(LoadBalancerArn=lb["LoadBalancerArn"]):
                        target_groups.extend(tg_page.get("TargetGroups", []))

                    lbs.append(
                        {
                            "Region": self.region,
                            "LoadBalancerName": lb.get("LoadBalancerName"),
                            "DNSName": lb.get("DNSName"),
                            "Type": lb.get("Type"),
                            "Scheme": lb.get("Scheme"),
                            "VpcId": lb.get("VpcId"),
                            "State": lb.get("State", {}).get("Code"),
                            "AvailabilityZones": lb.get("AvailabilityZones", []),
                            "SecurityGroups": lb.get("SecurityGroups", []),
                            "TargetGroups": [
                                {
                                    "TargetGroupName": tg.get("TargetGroupName"),
                                    "TargetGroupArn": tg.get("TargetGroupArn"),
                                    "Protocol": tg.get("Protocol"),
                                    "Port": tg.get("Port"),
                                    "HealthCheckProtocol": tg.get("HealthCheckProtocol"),
                                    "HealthCheckPort": tg.get("HealthCheckPort"),
                                    "HealthCheckPath": tg.get("HealthCheckPath"),
                                }
                                for tg in target_groups
                            ],
                        }
                    )
        except Exception as e:
            self._handle_error(e, "Load Balancers")
        return lbs

    def get_cloudfront_distributions(self) -> List[Dict[str, Any]]:
        """
        Get information about CloudFront distributions.

        :return: List of CloudFront distribution information
        :rtype: List[Dict[str, Any]]
        """
        distributions = []
        try:
            cloudfront = self._get_client("cloudfront")
            paginator = cloudfront.get_paginator("list_distributions")

            for page in paginator.paginate():
                for dist in page.get("DistributionList", {}).get("Items", []):
                    distributions.append(
                        {
                            "Region": self.region,
                            "Id": dist.get("Id"),
                            "DomainName": dist.get("DomainName"),
                            "Status": dist.get("Status"),
                            "Enabled": dist.get("Enabled"),
                            "Origins": dist.get("Origins", {}).get("Items", []),
                            "DefaultCacheBehavior": dist.get("DefaultCacheBehavior", {}),
                            "CacheBehaviors": dist.get("CacheBehaviors", {}).get("Items", []),
                            "CustomErrorResponses": dist.get("CustomErrorResponses", {}).get("Items", []),
                            "Comment": dist.get("Comment"),
                            "PriceClass": dist.get("PriceClass"),
                            "LastModifiedTime": str(dist.get("LastModifiedTime")),
                            "WebACLId": dist.get("WebACLId"),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "CloudFront distributions")
        return distributions

    def get_route53_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get information about Route53 hosted zones and records.

        :return: Dictionary containing Route53 information
        :rtype: Dict[str, List[Dict[str, Any]]]
        """
        route53_info = {"HostedZones": [], "Records": []}
        try:
            route53 = self._get_client("route53")

            # Get hosted zones
            paginator = route53.get_paginator("list_hosted_zones")
            for page in paginator.paginate():
                for zone in page.get("HostedZones", []):
                    try:
                        # Get records for this zone
                        records = []
                        record_paginator = route53.get_paginator("list_resource_record_sets")
                        for record_page in record_paginator.paginate(HostedZoneId=zone["Id"]):
                            for record in record_page.get("ResourceRecordSets", []):
                                records.append(
                                    {
                                        "Name": record.get("Name"),
                                        "Type": record.get("Type"),
                                        "TTL": record.get("TTL"),
                                        "ResourceRecords": record.get("ResourceRecords", []),
                                        "AliasTarget": record.get("AliasTarget"),
                                        "Weight": record.get("Weight"),
                                        "Region": record.get("Region"),
                                        "GeoLocation": record.get("GeoLocation"),
                                        "Failover": record.get("Failover"),
                                        "MultiValueAnswer": record.get("MultiValueAnswer"),
                                        "HealthCheckId": record.get("HealthCheckId"),
                                    }
                                )

                        route53_info["HostedZones"].append(
                            {
                                "Id": zone.get("Id"),
                                "Name": zone.get("Name"),
                                "CallerReference": zone.get("CallerReference"),
                                "Config": zone.get("Config", {}),
                                "ResourceRecordSetCount": zone.get("ResourceRecordSetCount"),
                                "Records": records,
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"Route53 zone {zone['Name']}")
        except Exception as e:
            self._handle_error(e, "Route53 zones")
        return route53_info

    def collect(self) -> Dict[str, Any]:
        """
        Collect all networking resources.

        :return: Dictionary containing all networking resource information
        :rtype: Dict[str, Any]
        """
        return {
            "VPCs": self.get_vpcs(),
            "ElasticIPs": self.get_elastic_ips(),
            "LoadBalancers": self.get_load_balancers(),
            "CloudFrontDistributions": self.get_cloudfront_distributions(),
            "Route53": self.get_route53_info(),
        }
