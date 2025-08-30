#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""standard imports"""

import concurrent.futures
import logging
import os
import re
import warnings
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from regscale.core.app.application import Application

import requests
from requests.adapters import HTTPAdapter, Retry
from rich.progress import Progress
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from regscale.core.app.internal.login import login, verify_token


class Api:
    """Wrapper for interacting with the RegScale API

    :param Optional[Application] app: Application object, defaults to None
    :param int timeout: timeout for API calls, defaults to 10
    :param Union[int, str] retry: number of retries for API calls, defaults to 5
    """

    _app: "Application"
    app: "Application"
    _retry_log: str = "Retrying request with new token."
    _no_res_text: str = "No response text available"
    _ssl_warning_displayed: bool = False

    def __init__(
        self,
        timeout: int = int(os.getenv("REGSCALE_TIMEOUT", 10)),
        retry: int = 5,
    ):
        from regscale.core.app.application import Application
        from regscale.integrations.variables import ScannerVariables

        if isinstance(timeout, str):
            timeout = int(timeout)

        self.verify = True
        self.timeout = timeout
        self.accept = "application/json"
        self.content_type = "application/json"
        r_session = requests.Session()
        self.pool_connections = 200
        self.pool_maxsize = 200
        self.retries = Retry(total=retry, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.auth = None
        super().__init__()
        self.app = Application()
        self.logger = logging.getLogger("regscale")
        self.verify = ScannerVariables.sslVerify
        if not self.verify:
            if not Api._ssl_warning_displayed:
                self.logger.warning("SSL Verification has been disabled.")
                Api._ssl_warning_displayed = True
            r_session.verify = False
            disable_warnings(InsecureRequestWarning)
        if self.config and "timeout" in self.config:
            self.timeout = self.config["timeout"]
        # get the user's domain prefix eg https:// or http://
        domain = self.config.get("domain") or self.app.retrieve_domain()
        domain = domain[: (domain.find("://") + 3)]
        r_session.mount(
            domain,
            HTTPAdapter(
                max_retries=self.retries,
                pool_connections=self.pool_connections,
                pool_maxsize=self.pool_maxsize,
                pool_block=True,
            ),
        )
        self.session = r_session

    @property
    def config(self) -> dict:
        """
        Get the application config

        :return: Application config
        :rtype: dict
        """
        return self.app.config

    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[Union[list, Tuple]] = None,
        retry_login: bool = True,
        merge_headers: bool = False,
    ) -> Optional[requests.models.Response]:
        """
        Get Request for API

        :param str url: URL for API call
        :param dict headers: headers for the api get call, defaults to None
        :param Optional[Union[list, Tuple]] params: Any parameters for the API call, defaults to None
        :param bool retry_login: Whether to retry login on 401 Unauthorized responses, defaults to True
        :param bool merge_headers: Whether to merge headers, defaults to False
        :return: Requests response
        :rtype: Optional[requests.models.Response]
        """
        url = normalize_url(url)
        if self.auth:
            self.session.auth = self.auth
        headers = self._handle_headers(headers, merge_headers)
        response = None
        try:
            self.logger.debug("GET: %s", url)
            response = self.session.get(
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            if response.status_code == 401 and self._handle_401(retry_login):
                self.logger.debug(self._retry_log)
                response = self.get(url=url, headers=headers, params=params, retry_login=False)
            return response
        except Exception as e:
            self._log_response_error(url, e, response)
            return response
        finally:
            resp_text = getattr(response, "text", self._no_res_text)
            self.logger.debug(f"{resp_text[:500]}..." if len(str(resp_text)) > 500 else resp_text)

    def delete(
        self, url: str, headers: Optional[dict] = None, retry_login: bool = True, merge_headers: bool = False
    ) -> requests.models.Response:
        """
        Delete data using API

        :param str url: URL for the API call
        :param Optional[dict] headers: headers for the API call, defaults to None
        :param bool retry_login: Whether to retry login on 401 Unauthorized responses, defaults to True
        :param bool merge_headers: Whether to merge headers, defaults to False
        :return: API response
        :rtype: requests.models.Response
        """
        url = normalize_url(url)
        if self.auth:
            self.session.auth = self.auth
        headers = self._handle_headers(headers, merge_headers)
        response = None
        try:
            self.logger.debug("Delete: %s", url)
            response = self.session.delete(
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
            if response.status_code == 401 and self._handle_401(retry_login):
                self.logger.debug(self._retry_log)
                response = self.delete(url=url, headers=headers, retry_login=False)
            return response
        except Exception as e:
            self._log_response_error(url, e, response)
            return response
        finally:
            self.logger.debug(getattr(response, "text", self._no_res_text))

    def post(
        self,
        url: str,
        headers: Optional[dict] = None,
        json: Optional[Union[dict, str, list]] = None,
        data: Optional[dict] = None,
        files: Optional[list] = None,
        params: Any = None,
        retry_login: bool = True,
        merge_headers: bool = False,
    ) -> Optional[requests.models.Response]:
        """
        Post data to API

        :param str url: URL for the API call
        :param dict headers: Headers for the API call, defaults to None
        :param Optional[Union[dict, str, list]] json: Dictionary of data for the API call, defaults to None
        :param dict data: Dictionary of data for the API call, defaults to None
        :param list files: Files to post during API call, defaults to None
        :param Any params: Any parameters for the API call, defaults to None
        :param bool retry_login: Whether to retry login on 401 Unauthorized responses, defaults to True
        :param bool merge_headers: Whether to merge headers, defaults to False
        :return: API response
        :rtype: Optional[requests.models.Response]
        """
        url = normalize_url(url)
        if self.auth:
            self.session.auth = self.auth
        headers = self._handle_headers(headers, merge_headers)
        response = None

        # Do not send Authorization headers if validatToken in endpoint
        if "validateToken" in url:
            headers.pop("Authorization", None)

        try:
            self.logger.debug("POST: %s", url)
            if not json and data:
                response = self.session.post(
                    url=url,
                    headers=headers,
                    data=data,
                    files=files,
                    params=params,
                    timeout=self.timeout,
                )
            else:
                response = self.session.post(
                    url=url,
                    headers=headers,
                    json=json,
                    files=files,
                    params=params,
                    timeout=self.timeout,
                )
            if getattr(response, "status_code", 0) == 401 and self._handle_401(retry_login):
                self.logger.debug(self._retry_log)
                response = self.post(
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                    retry_login=False,
                )
            return response
        except Exception as e:
            self._log_response_error(url, e, response)
            return response
        finally:
            self.logger.debug(getattr(response, "text", self._no_res_text))

    def put(
        self,
        url: str,
        headers: Optional[dict] = None,
        json: Optional[Union[dict, List[dict]]] = None,
        params: Optional[Union[list, Tuple]] = None,
        retry_login: bool = True,
        merge_headers: bool = False,
    ) -> Optional[requests.models.Response]:
        """
        Update data via API call

        :param str url: URL for the API call
        :param Optional[dict] headers: Headers for the API call, defaults to None
        :param Optional[Union[dict, List[dict]]] json: Dictionary of data for the API call, defaults to None
        :param Optional[Union[list, Tuple]] params: Any parameters for the API call, defaults to None
        :param bool retry_login: Whether to retry login on 401 Unauthorized responses, defaults to True
        :param bool merge_headers: Whether to merge headers, defaults to False
        :return: API response if
        :rtype: Optional[requests.models.Response]
        """
        url = normalize_url(url)
        if self.auth:
            self.session.auth = self.auth
        headers = self._handle_headers(headers, merge_headers)
        response = None
        try:
            self.logger.debug("PUT: %s", url)
            response = self.session.put(
                url=url,
                headers=headers,
                json=json,
                params=params,
                timeout=self.timeout,
            )

            if getattr(response, "status_code", 0) == 401 and self._handle_401(retry_login):
                self.logger.debug(self._retry_log)
                response = self.put(
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    retry_login=False,
                )
            return response
        except Exception as e:
            self._log_response_error(url, e, response)
            return response
        finally:
            self.logger.debug(getattr(response, "text", self._no_res_text))

    def graph(
        self,
        query: str,
        url: Optional[str] = None,
        headers: Optional[dict] = None,
        res_data: Optional[dict] = None,
        merge_headers: bool = False,
    ) -> dict:
        """
        Execute GraphQL query and handles pagination before returning the data to the API call

        :param str query: the GraphQL query to execute
        :param Optional[str] url: URL for the API call, defaults to None
        :param Optional[dict] headers: Headers for the API call, defaults to None
        :param Optional[dict] res_data: dictionary of data from GraphQL response, only used during pagination & recursion
        :param bool merge_headers: Whether to merge headers, defaults to False
        :return: Dictionary response from GraphQL API
        :rtype: dict
        """
        self.logger.debug("STARTING NEW GRAPH CALL")
        self.logger.debug("=" * 50)
        response_data = {}
        pagination_flag = False
        # change the timeout to match the timeout of the GraphQL timeout in the application
        self.timeout = 90
        if self.auth:
            self.session.auth = self.auth
        headers = self._handle_headers(headers, merge_headers)
        # check the query if skip was provided, if not add it for pagination
        if "skip" not in query:
            query = query.replace("(", "(skip: 0\n")
        # set the url for the query
        url = normalize_url(f'{self.config["domain"]}/graphql' if url is None else url)
        self.logger.debug(f"{url=}")
        self.logger.debug(f"{query=}")
        # make the API call
        response = self.session.post(
            url=normalize_url(url),
            headers=headers,
            json={"query": query},
            timeout=self.timeout,
        )
        self.logger.debug(f"{response.text=}")
        try:
            response_json = response.json()
            if "errors" in response_json:
                self.logger.error("GraphQL query returned errors:")
                for error in response_json["errors"]:
                    self.logger.error(f"Message: {error.get('message')}")
                    self.logger.error(f"Locations: {error.get('locations')}")
                    self.logger.error(f"Path: {error.get('path')}")
                self.logger.error(f"Query that caused the error: {query}", exc_info=True)
                return {}  # Return an empty dict instead of exiting
            # convert response to JSON object
            response_data = response_json["data"]
            self.logger.debug(f"{response_data=}")
            # iterate through and add it to the res_data if needed
            for key, value in response_data.items():
                # add the new API response data to the data from previous call
                if res_data:
                    res_data[key]["items"].extend(response_data[key]["items"])
                # check if pagination required
                try:
                    if value.get("pageInfo").get("hasNextPage") is True and not pagination_flag:
                        # set pagination_flag to true
                        pagination_flag = True
                        # find the location of the old skip in the query and parse the int after it
                        old_skip_match = re.search(r"skip: (\d+)", query)
                        if old_skip_match:
                            old_skip = int(old_skip_match.group(1))

                            # set the new value of the skip using old + # of items returned
                            new_skip = old_skip + len(response_data[key]["items"])

                            # replace the old skip value with the new skip value that was calculated
                            query = query.replace(f"skip: {old_skip}", f"skip: {new_skip}")
                        else:
                            # If no skip found, add it to the beginning of the query
                            new_skip = len(response_data[key]["items"])
                            query = query.replace("(", f"(skip: {new_skip}\n", 1)

                        # if no previous pagination, break this loop
                        if not res_data:
                            break
                except (KeyError, AttributeError):
                    continue
        except requests.exceptions.JSONDecodeError as err:
            self.logger.error("Received JSONDecodeError!\n%s", err)
            self.logger.debug("%i: %s - %s", response.status_code, response.text, response.reason)
            return {}
        except KeyError as err:
            self.logger.error("No items were returned from %s!\n%s", url, err)
            self.logger.debug("%i: %s - %s", response.status_code, response.text, response.reason)
            return {}
        # check if already called for recursion
        # res_data: set data to pagination data
        # response_data: most recent API call
        data = res_data or response_data
        if pagination_flag:
            # recall the function with the new query and extend the data with the results
            response_data = self.graph(url=url, headers=headers, query=query, res_data=data)
            # set the data to the pagination data
            data = response_data
        # return the data
        return data

    def update_server(
        self,
        url: str,
        headers: Optional[dict] = None,
        json_list: Optional[list] = None,
        method: str = "post",
        config: Optional[dict] = None,
        message: str = "Working",
    ) -> None:
        """
        Concurrent Post or Put of multiple objects

        The 'update_server' method is deprecated, use 'RegScaleModel' create or update methods instead

        :param str url: URL for the API call
        :param Optional[dict] headers: Headers for the API call, defaults to None
        :param Optional[list] json_list: Dictionary of data for the API call, defaults to None
        :param str method: Method for API to use, defaults to "post"
        :param Optional[dict] config: Config for the API, defaults to None
        :param str message: Message to display in console, defaults to "Working"
        :rtype: None
        """
        warnings.warn(
            "The 'update_server' method is deprecated, use 'RegScaleModel' create or update methods instead",
            DeprecationWarning,
        )
        if headers is None and config:
            headers = {"Accept": self.accept, "Authorization": config["token"]}

        if json_list and len(json_list) > 0:
            with Progress(transient=False) as progress:
                task = progress.add_task(message, total=len(json_list))
                # Ensure maxThreads is an integer for ThreadPoolExecutor
                max_workers = self.config.get("maxThreads", 100)
                if not isinstance(max_workers, int):
                    try:
                        max_workers = int(max_workers)
                    except (ValueError, TypeError):
                        max_workers = 100
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    if method.lower() == "post":
                        result_futures = list(
                            map(
                                lambda x: executor.submit(self.post, url, headers, x),
                                json_list,
                            )
                        )
                    if method.lower() == "put":
                        result_futures = list(
                            map(
                                lambda x: executor.submit(self.put, f"{url}/{x['id']}", headers, x),
                                json_list,
                            )
                        )
                    if method.lower() == "delete":
                        result_futures = list(
                            map(
                                lambda x: executor.submit(self.delete, f"{url}/{x['id']}", headers),
                                json_list,
                            )
                        )
                    for future in concurrent.futures.as_completed(result_futures):
                        try:
                            if future.result().status_code != 200:
                                self.logger.warning(
                                    "Status code is %s: %s from %s.",
                                    future.result().status_code,
                                    future.result().text,
                                    future.result().url,
                                )
                            progress.update(task, advance=1)
                        except Exception as ex:
                            self.logger.error("Error is %s, type: %s", ex, type(ex))

    def _log_response_error(
        self,
        url: str,
        error: Exception,
        response: Optional[requests.Response],
    ) -> None:
        """
        Log error messages from API responses

        :param str url: URL for the API call
        :param Exception error: Exception message
        :param Optional[requests.Response] response: API response
        :param str url: URL for the API call
        """
        if response is None:
            self.logger.error("Received unexpected response from %s: %s", url, error)
        else:
            self.logger.error(
                "Received unexpected response from %s %s\nStatus code %s: %s\nText: %s",
                url,
                error,
                response.status_code,
                response.reason,
                response.text,
            )

    def _handle_login_on_401(
        self,
        retry_login: bool = True,
    ) -> bool:
        """
        Handle login on 401 Unauthorized responses

        :param bool retry_login: Whether to retry login or not, defaults to True
        :return: Whether login was successful
        :rtype: bool
        """
        token = self.config.get("token")
        if token and "Bearer " in token:
            token = token.split("Bearer ")[1]
        self.logger.debug("verifying token")
        is_token_valid = verify_token(app=self.app, token=token)
        self.logger.debug(f"is token valid: {is_token_valid}")
        if not is_token_valid:
            self.logger.debug("getting new token")
            new_token = login(
                app=self.app,
                str_user=os.getenv("REGSCALE_USERNAME"),
                str_password=os.getenv("REGSCALE_PASSWORD"),
                host=self.config["domain"],
            )
            self.logger.debug("Token: %s", new_token[:20])
            return retry_login
        return False

    def _handle_401(self, retry_login: bool) -> bool:
        """
        Handle 401 Unauthorized responses.

        :param bool retry_login: Whether to retry login
        :return: True if login was retried, False otherwise
        :rtype: bool
        """
        if self._handle_login_on_401(retry_login=retry_login):
            self.logger.debug("Retrying request with new token.")
            return True
        return False

    def _handle_headers(self, headers: Optional[dict], merge_headers=False) -> dict:
        """
        Handle headers for API calls

        :param Optional[dict] headers: Headers for the API call
        :param bool merge_headers: Whether to merge headers with defaults
        :return: Dictionary of headers
        :rtype: dict
        """
        default_headers = {
            "accept": self.accept,
            "Content-Type": self.content_type,
        }
        if token := self.config.get("token"):
            default_headers["Authorization"] = token

        if headers is None:
            headers = default_headers

        headers = headers or {}

        if merge_headers:
            return {**default_headers, **headers}

        return headers


def normalize_url(url: str) -> str:
    """
    Function to remove extra slashes and trailing slash from a given URL

    :param str url: URL string normalize
    :return: A normalized URL
    :rtype: str
    """
    segments = url.split("/")
    correct_segments = [segment for segment in segments if segment != ""]
    first_segment = str(correct_segments[0])
    if "http" not in first_segment:
        correct_segments = ["http:"] + correct_segments
    correct_segments[0] = f"{correct_segments[0]}/"
    return "/".join(correct_segments)
