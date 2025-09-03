"""AWS application integration resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class IntegrationCollector(BaseCollector):
    """Collector for AWS application integration resources."""

    def get_api_gateways(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get information about API Gateway APIs (REST and HTTP).

        :return: Dictionary containing API Gateway information
        :rtype: Dict[str, List[Dict[str, Any]]]
        """
        apis = {"REST": [], "HTTP": []}
        try:
            # Get REST APIs
            apigw = self._get_client("apigateway")
            rest_paginator = apigw.get_paginator("get_rest_apis")

            for page in rest_paginator.paginate():
                for api in page.get("items", []):
                    try:
                        stages = apigw.get_stages(restApiId=api["id"])["item"]
                        apis["REST"].append(
                            {
                                "Region": self.region,
                                "Id": api.get("id"),
                                "Name": api.get("name"),
                                "Description": api.get("description"),
                                "CreatedDate": str(api.get("createdDate")),
                                "Version": api.get("version"),
                                "EndpointConfiguration": api.get("endpointConfiguration", {}),
                                "Stages": [
                                    {
                                        "StageName": stage.get("stageName"),
                                        "DeploymentId": stage.get("deploymentId"),
                                        "Description": stage.get("description"),
                                        "CreatedDate": str(stage.get("createdDate")),
                                        "LastUpdatedDate": str(stage.get("lastUpdatedDate")),
                                    }
                                    for stage in stages
                                ],
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"REST API {api['name']}")

            # Get HTTP APIs
            apigwv2 = self._get_client("apigatewayv2")
            http_paginator = apigwv2.get_paginator("get_apis")

            for page in http_paginator.paginate():
                for api in page.get("Items", []):
                    try:
                        stages = apigwv2.get_stages(ApiId=api["ApiId"])["Items"]
                        apis["HTTP"].append(
                            {
                                "Region": self.region,
                                "Id": api.get("ApiId"),
                                "Name": api.get("Name"),
                                "Description": api.get("Description"),
                                "ProtocolType": api.get("ProtocolType"),
                                "CreatedDate": str(api.get("CreatedDate")),
                                "ApiEndpoint": api.get("ApiEndpoint"),
                                "Stages": [
                                    {
                                        "StageName": stage.get("StageName"),
                                        "Description": stage.get("Description"),
                                        "CreatedDate": str(stage.get("CreatedDate")),
                                        "LastUpdatedDate": str(stage.get("LastUpdatedDate")),
                                        "DefaultRouteSettings": stage.get("DefaultRouteSettings", {}),
                                    }
                                    for stage in stages
                                ],
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"HTTP API {api['Name']}")
        except Exception as e:
            self._handle_error(e, "API Gateway APIs")
        return apis

    def get_sns_topics(self) -> List[Dict[str, Any]]:
        """
        Get information about SNS topics.

        :return: List of SNS topic information
        :rtype: List[Dict[str, Any]]
        """
        topics = []
        try:
            sns = self._get_client("sns")
            paginator = sns.get_paginator("list_topics")

            for page in paginator.paginate():
                for topic in page.get("Topics", []):
                    try:
                        # Get topic attributes
                        attrs = sns.get_topic_attributes(TopicArn=topic["TopicArn"])["Attributes"]
                        # Get subscriptions
                        subs = []
                        sub_paginator = sns.get_paginator("list_subscriptions_by_topic")
                        for sub_page in sub_paginator.paginate(TopicArn=topic["TopicArn"]):
                            subs.extend(sub_page.get("Subscriptions", []))

                        topics.append(
                            {
                                "Region": self.region,
                                "TopicArn": topic.get("TopicArn"),
                                "Owner": attrs.get("Owner"),
                                "Policy": attrs.get("Policy"),
                                "DisplayName": attrs.get("DisplayName"),
                                "SubscriptionsConfirmed": attrs.get("SubscriptionsConfirmed"),
                                "SubscriptionsPending": attrs.get("SubscriptionsPending"),
                                "SubscriptionsDeleted": attrs.get("SubscriptionsDeleted"),
                                "Subscriptions": [
                                    {
                                        "SubscriptionArn": sub.get("SubscriptionArn"),
                                        "Protocol": sub.get("Protocol"),
                                        "Endpoint": sub.get("Endpoint"),
                                    }
                                    for sub in subs
                                ],
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"SNS topic {topic['TopicArn']}")
        except Exception as e:
            self._handle_error(e, "SNS topics")
        return topics

    def get_sqs_queues(self) -> List[Dict[str, Any]]:
        """
        Get information about SQS queues.

        :return: List of SQS queue information
        :rtype: List[Dict[str, Any]]
        """
        queues = []
        try:
            sqs = self._get_client("sqs")
            paginator = sqs.get_paginator("list_queues")

            for page in paginator.paginate():
                for queue_url in page.get("QueueUrls", []):
                    try:
                        # Get queue attributes
                        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])["Attributes"]

                        queues.append(
                            {
                                "Region": self.region,
                                "QueueUrl": queue_url,
                                "QueueArn": attrs.get("QueueArn"),
                                "ApproximateNumberOfMessages": attrs.get("ApproximateNumberOfMessages"),
                                "ApproximateNumberOfMessagesNotVisible": attrs.get(
                                    "ApproximateNumberOfMessagesNotVisible"
                                ),
                                "ApproximateNumberOfMessagesDelayed": attrs.get("ApproximateNumberOfMessagesDelayed"),
                                "CreatedTimestamp": attrs.get("CreatedTimestamp"),
                                "LastModifiedTimestamp": attrs.get("LastModifiedTimestamp"),
                                "VisibilityTimeout": attrs.get("VisibilityTimeout"),
                                "MaximumMessageSize": attrs.get("MaximumMessageSize"),
                                "MessageRetentionPeriod": attrs.get("MessageRetentionPeriod"),
                                "DelaySeconds": attrs.get("DelaySeconds"),
                                "Policy": attrs.get("Policy"),
                                "RedrivePolicy": attrs.get("RedrivePolicy"),
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"SQS queue {queue_url}")
        except Exception as e:
            self._handle_error(e, "SQS queues")
        return queues

    def get_eventbridge_rules(self) -> List[Dict[str, Any]]:
        """
        Get information about EventBridge rules.

        :return: List of EventBridge rule information
        :rtype: List[Dict[str, Any]]
        """
        rules = []
        try:
            events = self._get_client("events")
            paginator = events.get_paginator("list_rules")

            for page in paginator.paginate():
                for rule in page.get("Rules", []):
                    try:
                        # Get targets for this rule
                        targets = events.list_targets_by_rule(Rule=rule["Name"])["Targets"]

                        rules.append(
                            {
                                "Region": self.region,
                                "Name": rule.get("Name"),
                                "Arn": rule.get("Arn"),
                                "Description": rule.get("Description"),
                                "State": rule.get("State"),
                                "ScheduleExpression": rule.get("ScheduleExpression"),
                                "EventPattern": rule.get("EventPattern"),
                                "Targets": [
                                    {
                                        "Id": target.get("Id"),
                                        "Arn": target.get("Arn"),
                                        "RoleArn": target.get("RoleArn"),
                                        "Input": target.get("Input"),
                                        "InputPath": target.get("InputPath"),
                                    }
                                    for target in targets
                                ],
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"EventBridge rule {rule['Name']}")
        except Exception as e:
            self._handle_error(e, "EventBridge rules")
        return rules

    def collect(self) -> Dict[str, Any]:
        """
        Collect all application integration resources.

        :return: Dictionary containing all application integration resource information
        :rtype: Dict[str, Any]
        """
        return {
            "APIGateway": self.get_api_gateways(),
            "SNSTopics": self.get_sns_topics(),
            "SQSQueues": self.get_sqs_queues(),
            "EventBridgeRules": self.get_eventbridge_rules(),
        }
