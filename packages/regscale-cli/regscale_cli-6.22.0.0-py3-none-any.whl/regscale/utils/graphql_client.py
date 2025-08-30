"""
A module for making paginated GraphQL queries.
"""

import logging
from typing import List, Dict, Optional, Any

import graphql

from regscale.core.app.utils.app_utils import create_progress_object, error_and_exit

logger = logging.getLogger(__name__)


class PaginatedGraphQLClient:
    """
    A class for making paginated GraphQL queries.

    :param str endpoint: The GraphQL endpoint.
    :param str query: The GraphQL query.
    :param Optional[Dict[str, str]] headers: Optional headers to include in the request.
    :param str logging_level: The logging level for the client (default: 'CRITICAL').
    """

    def __init__(
        self,
        endpoint: str,
        query: str,
        headers: Optional[Dict[str, str]] = None,
        logging_level: str = logging.CRITICAL,
    ) -> None:
        from regscale.integrations.variables import ScannerVariables
        from gql import gql, Client  # Optimize import performance
        from gql.transport.requests import RequestsHTTPTransport
        from gql.transport.requests import log as requests_logger

        self.log_level = logging_level
        self.endpoint = endpoint
        self.query = gql(query)
        self.headers = headers or {}  # Ensure headers are a dictionary
        self.transport = RequestsHTTPTransport(url=endpoint, headers=self.headers, verify=ScannerVariables.sslVerify)
        self.client = Client(transport=self.transport)
        self.job_progress = create_progress_object()
        requests_logger.setLevel(level=self.log_level)

    def fetch_all(
        self,
        topic_key: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches all results from the paginated query.

        :param str topic_key: The key to the topic in the response.
        :param Optional[Dict[str, Any]] variables: Optional query variables.
        :return: A list of results.
        :rtype: List[Dict[str, Any]]
        """
        self.job_progress.add_task("[#f68d1f]Fetching data...", total=None)
        results = []
        next_cursor = None
        has_next_page = True
        page_info_default = {"hasNextPage": False, "endCursor": None}
        while has_next_page:
            if data := self.fetch_page(variables=variables, after=next_cursor):
                if nodes := data.get(topic_key, {}).get("nodes"):
                    results.extend(nodes)
                page_info = data.get(topic_key, {}).get("pageInfo") or page_info_default
                logger.debug(f"pageInfo: {page_info}")
                has_next_page = page_info.get("hasNextPage", False)
                next_cursor = page_info.get("endCursor", None)
                if not has_next_page:
                    break
            else:
                break
        return results

    def fetch_page(self, variables: Optional[Dict[str, Any]] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches a single page of results.

        :param Optional[Dict[str, Any]] variables: Optional query variables.
        :param Optional[str] after: The cursor for pagination (optional, defaults to None for the first page).
        :return: A dictionary containing the fetched page of results and pagination information.
        :rtype: Dict[str, Any]
        """
        variables = variables or {}
        variables["after"] = after

        try:
            result = self.client.execute(self.query, variable_values=variables)
            return result
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {str(e)}", exc_info=True)
            logger.error(f"Query: {graphql.print_ast(self.query)}")
            error_and_exit(f"Variable: {variables}")

    def fetch_results(self, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetches a single page of results.

        :param Optional[Dict[str, Any]] variables: Optional query variables.
        :return: A dictionary containing the fetched page of results and pagination information.
        :rtype: Dict[str, Any]
        """
        try:
            result = self.client.execute(self.query, variable_values=variables)
            return result
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {str(e)}", exc_info=True)
            logger.error(f"Query: {self.query}")
            logger.error(f"Variables: {variables}")
            error_and_exit(f"Variable: {variables}")
