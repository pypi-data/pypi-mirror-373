"""
QueryParameter, Query, and Search models used for assets
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QueryParameter(BaseModel):
    """
    QueryParameter object
    """

    id: int = 0
    field: str = ""
    name: str = ""
    type: str = ""
    operator: str = ""
    value: str = ""
    viewName: Optional[str] = ""


class Query(BaseModel):
    id: int = 0
    viewName: str = ""
    module: str = ""
    scope: str = ""
    createdById: str = ""
    dateCreated: Optional[datetime] = datetime.now()
    parameters: List[QueryParameter] = []


class Search(BaseModel):
    """
    Search object
    """

    parentID: int = 0
    module: str = ""
    friendlyName: str = ""
    workbench: str = ""
    base: str = ""
    sort: str = "id"
    direction: str = "Ascending"
    simpleSearch: str = ""
    page: int = 0
    pageSize: int = 0
    query: Optional[Query] = None
    groupBy: str = ""
    intDays: int = 0
    subTab: bool = False
