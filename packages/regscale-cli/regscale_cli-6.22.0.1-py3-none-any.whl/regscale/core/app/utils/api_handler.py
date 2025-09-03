"""
API Handler class to handle API requests using API class
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib import parse
from urllib.parse import urljoin

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import parse_user_id_from_jwt

logger = logging.getLogger()


class APIRetrieveError(Exception):
    """Exception raised when there is an error retrieving data via API."""

    pass


class APIInsertionError(Exception):
    """Exception raised when there is an error inserting data into the API."""

    pass


class APIUpdateError(Exception):
    """Exception raised when there is an error updating data in the API."""

    pass


class APIResponseError(Exception):
    """Exception raised when there is an error in the API response."""

    pass


class APIHandler(Application):
    """Class to handle API requests."""

    def __init__(self):
        logger.debug("Instantiating APIHandler")
        super().__init__()

        if self.api_handler is None:
            self.api: Api = Api()
            self.domain: str = self.api.config["domain"]
            self.endpoint_tracker: Dict[str, Dict[str, Union[int, float, set]]] = {}  # Initialize the endpoint tracker
            self.api_handler: APIHandler = self  # type: ignore
        else:
            logger.warning("APIHandler already set for Application. Not initializing a new instance.")
            return

        self._regscale_version: Optional[str] = None  # Initialize version as None

    @property
    def regscale_version(self) -> str:
        """
        Get the version from the API endpoint.

        :return: The version string
        :rtype: str
        """
        from regscale.utils.version import RegscaleVersion

        rs_version = RegscaleVersion()
        if self._regscale_version is None:
            self._regscale_version = rs_version.current_version
        return self._regscale_version

    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        query: Optional[str] = None,
        files: Optional[List[Any]] = None,
        params: Optional[Any] = None,
        retry_login: bool = True,
    ) -> Any:
        """
        Generic function to make API requests.

        :param str method: HTTP method ('get', 'post', 'put')
        :param str endpoint: API endpoint, domain is added automatically
        :param Dict[str, Any] headers: Optional headers
        :param Union[Dict[str, Any], List[Any]] data: Data to send
        :param str query: Optional GraphQL query
        :param List[Any] files: Optional files to send
        :param Any params: Optional query parameters
        :param bool retry_login: Whether to retry login on 401, defaults to True
        :return: Response data or None
        :rtype: Any
        """
        start_time = time.time()
        self._update_endpoint_tracker(endpoint, method)

        url = self._get_url(endpoint)
        if not url:
            return None

        logger.debug("[API_HANDLER] - Making %s request to %s", method.upper(), url)
        response = None
        try:
            response = self._send_request(method, url, headers, data, query, files, params, retry_login)
            return response
        except Exception as e:
            self._log_error(e, response)
            return response
        finally:
            self._update_endpoint_time(endpoint, start_time)

    def _update_endpoint_tracker(self, endpoint: str, method: str) -> None:
        """
        Update the endpoint tracker with the current request.

        :param str endpoint: The API endpoint
        :param str method: The HTTP method used
        """
        if endpoint not in self.endpoint_tracker:
            self.endpoint_tracker[endpoint] = {
                "count": 0,
                "methods": set(),
                "time": 0,
                "get": 0,
                "put": 0,
                "post": 0,
                "delete": 0,
                "graph": 0,
            }
        self.endpoint_tracker[endpoint]["count"] += 1
        self.endpoint_tracker[endpoint]["methods"].add(method)
        self.endpoint_tracker[endpoint][method.lower()] += 1

    def _get_url(self, endpoint: str) -> Optional[str]:
        """
        Get the full URL for the given endpoint.

        :param str endpoint: The API endpoint
        :return: The full URL or None if it couldn't be constructed
        :rtype: Optional[str]
        """
        url = urljoin(self.domain, parse.quote(str(endpoint)))  # type: ignore
        if not url:
            logger.error("[API_HANDLER] - URL is empty or None")
        return url

    def _send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, Any]],
        data: Any,
        query: Optional[str],
        files: Optional[List[Any]],
        params: Any,
        retry_login: Optional[bool] = True,
    ) -> Any:
        """
        Send the actual HTTP request.

        :param str method: The HTTP method
        :param str url: The full URL
        :param Dict[str, Any] headers: The request headers
        :param Any data: The request data
        :param str query: The GraphQL query (if applicable)
        :param List[Any] files: The files to send (if applicable)
        :param Any params: The query parameters
        :param Optional[bool] retry_login: Whether to retry login on 401, defaults to True
        :return: The API response
        :rtype: Any
        """
        if method == "get":
            return self.api.get(url=url, headers=headers, params=params, retry_login=retry_login, merge_headers=True)
        elif method == "delete":
            return self.api.delete(url=url, headers=headers, retry_login=retry_login, merge_headers=True)
        elif method == "post" and files:
            return self.api.post(
                url, headers=headers, data=data, params=params, files=files, retry_login=retry_login, merge_headers=True
            )
        elif method == "graph":
            return self.api.graph(query=query, headers=headers, merge_headers=True)
        else:
            return getattr(self.api, method)(
                url, headers=headers, json=data, params=params, retry_login=retry_login, merge_headers=True
            )

    @staticmethod
    def _log_error(e: Exception, response: Any) -> None:
        """
        Log errors that occur during API requests.

        :param Exception e: The exception that occurred
        :param Any response: The API response (if available)
        """
        logger.error(f"An error occurred: {e}", exc_info=True)
        if response is not None:
            logger.error(f"Response Code: {response.status_code} - {response.text}")

    def _update_endpoint_time(self, endpoint: str, start_time: float) -> None:
        """
        Update the total time spent on an endpoint.

        :param str endpoint: The API endpoint
        :param float start_time: The start time of the request
        """
        total_time = time.time() - start_time
        self.endpoint_tracker[endpoint]["time"] += total_time

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Fetch a record from RegScale.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Any params: Optional query parameters
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request("get", endpoint, headers=headers, params=params)

    def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        files: Optional[List[Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Insert new data into an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Union[Dict[str, Any], List[Any]] data: Data to send
        :param List[Any] files: Files to send
        :param Any params: Optional query parameters
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request(
            "post",
            endpoint,
            headers=headers,
            data=data,
            params=params,
            files=files,
        )

    def put(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Union[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Update existing data in an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Union[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]] data: Data to send
        :param Any params: Optional query parameters
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request("put", endpoint, headers=headers, data=data, params=params)

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Delete existing data in an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Any params: Optional query parameters
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request("delete", endpoint, headers=headers, params=params)

    def graph(self, query: str) -> Any:
        """
        Fetch data from the graph API.

        :param str query: GraphQL query
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request("graph", "/graphql", query=query)

    def get_user_id(self) -> str:
        """
        Get the user ID of the current user.

        :return: The user ID of the current user.
        :rtype: str
        """
        return parse_user_id_from_jwt(self, self.config["token"])

    def get_config_user_id(self) -> str:
        """
        Get the user ID of the current user.

        :return: The user ID of the current user.
        :rtype: str
        """
        return self.config.get("userId", "")

    def log_api_summary(self) -> None:
        """
        Log a summary of API calls made during the lifetime of this APIHandler instance.
        """
        logger.info("APIHandler instance is being destroyed. Summary of API calls:")

        total_calls = 0
        total_time = 0.0

        for endpoint, details in sorted(
            self.endpoint_tracker.items(),
            key=lambda item: item[1]["time"],
            reverse=False,
        ):
            methods = ", ".join(details["methods"])
            count = details["count"]
            total_calls += count
            total_time += details["time"]
            logger.debug(
                f"Endpoint '{endpoint}' was called {count} times with methods: {methods} and total time: "
                f"{details['time']:.2f}s "
                f"gets: {details['get']} puts: {details['put']} posts: {details['post']} deletes: {details['delete']} graphs: {details['graph']}"
            )

        logger.info(f"Total API calls: {total_calls}")
        logger.info(f"Total time spent on API calls: {total_time:.2f}s")
