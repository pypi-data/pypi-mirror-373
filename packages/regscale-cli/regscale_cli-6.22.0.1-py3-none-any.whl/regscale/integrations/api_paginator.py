#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Paginator for RegScale integrations.

This class provides a reusable way to fetch paginated API responses and optionally
write results to JSONL files for processing by scanner integrations.
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from regscale.exceptions import ValidationException

logger = logging.getLogger("regscale")

# Constants for common patterns and protocols
HTTPS_PREFIX = "https://"  # NOSONAR
HTTP_PATTERN = "http://"  # NOSONAR
ALLOWED_PAGINATION_TYPES = ["offset", "page", "token", "cursor", "custom"]
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
ALLOWED_HTTP_METHODS = ["GET", "POST"]
DEFAULT_PAGE_SIZE = 100
WRITE_MODE = "w"
APPEND_MODE = "a"


class ApiPaginator:
    """
    A utility class to handle API pagination and write results to a JSONL file.

    This class is designed to work with RESTful APIs that use common pagination patterns.
    It can retrieve all pages of results and optionally write them to a file for further processing.

    Supports various pagination methods:
    - Offset/limit pagination
    - Page/per_page pagination
    - Token-based pagination
    - Cursor-based pagination

    Also includes error handling, rate limiting, and concurrent requests.
    """

    def __init__(
        self,
        base_url: str,
        auth_headers: Dict[str, str],
        output_file: Optional[str] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: Optional[int] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_backoff_factor: float = 0.5,
        throttle_rate: Optional[float] = None,
        concurrent_requests: int = 1,
        ssl_verify: bool = True,
    ):
        """
        Initialize the API Paginator.

        Args:
            base_url (str): The base URL for the API
            auth_headers (Dict[str, str]): Authentication headers for the API
            output_file (Optional[str]): Path to write results to (JSONL format)
            page_size (int): Number of items per page to request
            max_pages (Optional[int]): Maximum number of pages to retrieve (None for all)
            timeout (int): Request timeout in seconds
            retry_attempts (int): Number of times to retry failed requests
            retry_backoff_factor (float): Backoff factor for retries
            throttle_rate (Optional[float]): Seconds to wait between requests (rate limiting)
            concurrent_requests (int): Number of concurrent requests to make
            ssl_verify (bool): Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.auth_headers = auth_headers
        self.output_file = output_file
        self.page_size = page_size
        self.max_pages = max_pages
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_backoff_factor = retry_backoff_factor
        self.throttle_rate = throttle_rate
        self.concurrent_requests = max(1, concurrent_requests)
        self.ssl_verify = ssl_verify

        # Initialize session with retry capability
        self.session = self._create_session()

        # Ensure output directory exists if file is specified
        self._ensure_output_dir_exists()

    def _ensure_output_dir_exists(self) -> None:
        """Ensure the output directory exists if output file is specified."""
        if self.output_file:
            output_dir = os.path.dirname(os.path.abspath(self.output_file))
            os.makedirs(output_dir, exist_ok=True)

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry capability.

        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.retry_attempts,
            backoff_factor=self.retry_backoff_factor,
            status_forcelist=RETRY_STATUS_CODES,
            allowed_methods=ALLOWED_HTTP_METHODS,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount(HTTPS_PREFIX, adapter)

        # Only mount HTTP adapter if SSL verification is disabled (for internal/development use)
        if not self.ssl_verify:
            session.mount(HTTP_PATTERN, adapter)
            logger.warning(
                "HTTP protocol enabled due to disabled SSL verification. Not recommended for production use."
            )

        # Add default headers
        session.headers.update(self.auth_headers)

        return session

    def _prepare_pagination_params(
        self, pagination_type: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare pagination parameters based on pagination type.

        Args:
            pagination_type (str): Type of pagination
            params (Optional[Dict[str, Any]]): Existing parameters

        Returns:
            Dict[str, Any]: Updated parameters
        """
        current_params = params.copy() if params else {}

        if pagination_type == "offset":
            current_params["limit"] = self.page_size
            current_params["offset"] = 0
        elif pagination_type == "page":
            current_params["per_page"] = self.page_size
            current_params["page"] = 1

        return current_params

    def _apply_throttling(self, page_count: int) -> None:
        """Apply throttling between requests if configured.

        Args:
            page_count (int): Current page count
        """
        if self.throttle_rate and page_count > 0:
            time.sleep(self.throttle_rate)

    def _make_request(
        self, url: str, params: Dict[str, Any], request_method: str, post_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request and handle errors.

        Args:
            url (str): URL to request
            params (Dict[str, Any]): Query parameters
            request_method (str): HTTP method (GET/POST)
            post_data (Optional[Dict[str, Any]]): Data for POST requests

        Returns:
            Optional[Dict[str, Any]]: Response data or None on error
        """
        response = None
        try:
            if request_method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout, verify=self.ssl_verify)
            else:  # POST
                response = self.session.post(
                    url, params=params, json=post_data, timeout=self.timeout, verify=self.ssl_verify
                )

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            logger.debug(f"Response: {response.text if hasattr(response, 'text') else 'No response text'}")
            return None
        except ValueError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return None

    def _extract_data(self, result: Dict[str, Any], data_path: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract data from API response based on data path.

        Args:
            result (Dict[str, Any]): API response
            data_path (Optional[str]): Path to data in response

        Returns:
            Optional[List[Dict[str, Any]]]: Extracted data items or None
        """
        if not result:
            return None

        if data_path:
            # Navigate the nested structure to find data
            data = self._navigate_data_path(result, data_path)
            if not data:
                return None
        else:
            # Use the entire response if no path is specified
            data = result

        # Convert to list if it's not already
        return data if isinstance(data, list) else [data]

    def _navigate_data_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Navigate a nested structure using a dot-separated path.

        Args:
            data (Dict[str, Any]): The data structure to navigate
            path (str): Dot-separated path

        Returns:
            Any: The value found or empty dict if not found
        """
        result = data
        for key in path.split("."):
            result = result.get(key, {})
            if not result and result != 0:  # Handle 0 as a valid value
                logger.warning(f"No data found at path '{path}' in response")
                return None
        return result

    def _write_items_to_file(self, items: List[Dict[str, Any]], output_file: str, file_mode: str) -> None:
        """
        Write items to JSONL file.

        Args:
            items (List[Dict[str, Any]]): Items to write
            output_file (str): Path to output file
            file_mode (str): File mode (w/a)
        """
        try:
            with open(output_file, file_mode) as f:
                for item in items:
                    f.write(json.dumps(item) + "\n")
        except IOError as e:
            logger.error(f"Error writing to file {output_file}: {str(e)}")

    def _process_offset_pagination(
        self, current_params: Dict[str, Any], items: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process offset-based pagination.

        Args:
            current_params (Dict[str, Any]): Current parameters
            items (List[Dict[str, Any]]): Current items

        Returns:
            Tuple[bool, Dict[str, Any]]: (has_more, updated_params)
        """
        current_params["offset"] += self.page_size
        # Auto-detect if we've reached the end
        has_more = len(items) == self.page_size
        return has_more, current_params

    def _process_page_pagination(
        self, current_params: Dict[str, Any], items: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process page-based pagination.

        Args:
            current_params (Dict[str, Any]): Current parameters
            items (List[Dict[str, Any]]): Current items

        Returns:
            Tuple[bool, Dict[str, Any]]: (has_more, updated_params)
        """
        current_params["page"] += 1
        # Auto-detect if we've reached the end
        has_more = len(items) == self.page_size
        return has_more, current_params

    def _process_token_pagination(
        self, result: Dict[str, Any], current_params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process token-based pagination.

        Args:
            result (Dict[str, Any]): Current response
            current_params (Dict[str, Any]): Current parameters

        Returns:
            Tuple[bool, Dict[str, Any]]: (has_more, updated_params)
        """
        next_token = self._extract_next_token(result)
        if next_token:
            current_params["next_token"] = next_token
            return True, current_params
        return False, current_params

    def _process_cursor_pagination(
        self, result: Dict[str, Any], current_params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process cursor-based pagination.

        Args:
            result (Dict[str, Any]): Current response
            current_params (Dict[str, Any]): Current parameters

        Returns:
            Tuple[bool, Dict[str, Any]]: (has_more, updated_params)
        """
        cursor = self._extract_cursor(result)
        if cursor:
            current_params["cursor"] = cursor
            return True, current_params
        return False, current_params

    def _process_custom_pagination(
        self,
        result: Dict[str, Any],
        current_params: Dict[str, Any],
        next_page_extractor: Callable[[Dict[str, Any]], Optional[str]],
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Process custom pagination using extractor function.

        Args:
            result (Dict[str, Any]): Current response
            current_params (Dict[str, Any]): Current parameters
            next_page_extractor (Callable): Function to extract next page

        Returns:
            Tuple[bool, str, Dict[str, Any]]: (has_more, url, updated_params)
        """
        next_page = next_page_extractor(result)
        if not next_page:
            return False, "", current_params

        # Validate URL if it's a full URL
        if next_page.startswith(HTTPS_PREFIX):
            return True, next_page, current_params
        elif next_page.startswith(HTTP_PATTERN) and not self.ssl_verify:
            # Only allow HTTP URLs when SSL verification is disabled
            logger.warning("Using insecure HTTP URL for pagination")
            return True, next_page, current_params
        else:
            # Just a token or path
            current_params["next"] = next_page
            return True, "", current_params

    def _process_next_page(
        self,
        pagination_type: str,
        result: Dict[str, Any],
        current_params: Dict[str, Any],
        items: List[Dict[str, Any]],
        next_page_extractor: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process pagination for the next page.

        Args:
            pagination_type (str): Type of pagination
            result (Dict[str, Any]): Current page result
            current_params (Dict[str, Any]): Current parameters
            items (List[Dict[str, Any]]): Current page items
            next_page_extractor (Optional[Callable]): Custom extractor function

        Returns:
            Tuple[bool, str, Dict[str, Any]]: (has_more, url, updated_params)
        """
        url = ""  # Default empty URL (no change)

        if pagination_type == "offset":
            has_more, current_params = self._process_offset_pagination(current_params, items)
        elif pagination_type == "page":
            has_more, current_params = self._process_page_pagination(current_params, items)
        elif pagination_type == "token":
            has_more, current_params = self._process_token_pagination(result, current_params)
        elif pagination_type == "cursor":
            has_more, current_params = self._process_cursor_pagination(result, current_params)
        elif pagination_type == "custom" and next_page_extractor:
            has_more, url, current_params = self._process_custom_pagination(result, current_params, next_page_extractor)
        else:
            # Default - no more pages
            has_more = False

        return has_more, url, current_params

    def _setup_pagination(
        self, endpoint: str, pagination_type: str, params: Optional[Dict[str, Any]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Setup initial pagination state.

        Args:
            endpoint (str): API endpoint
            pagination_type (str): Type of pagination
            params (Optional[Dict[str, Any]]): Query parameters

        Returns:
            Tuple[str, Dict[str, Any]]: (url, current_params)
        """
        # Validate pagination type
        if pagination_type not in ALLOWED_PAGINATION_TYPES:
            raise ValidationException(f"Invalid pagination type: {pagination_type}")

        # Build full URL and prepare parameters
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        current_params = self._prepare_pagination_params(pagination_type, params)

        return url, current_params

    def _process_result_page(
        self, result: Dict[str, Any], data_path: Optional[str], output_mode: Optional[str]
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str], int]:
        """
        Process a page of results.

        Args:
            result (Dict[str, Any]): API response
            data_path (Optional[str]): Path to data
            output_mode (Optional[str]): File mode for output

        Returns:
            Tuple[Optional[List[Dict[str, Any]]], Optional[str], int]:
                (items, new_output_mode, item_count)
        """
        items = self._extract_data(result, data_path)
        if not items:
            return None, output_mode, 0

        # Process items - either write to file or prepare to yield
        if self.output_file and output_mode:
            self._write_items_to_file(items, self.output_file, output_mode)
            # Use append mode for subsequent pages
            return items, APPEND_MODE, len(items)

        # For streaming mode, items will be yielded by caller
        return items, output_mode, len(items)

    def _fetch_next_page(
        self,
        url: str,
        current_params: Dict[str, Any],
        request_method: str,
        post_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch the next page of results.

        Args:
            url (str): URL to request
            current_params (Dict[str, Any]): Current parameters
            request_method (str): HTTP method
            post_data (Optional[Dict[str, Any]]): Data for POST requests

        Returns:
            Optional[Dict[str, Any]]: The API response or None on error
        """
        return self._make_request(url, current_params, request_method, post_data)

    def _yield_items(self, items: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Yield items to the caller in streaming mode.

        Args:
            items (List[Dict[str, Any]]): Items to yield

        Returns:
            Iterator[Dict[str, Any]]: Iterator of items
        """
        for item in items:
            yield item

    def _should_continue_pagination(
        self,
        has_more: bool,
        page_count: int,
    ) -> bool:
        """
        Determine if pagination should continue.

        Args:
            has_more (bool): Whether there are more results
            page_count (int): Current page count

        Returns:
            bool: True if pagination should continue
        """
        return has_more and (self.max_pages is None or page_count < self.max_pages)

    def _log_pagination_progress(
        self,
        page_count: int,
        item_count: int,
        url: Optional[str] = None,
    ) -> None:
        """
        Log pagination progress.

        Args:
            page_count (int): Current page count
            item_count (int): Item count for current page
            url (Optional[str]): URL for current request, optional for final log
        """
        if url:
            logger.debug(f"Fetching page {page_count + 1} from {url}")
        if item_count > 0:
            logger.debug(f"Processed page {page_count} with {item_count} items")

    def _log_pagination_complete(
        self,
        total_items: int,
        page_count: int,
    ) -> None:
        """
        Log completion of pagination.

        Args:
            total_items (int): Total number of items fetched
            page_count (int): Total number of pages
        """
        logger.info(f"Completed pagination: {total_items} items in {page_count} pages")

    def _process_single_page(
        self,
        url: str,
        current_params: Dict[str, Any],
        request_method: str,
        post_data: Optional[Dict[str, Any]],
        data_path: Optional[str],
        pagination_type: str,
        output_mode: Optional[str],
        page_count: int,
        next_page_extractor: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
    ) -> Tuple[bool, str, Dict[str, Any], Optional[List[Dict[str, Any]]], Optional[str], int]:
        """
        Process a single page of API results.

        Args:
            url (str): Current API URL
            current_params (Dict[str, Any]): Current request parameters
            request_method (str): HTTP method to use
            post_data (Optional[Dict[str, Any]]): Data for POST requests
            data_path (Optional[str]): Path to data in response
            pagination_type (str): Type of pagination
            output_mode (Optional[str]): Current file output mode
            page_count (int): Current page counter
            next_page_extractor (Optional[Callable]): Function to extract next page

        Returns:
            Tuple containing:
                bool: Whether there are more pages
                str: Next URL if applicable
                Dict[str, Any]: Updated parameters
                Optional[List[Dict[str, Any]]]: Items from this page
                Optional[str]: Updated output mode
                int: Number of items processed
        """
        # Log beginning of page fetch
        self._log_pagination_progress(page_count, 0, url)

        # Apply throttling if needed
        self._apply_throttling(page_count)

        # Fetch the page
        result = self._fetch_next_page(url, current_params, request_method, post_data)
        if not result:
            return False, url, current_params, None, output_mode, 0

        # Process the results
        items, new_output_mode, item_count = self._process_result_page(result, data_path, output_mode)
        if not items:
            return False, url, current_params, None, output_mode, 0

        # Update pagination for next page
        has_more, next_url, updated_params = self._process_next_page(
            pagination_type, result, current_params, items, next_page_extractor
        )

        # Log page processed
        self._log_pagination_progress(page_count, item_count, url)

        return has_more, next_url, updated_params, items, new_output_mode, item_count

    def fetch_paginated_results(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data_path: Optional[str] = None,
        pagination_type: str = "offset",
        next_page_extractor: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
        request_method: str = "GET",
        post_data: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch all pages of results from the API endpoint.

        Args:
            endpoint (str): API endpoint path (will be appended to base_url)
            params (Optional[Dict[str, Any]]): Query parameters for the request
            data_path (Optional[str]): JSON path to the data array within the response
            pagination_type (str): Type of pagination: "offset", "page", "token", or "cursor"
            next_page_extractor (Optional[Callable]): Function to extract next page URL/token
            request_method (str): HTTP method to use ("GET" or "POST")
            post_data (Optional[Dict[str, Any]]): JSON data to send with POST requests

        Returns:
            Iterator[Dict[str, Any]]: Iterator yielding each result item

        Raises:
            ValidationException: If an invalid pagination type is provided
        """
        # Setup initial pagination state
        url, current_params = self._setup_pagination(endpoint, pagination_type, params)
        current_post_data = post_data.copy() if post_data else {}
        page_count = 0
        total_items = 0
        has_more = True

        # Use file or memory for storing results
        output_mode = WRITE_MODE if self.output_file else None

        # Main pagination loop
        while self._should_continue_pagination(has_more, page_count):
            # Process a single page
            has_more, next_url, current_params, items, output_mode, item_count = self._process_single_page(
                url=url,
                current_params=current_params,
                request_method=request_method,
                post_data=current_post_data,
                data_path=data_path,
                pagination_type=pagination_type,
                output_mode=output_mode,
                page_count=page_count,
                next_page_extractor=next_page_extractor,
            )

            # If no items processed, we're done
            if not items or item_count == 0:
                break

            # In streaming mode, yield items directly
            if not self.output_file:
                for item in items:
                    yield item

            # Update URL if changed
            if next_url:
                url = next_url

            # Update counters
            total_items += item_count
            page_count += 1

        # Log completion
        self._log_pagination_complete(total_items, page_count)

        # If writing to file, read back as iterator
        if self.output_file:
            yield from self.read_jsonl_file(self.output_file)

    def _create_endpoint_fetch_task(
        self, endpoint: str, params: Optional[Dict[str, Any]], data_path: Optional[str], request_method: str
    ) -> Callable[[], List[Dict[str, Any]]]:
        """
        Create a callable task for fetching a single endpoint.

        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters
            data_path (Optional[str]): Path to data
            request_method (str): HTTP method

        Returns:
            Callable[[], List[Dict[str, Any]]]: Task function
        """

        def task() -> List[Dict[str, Any]]:
            results = []
            for item in self.fetch_paginated_results(
                endpoint=endpoint,
                params=params,
                data_path=data_path,
                request_method=request_method,
            ):
                results.append(item)
            return results

        return task

    def _process_concurrent_results(self, futures: List, use_output_file: Optional[str]) -> Iterator[Dict[str, Any]]:
        """
        Process results from concurrent endpoint fetches.

        Args:
            futures (List): List of Future objects
            use_output_file (Optional[str]): Output file path

        Returns:
            Iterator[Dict[str, Any]]: Iterator of results
        """
        file_mode = WRITE_MODE if use_output_file else None

        for future in futures:
            try:
                results = future.result()
                if not results:
                    continue

                if use_output_file:
                    self._write_items_to_file(results, use_output_file, file_mode)
                    # Use append mode for subsequent endpoints
                    file_mode = APPEND_MODE
                else:
                    for item in results:
                        yield item
            except Exception as e:
                logger.error(f"Error in concurrent fetch: {str(e)}")

    def fetch_all_concurrent(
        self,
        endpoints: List[str],
        params: Optional[Dict[str, Any]] = None,
        data_path: Optional[str] = None,
        request_method: str = "GET",
        output_file: Optional[str] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch multiple endpoints concurrently and combine results.

        Args:
            endpoints (List[str]): List of API endpoint paths
            params (Optional[Dict[str, Any]]): Query parameters for the requests
            data_path (Optional[str]): JSON path to the data array within the response
            request_method (str): HTTP method to use ("GET" or "POST")
            output_file (Optional[str]): Override the instance output_file

        Returns:
            Iterator[Dict[str, Any]]: Iterator yielding each result item
        """
        use_output_file = output_file or self.output_file

        # Create tasks for each endpoint
        tasks = [
            self._create_endpoint_fetch_task(endpoint, params, data_path, request_method) for endpoint in endpoints
        ]

        # Execute tasks concurrently
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            # Start all fetch tasks
            futures = [executor.submit(task) for task in tasks]

            # Process results as they complete
            yield from self._process_concurrent_results(futures, use_output_file)

        # If we're writing to a file, read it back as an iterator
        if use_output_file:
            yield from self.read_jsonl_file(use_output_file)

    def _extract_next_token(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract the next token from a response.

        This method tries several common patterns for next token references.

        Args:
            response (Dict[str, Any]): The API response

        Returns:
            Optional[str]: The next token or None if not found
        """
        # Try common patterns for next token
        token_paths = [
            ["nextToken"],
            ["next_token"],
            ["pagination", "nextToken"],
            ["meta", "next_token"],
            ["paging", "next"],
            ["links", "next"],
        ]

        return self._extract_value_from_paths(response, token_paths)

    def _extract_cursor(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract the cursor from a response.

        This method tries several common patterns for cursor references.

        Args:
            response (Dict[str, Any]): The API response

        Returns:
            Optional[str]: The cursor or None if not found
        """
        # Try common patterns for cursor
        cursor_paths = [
            ["cursor"],
            ["page", "cursor"],
            ["meta", "cursor"],
            ["paging", "cursors", "after"],
            ["pagination", "cursor"],
        ]

        return self._extract_value_from_paths(response, cursor_paths)

    def _extract_value_from_path(self, data: Dict[str, Any], path: List[str]) -> Optional[str]:
        """
        Extract a value from a nested dictionary using a single path.

        Args:
            data (Dict[str, Any]): The dictionary to search
            path (List[str]): Path to the value

        Returns:
            Optional[str]: The found value or None
        """
        value = data
        try:
            for key in path:
                if key in value:
                    value = value[key]
                else:
                    return None
            if value and isinstance(value, (str, int)):
                return str(value)
        except (KeyError, TypeError):
            pass
        return None

    def _extract_value_from_paths(self, data: Dict[str, Any], paths: List[List[str]]) -> Optional[str]:
        """
        Extract a value from a nested dictionary using multiple possible paths.

        Args:
            data (Dict[str, Any]): The dictionary to search
            paths (List[List[str]]): List of possible path lists to the value

        Returns:
            Optional[str]: The found value or None
        """
        for path in paths:
            value = self._extract_value_from_path(data, path)
            if value:
                return value
        return None

    @staticmethod
    def _parse_jsonl_line(line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single JSONL line.

        Args:
            line (str): Line to parse

        Returns:
            Optional[Dict[str, Any]]: Parsed JSON or None on error
        """
        line = line.strip()
        if not line:  # Skip empty lines
            return None

        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON line: {str(e)}")
            logger.debug(f"Problematic line: {line}")
            return None

    @staticmethod
    def read_jsonl_file(file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Read a JSONL file and yield each line as a parsed JSON object.

        Args:
            file_path (str): Path to the JSONL file

        Returns:
            Iterator[Dict[str, Any]]: Iterator of parsed JSON objects
        """
        try:
            with open(file_path, "r") as f:
                for line in f:
                    parsed = ApiPaginator._parse_jsonl_line(line)
                    if parsed:
                        yield parsed
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except IOError as e:
            logger.error(f"IO error reading file {file_path}: {str(e)}")

    def get_output_file_path(self) -> Optional[str]:
        """
        Get the path to the output file.

        Returns:
            Optional[str]: Path to the output file or None if not set
        """
        return self.output_file

    def clear_output_file(self) -> None:
        """
        Clear the output file if it exists.
        """
        if not self.output_file:
            return

        if os.path.exists(self.output_file):
            try:
                os.remove(self.output_file)
                logger.debug(f"Cleared output file: {self.output_file}")
            except OSError as e:
                logger.error(f"Error clearing output file {self.output_file}: {str(e)}")
