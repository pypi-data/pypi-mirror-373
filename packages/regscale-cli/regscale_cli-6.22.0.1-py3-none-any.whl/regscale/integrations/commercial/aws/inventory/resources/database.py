"""AWS database resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class DatabaseCollector(BaseCollector):
    """Collector for AWS database resources."""

    def get_rds_instances(self) -> List[Dict[str, Any]]:
        """
        Get information about RDS instances.

        :return: List of RDS instance information
        :rtype: List[Dict[str, Any]]
        """
        instances = []
        try:
            rds = self._get_client("rds")
            paginator = rds.get_paginator("describe_db_instances")

            for page in paginator.paginate():
                for instance in page.get("DBInstances", []):
                    instances.append(
                        {
                            "Region": self.region,
                            "DBInstanceIdentifier": instance.get("DBInstanceIdentifier"),
                            "DBInstanceClass": instance.get("DBInstanceClass"),
                            "Engine": instance.get("Engine"),
                            "EngineVersion": instance.get("EngineVersion"),
                            "DBInstanceStatus": instance.get("DBInstanceStatus"),
                            "Endpoint": instance.get("Endpoint", {}),
                            "AllocatedStorage": instance.get("AllocatedStorage"),
                            "InstanceCreateTime": str(instance.get("InstanceCreateTime")),
                            "VpcId": instance.get("DBSubnetGroup", {}).get("VpcId"),
                            "MultiAZ": instance.get("MultiAZ"),
                            "PubliclyAccessible": instance.get("PubliclyAccessible"),
                            "StorageEncrypted": instance.get("StorageEncrypted"),
                            "KmsKeyId": instance.get("KmsKeyId"),
                            "Tags": instance.get("TagList", []),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "RDS instances")
        return instances

    def get_dynamodb_tables(self) -> List[Dict[str, Any]]:
        """
        Get information about DynamoDB tables.

        :return: List of DynamoDB table information
        :rtype: List[Dict[str, Any]]
        """
        tables = []
        try:
            dynamodb = self._get_client("dynamodb")
            paginator = dynamodb.get_paginator("list_tables")

            for page in paginator.paginate():
                for table_name in page.get("TableNames", []):
                    try:
                        table = dynamodb.describe_table(TableName=table_name)["Table"]
                        tables.append(
                            {
                                "Region": self.region,
                                "TableName": table.get("TableName"),
                                "TableStatus": table.get("TableStatus"),
                                "CreationDateTime": str(table.get("CreationDateTime")),
                                "TableSizeBytes": table.get("TableSizeBytes"),
                                "ItemCount": table.get("ItemCount"),
                                "TableArn": table.get("TableArn"),
                                "ProvisionedThroughput": {
                                    "ReadCapacityUnits": table.get("ProvisionedThroughput", {}).get(
                                        "ReadCapacityUnits"
                                    ),
                                    "WriteCapacityUnits": table.get("ProvisionedThroughput", {}).get(
                                        "WriteCapacityUnits"
                                    ),
                                },
                                "BillingModeSummary": table.get("BillingModeSummary", {}),
                                "GlobalSecondaryIndexes": table.get("GlobalSecondaryIndexes", []),
                                "LocalSecondaryIndexes": table.get("LocalSecondaryIndexes", []),
                                "StreamSpecification": table.get("StreamSpecification", {}),
                                "SSEDescription": table.get("SSEDescription", {}),
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"DynamoDB table {table_name}")
        except Exception as e:
            self._handle_error(e, "DynamoDB tables")
        return tables

    def collect(self) -> Dict[str, Any]:
        """
        Collect all database resources.

        :return: Dictionary containing all database resource information
        :rtype: Dict[str, Any]
        """
        return {"RDSInstances": self.get_rds_instances(), "DynamoDBTables": self.get_dynamodb_tables()}
