#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the ApiPaginator class.
"""

import json
import os
import tempfile
from typing import Dict, List, Any
from unittest.mock import patch

import pytest
import responses

from regscale.integrations.api_paginator import ApiPaginator, HTTPS_PREFIX


class TestApiPaginator:
    """Test cases for ApiPaginator class."""

    @pytest.fixture
    def base_url(self) -> str:
        """Return a base URL for testing."""
        return "https://api.example.com"

    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        """Return authentication headers for testing."""
        return {"Authorization": "Bearer test-token"}

    @pytest.fixture
    def temp_output_file(self, tmp_path) -> str:
        """Create a temporary output file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
            tmp_path = tmp.name
        yield tmp_path
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    @pytest.fixture
    def mock_response_data(self) -> List[Dict[str, Any]]:
        """Return mock API response data for testing."""
        return [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
        ]

    @pytest.fixture
    def paginator(self, base_url, auth_headers) -> ApiPaginator:
        """Return an ApiPaginator instance for testing."""
        return ApiPaginator(
            base_url=base_url,
            auth_headers=auth_headers,
            page_size=2,
        )

    @pytest.fixture
    def file_paginator(self, base_url, auth_headers, temp_output_file) -> ApiPaginator:
        """Return an ApiPaginator instance with file output for testing."""
        return ApiPaginator(
            base_url=base_url,
            auth_headers=auth_headers,
            page_size=2,
            output_file=temp_output_file,
        )

    def test_init(self, base_url, auth_headers, temp_output_file):
        """Test initialization with default and custom parameters."""
        # Test with minimal parameters
        paginator = ApiPaginator(base_url=base_url, auth_headers={})
        assert paginator.base_url == base_url
        assert paginator.auth_headers == {}
        assert paginator.page_size == 100
        assert paginator.throttle_rate is None
        assert paginator.timeout == 30
        assert paginator.ssl_verify is True
        assert paginator.output_file is None

        # Test with custom parameters
        paginator = ApiPaginator(
            base_url=base_url,
            auth_headers=auth_headers,
            page_size=50,
            throttle_rate=0.5,
            timeout=10,
            ssl_verify=False,
            output_file=temp_output_file,
        )
        assert paginator.base_url == base_url
        assert paginator.auth_headers == auth_headers
        assert paginator.page_size == 50
        assert paginator.throttle_rate == abs(0.5)
        assert paginator.timeout == 10
        assert paginator.ssl_verify is False
        assert paginator.output_file == temp_output_file

    def test_create_session(self, paginator):
        """Test creation of requests session."""
        session = paginator.session

        # Verify session has the correct headers
        assert paginator.auth_headers.items() <= session.headers.items()

        # Verify HTTPS adapter is mounted
        assert HTTPS_PREFIX in session.adapters

        # For ssl_verify=True, both HTTP and HTTPS adapters are present
        # We no longer check for HTTP adapter absence
        assert session.adapters.get(HTTPS_PREFIX) is not None

    @responses.activate
    def test_offset_pagination(self, paginator, base_url, mock_response_data):
        """Test offset-based pagination."""
        # First page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[:2],
            status=200,
        )

        # Second page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[2:],
            status=200,
        )

        # Third page (empty, to end pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=[],
            status=200,
        )

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="offset",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

        # Verify that offset was incremented correctly
        request_params = [r.request.params for r in responses.calls]
        assert request_params[0]["offset"] == "0"
        assert request_params[0]["limit"] == "2"
        assert request_params[1]["offset"] == "2"
        assert request_params[1]["limit"] == "2"
        # We don't need to check the third request, as it might not be made
        # if the API returns an empty list for the second page

    @responses.activate
    def test_page_pagination(self, paginator, base_url, mock_response_data):
        """Test page-based pagination."""
        # First page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[:2],
            status=200,
        )

        # Second page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[2:],
            status=200,
        )

        # Third page (empty, to end pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=[],
            status=200,
        )

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="page",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

        # Verify that page was incremented correctly
        request_params = [r.request.params for r in responses.calls]
        assert request_params[0]["page"] == "1"
        assert request_params[0]["per_page"] == "2"
        assert request_params[1]["page"] == "2"
        assert request_params[1]["per_page"] == "2"
        # We don't need to check the third request as it might not be made
        # if the API returns an empty list for the second page

    @responses.activate
    def test_token_pagination(self, paginator, base_url, mock_response_data):
        """Test token-based pagination."""
        # First page with next token
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={"data": mock_response_data[:2], "nextToken": "token123"},
            status=200,
        )

        # Second page with no next token (end of pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={"data": mock_response_data[2:], "nextToken": None},
            status=200,
        )

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="token",
                data_path="data",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

        # Verify token was passed in second request
        request_params = [r.request.params for r in responses.calls]
        assert "next_token" not in request_params[0]
        assert request_params[1]["next_token"] == "token123"

    @responses.activate
    def test_cursor_pagination(self, paginator, base_url, mock_response_data):
        """Test cursor-based pagination."""
        # First page with next cursor
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={
                "data": mock_response_data[:2],
                "paging": {"cursors": {"after": "cursor123"}},
            },
            status=200,
        )

        # Second page with no next cursor (end of pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={"data": mock_response_data[2:], "paging": {"cursors": {}}},
            status=200,
        )

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="cursor",
                data_path="data",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

        # Verify cursor was passed in second request
        request_params = [r.request.params for r in responses.calls]
        assert "cursor" not in request_params[0]
        assert request_params[1]["cursor"] == "cursor123"

    @responses.activate
    def test_custom_pagination(self, paginator, base_url, mock_response_data):
        """Test custom pagination."""
        # Setup a custom pagination scenario
        # First page with custom next page info
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={
                "items": mock_response_data[:2],
                "metadata": {"has_more": True, "next_page": "/items?page=2"},
            },
            status=200,
        )

        # Second page with no more pages
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={
                "items": mock_response_data[2:],
                "metadata": {"has_more": False},
            },
            status=200,
        )

        # Define custom next page extractor
        def next_page_extractor(result):
            next_url = result.get("metadata", {}).get("next_page")
            return next_url

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="custom",
                data_path="items",
                next_page_extractor=next_page_extractor,
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

    @responses.activate
    def test_file_output(self, file_paginator, base_url, mock_response_data, temp_output_file):
        """Test writing results to a file."""
        # Add mock responses
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data,
            status=200,
        )

        # Second page (empty, to end pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=[],
            status=200,
        )

        # Fetch results
        results = list(
            file_paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="offset",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

        # Verify file content
        with open(temp_output_file, "r") as f:
            file_data = [json.loads(line) for line in f]
            assert file_data == mock_response_data

    @responses.activate
    def test_max_pages(self, paginator, base_url, mock_response_data):
        """Test max_pages parameter."""
        # First page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[:2],
            status=200,
        )

        # Second page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[2:],
            status=200,
        )

        # Set max_pages directly on the paginator
        paginator.max_pages = 1

        # We should only get the first page due to max_pages=1
        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="offset",
            )
        )

        assert len(results) == 2
        assert results == mock_response_data[:2]
        assert len(responses.calls) == 1

    @responses.activate
    def test_throttling(self, paginator, base_url, mock_response_data):
        """Test request throttling."""
        # Set throttle_rate
        paginator.throttle_rate = 0.01  # Small value for testing

        # First page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[:2],
            status=200,
        )

        # Second page
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=mock_response_data[2:],
            status=200,
        )

        # Third page (empty, to end pagination)
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json=[],
            status=200,
        )

        with patch("time.sleep") as mock_sleep:
            _ = list(
                paginator.fetch_paginated_results(
                    endpoint="items",
                    pagination_type="offset",
                )
            )

            # Throttling only occurs after the first request
            # It's only called once since we have two page requests
            assert mock_sleep.call_count == 1

    @responses.activate
    def test_error_handling(self, paginator, base_url):
        """Test error handling in requests."""
        # Response with error status
        responses.add(
            responses.GET,
            f"{base_url}/items",
            status=500,
            json={"error": "Server error"},
        )

        # Log error should be called
        with patch("logging.Logger.error") as mock_error:
            with patch("logging.Logger.debug") as mock_debug:  # Mock debug too
                # The paginator will handle the error internally and return None
                # We don't need to catch RetryError as it's already handled in _make_request
                results = list(
                    paginator.fetch_paginated_results(
                        endpoint="items",
                        pagination_type="offset",
                    )
                )

                # Verify the logs were called
                assert mock_error.called
                assert mock_debug.called
                # Verify that we attempted to make the call
                assert len(responses.calls) > 0
                # Result should be empty since error occurred
                assert len(results) == 0

    @responses.activate
    def test_data_path_navigation(self, paginator, base_url, mock_response_data):
        """Test navigating to data using a data path."""
        # API returns data in a nested structure
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={"response": {"items": mock_response_data}},
            status=200,
        )

        # Second call with empty data to end pagination
        responses.add(
            responses.GET,
            f"{base_url}/items",
            json={"response": {"items": []}},
            status=200,
        )

        results = list(
            paginator.fetch_paginated_results(
                endpoint="items",
                pagination_type="offset",
                data_path="response.items",
            )
        )

        assert len(results) == 3
        assert results == mock_response_data

    @responses.activate
    def test_fetch_all_concurrent(self, paginator, base_url, mock_response_data):
        """Test fetching multiple endpoints concurrently."""
        # Mock responses for endpoint1
        responses.add(
            responses.GET,
            f"{base_url}/endpoint1",
            json=mock_response_data[:2],
            status=200,
        )
        responses.add(
            responses.GET,
            f"{base_url}/endpoint1",
            json=[],
            status=200,
        )

        # Mock responses for endpoint2
        responses.add(
            responses.GET,
            f"{base_url}/endpoint2",
            json=mock_response_data[2:],
            status=200,
        )
        responses.add(
            responses.GET,
            f"{base_url}/endpoint2",
            json=[],
            status=200,
        )

        results = list(
            paginator.fetch_all_concurrent(
                endpoints=["endpoint1", "endpoint2"],
            )
        )

        assert len(results) == 3
        assert sorted(results, key=lambda x: x["id"]) == mock_response_data

    def test_read_jsonl_file(self, file_paginator, temp_output_file, mock_response_data):
        """Test reading from a JSONL file."""
        # Write test data to the file
        with open(temp_output_file, "w") as f:
            for item in mock_response_data:
                f.write(json.dumps(item) + "\n")

        # Use the static method directly
        results = list(ApiPaginator.read_jsonl_file(temp_output_file))
        assert results == mock_response_data

    def test_clear_output_file(self, file_paginator, temp_output_file):
        """Test clearing the output file."""
        # Write something to the file
        with open(temp_output_file, "w") as f:
            f.write("test data\n")

        # File should have content
        assert os.path.getsize(temp_output_file) > 0

        # Clear the file
        file_paginator.clear_output_file()

        # File should be deleted
        assert not os.path.exists(temp_output_file)

    def test_extract_value_from_paths(self, paginator):
        """Test extracting values from a nested structure."""
        # Test nested structure
        data = {
            "user": {
                "profile": {
                    "name": "Test User",
                    "email": "test@example.com",
                },
                "settings": {
                    "notifications": True,
                },
            },
            "metadata": {
                "created_at": "2023-01-01",
            },
        }

        # Create path lists for testing
        name_paths = [["user", "profile", "name"]]
        notifications_paths = [["user", "settings", "notifications"]]
        date_paths = [["metadata", "created_at"]]
        missing_paths = [["user", "age"]]
        multiple_paths = [["missing"], ["user", "profile", "name"]]

        # Test valid paths
        assert paginator._extract_value_from_paths(data, name_paths) == "Test User"
        assert paginator._extract_value_from_paths(data, notifications_paths) == "True"
        assert paginator._extract_value_from_paths(data, date_paths) == "2023-01-01"

        # Test non-existent paths
        assert paginator._extract_value_from_paths(data, missing_paths) is None

        # Test multiple paths (should find the first valid one)
        assert paginator._extract_value_from_paths(data, multiple_paths) == "Test User"


if __name__ == "__main__":
    pytest.main()
