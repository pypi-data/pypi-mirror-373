"""Provide utilities for managing and creating GraphQL queries."""

from textwrap import indent
from typing import Union, Optional, Iterable, Dict


class GraphQLQuery:
    """The GraphQLQuery class can be used to define and build a GraphQL query.

    :param str action: the action to perform ("query" to fetch data, "mutation" to change data), defaults to "query"
    """

    def __init__(self, action: str = "query"):
        self.query = {"query": ""}
        self.action = action

    def start_query(self):
        """Start a query."""
        self.query["query"] += f"{self.action} {{\n"

    def end_query(self):
        """End the query."""
        self.query["query"] += "}"

    def build(self):
        """Return the contents of the query."""
        return self.query["query"]

    def process_where_conditions(self, conditions: Dict[str, Dict]) -> str:
        """
        Process the where conditions for the query.

        :param Dict[str, Dict] conditions: a dict of dicts containing a key and a {op: value}, e.g. {"eq": "value"}
        :return: the processed where conditions
        :rtype: str
        """
        condition_strings = []
        for field, condition in conditions.items():
            if isinstance(condition, dict):
                sub_conditions = self.process_where_conditions(condition)
                condition_strings.append(f"{field}: {{ {sub_conditions} }}")
            else:
                value = f'"{condition}"' if isinstance(condition, str) else condition
                condition_strings.append(f"{field}: {value}")
        return ", ".join(condition_strings)

    def add_query(
        self,
        entity: str,
        items: Optional[Iterable] = None,
        order: Optional[Dict] = None,
        where: Optional[Dict[str, Dict]] = None,
        take: Union[str, int, float] = 50,
        skip: Union[str, int, float] = 0,
    ):
        """Add a GraphQL Query

        :param str entity: the entity to operate
        :param Optional[Iterable] items: a list or iterable of strings to join
        :param Optional[Dict] order: a dict of key value pairs to order on
        :param Optional[Dict[str, Dict]] where: a dict of dicts containing a key and a {op: value}, e.g. {"eq": "value"}
        :param Union[str, int, float] take: the number of objects to take (can be str, int, or float), defaults to 50
        :param Union[str, int, float] skip: the number of objects to skip (can be str, int, or float), defaults to 0
        """
        entity_string = f"{' ' * 4}{entity}(\n{' ' * 8}take: {take},\n{' ' * 8}skip: {skip},\n"
        order_string = ""
        if order is not None:
            order_conditions = ", ".join([f"{k}: {v}" for k, v in order.items()])
            order_string = f"{' ' * 8}order: {{ {order_conditions} }}\n"
        where_string = ""
        if where is not None:
            where_conditions = self.process_where_conditions(conditions=where)
            where_string = f"{' ' * 8}where: {{ {where_conditions} }}){{\n"
        items_string = ""
        if items is not None:
            item_fields = "\n".join(indent(line, " " * 12) for line in items)
            items_string = f"{' ' * 8}items {{\n{item_fields}\n{' ' * 8}}}\n"
        closing_string = f"{' ' * 8}totalCount\n{' ' * 8}pageInfo {{\n{' ' * 12}hasNextPage\n{' ' * 8}}}\n{' ' * 4}}}\n"
        # construct the query
        self.query["query"] += entity_string + where_string + order_string + items_string + closing_string
        return self


if __name__ == "__main__":
    query = GraphQLQuery()
    query.start_query()
    query.add_query(
        entity="securityChecklists",
        items=[
            "id",
            "asset {id name parentId parentModule}",
            "status",
            "tool",
            "datePerformed",
            "vulnerabilityId",
            "ruleId",
            "cci",
            "check",
            "results",
            "baseline",
            "comments",
        ],
        where={
            "asset": {
                "parentId": {"eq": 23423},
                "parentModule": {"eq": "parent_module_placeholder"},
            },
            "status": {"neq": "Completed"},
            "datePerformed": {"lte": "2023-01-01"},
        },
    )
    query.end_query()
    print(query.build())
    user_id = 234234
    before_date = "2023-04-24"
    after_date = "2021-01-01"
    query = GraphQLQuery()
    query.start_query()
    entities = [
        {
            "name": "assessments",
            "order": {"plannedFinish": "DESC"},
            "where": {
                "leadAssessorId": {"eq": user_id},
                "plannedFinish": {"lte": before_date},
                "status": {"nin": ["Complete", "Cancelled"]},
            },
            "items": [
                "uuid",
                "id",
                "title",
                "leadAssessorId",
                "assessmentType",
                "plannedFinish",
                "createdById",
                "dateCreated",
                "status",
                "assessmentResult",
                "actualFinish",
            ],
        },
        {
            "name": "dataCalls",
            "order": {"dateDue": "DESC"},
            "where": {
                "createdById": {"eq": user_id},
                "dateDue": {"lte": before_date},
                "status": {"nin": ["Completed", "Cancelled"]},
            },
            "items": [
                "uuid",
                "id",
                "title",
                "dataCallLeadId",
                "dateDue",
                "createdById",
                "dateCreated",
                "status",
            ],
        },
        {
            "name": "securityPlans",
            "order": {"expirationDate": "DESC"},
            "where": {
                "systemOwnerId": {"eq": user_id},
                "expirationDate": {"lte": before_date},
            },
            "items": [
                "uuid",
                "id",
                "systemName",
                "systemOwnerId",
                "status",
                "systemType",
                "expirationDate",
                "overallCategorization",
                "createdById",
                "dateCreated",
            ],
        },
        {
            "name": "workflowInstances",
            "order": {"startDate": "DESC"},
            "where": {
                "ownerId": {"eq": user_id},
                "status": {"neq": "Complete"},
                "startDate": {"gte": after_date},
                "endDate": {"eq": None},
            },
            "items": [
                "id",
                "name",
                "status",
                "startDate",
                "endDate",
                "comments",
                "currentStep",
                "createdById",
                "dateCreated",
                "lastUpdatedById",
                "ownerId",
                "atlasModule",
                "parentId",
            ],
        },
        {
            "name": "tasks",
            "order": {"dueDate": "DESC"},
            "where": {
                "assignedToId": {"eq": user_id},
                "dueDate": {"lte": before_date},
                "status": {"nin": ["Closed", "Cancelled"]},
            },
            "items": [
                "uuid",
                "id",
                "title",
                "assignedToId",
                "dueDate",
                "createdById",
                "status",
                "percentComplete",
            ],
        },
        {
            "name": "issues",
            "order": {"dueDate": "DESC"},
            "where": {
                "issueOwnerId": {"eq": user_id},
                "dueDate": {"lte": before_date},
                "status": {"nin": ["Closed", "Cancelled"]},
            },
            "items": [
                "uuid",
                "id",
                "title",
                "issueOwnerId",
                "severityLevel",
                "createdById",
                "dateCreated",
                "status",
                "dueDate",
            ],
        },
    ]
    for entity in entities:
        query.add_query(
            entity=entity["name"],
            order=entity["order"],
            where=entity["where"],
            items=entity["items"],
        )
    query.end_query()
    print(query.build())
