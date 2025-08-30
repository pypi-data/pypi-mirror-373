#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Api class"""
import os
from unittest.mock import MagicMock, patch

import pytest

from regscale.core.app.api import Api, normalize_url
from regscale.core.app.application import Application


@pytest.fixture
def mock_config():
    """Fixture for mocking config"""
    return {
        "token": "test-token",
        "domain": "https://api.example.com",
        "maxThreads": 10,
        "ssl_verify": True,
        "timeout": 10,
    }


@pytest.fixture
def api(mock_config):
    """Fixture for creating an Api instance with mocked config"""
    with patch("regscale.core.app.application.Application") as mock_app:
        mock_app.return_value.config = mock_config
        api = Api()
        api.session = MagicMock()
        return api


def test_handle_headers_with_no_merge(api):
    """Test _handle_headers when merge_headers is False"""
    custom_headers = {"Custom-Header": "value"}
    result = api._handle_headers(custom_headers, merge_headers=False)
    assert result == custom_headers


def test_handle_headers_with_merge(api):
    """Test _handle_headers when merge_headers is True"""
    custom_headers = {"Custom-Header": "value"}
    result = api._handle_headers(custom_headers, merge_headers=True)

    assert result["Custom-Header"] == "value"
    assert result["accept"] == api.accept
    assert result["Content-Type"] == api.content_type
    assert result["Authorization"] == "test-token"


def test_handle_headers_with_no_headers(api):
    """Test _handle_headers when headers is None"""
    # When merge_headers is False, should return empty dict for None headers
    result = api._handle_headers(None, merge_headers=False)
    assert result["accept"] == api.accept
    assert result["Content-Type"] == api.content_type
    assert result["Authorization"] == "test-token"

    # When merge_headers is True, should return default headers
    result = api._handle_headers(None, merge_headers=True)
    assert result["accept"] == api.accept
    assert result["Content-Type"] == api.content_type
    assert result["Authorization"] == "test-token"


def test_handle_headers_with_empty_headers(api):
    """Test _handle_headers when headers is an empty dict"""
    result = api._handle_headers({}, merge_headers=True)

    assert len(result) == 3
    assert result["accept"] == api.accept
    assert result["Content-Type"] == api.content_type
    assert result["Authorization"] == "test-token"

    # Test with merge_headers=False
    result = api._handle_headers({}, merge_headers=False)
    assert result == {}


def test_get_request_success(api):
    """Test successful GET request"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data": "test"}'
    api.session.get.return_value = mock_response

    response = api.get("https://api.example.com/test")

    assert response.status_code == 200
    assert response.text == '{"data": "test"}'
    api.session.get.assert_called_once()


def test_post_request_success(api):
    """Test successful POST request"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data": "created"}'
    api.session.post.return_value = mock_response

    json_data = {"key": "value"}
    response = api.post("https://api.example.com/test", json=json_data)

    assert response.status_code == 200
    assert response.text == '{"data": "created"}'
    api.session.post.assert_called_once()


def test_put_request_success(api):
    """Test successful PUT request"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data": "updated"}'
    api.session.put.return_value = mock_response

    json_data = {"key": "value"}
    response = api.put("https://api.example.com/test", json=json_data)

    assert response.status_code == 200
    assert response.text == '{"data": "updated"}'
    api.session.put.assert_called_once()


def test_delete_request_success(api):
    """Test successful DELETE request"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data": "deleted"}'
    api.session.delete.return_value = mock_response

    response = api.delete("https://api.example.com/test")

    assert response.status_code == 200
    assert response.text == '{"data": "deleted"}'
    api.session.delete.assert_called_once()


def test_request_with_401_retry(api):
    """Test request handling 401 unauthorized with retry"""
    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.text = '{"data": "success"}'

    api.session.get.side_effect = [mock_response_401, mock_response_200]

    with patch.object(api, "_handle_401", return_value=True):
        response = api.get("https://api.example.com/test")

        assert response.status_code == 200
        assert response.text == '{"data": "success"}'
        assert api.session.get.call_count == 2


def test_normalize_url():
    """Test URL normalization"""
    test_cases = [
        ("http://example.com//api//v1/", "http://example.com/api/v1"),
        ("example.com/api/v1", "http://example.com/api/v1"),
        ("https://example.com/api//v1", "https://example.com/api/v1"),
        ("http://example.com/api/v1/", "http://example.com/api/v1"),
    ]

    for input_url, expected_url in test_cases:
        assert normalize_url(input_url) == expected_url


def test_graph_query_success(api):
    """Test successful GraphQL query"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"vulnerabilities": {"items": [{"id": 1}], "pageInfo": {"hasNextPage": False}}}
    }

    api.session.post.return_value = mock_response
    query = """
    query {
        vulnerabilities {
            items {
                id
            }
        }
    }
    """
    result = api.graph(query)

    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"]["items"], list)
    assert result["vulnerabilities"]["items"][0]["id"] == 1
    api.session.post.assert_called_once()


def test_ssl_verify_false_envar():
    """Test that SSL verification setting is passed to the session via envar"""
    with patch.dict(os.environ, {"sslVerify": "false"}):
        assert os.getenv("sslVerify") == "false"
        api = Api()
        assert api.session.verify is False


def test_ssl_verify_true_envar():
    """Test that SSL verification setting is passed to the session via envar"""
    with patch.dict(os.environ, {"sslVerify": "true"}):
        assert os.getenv("sslVerify") == "true"
        api = Api()
        assert api.verify is True
        assert api.session.verify is True


def test_ssl_verify_false_config():
    """Test that SSL verification setting is passed to the session via init.yaml"""
    app = Application(config={"sslVerify": False})
    app.config_file = "test_ssl_verify_false_config.yaml"
    app.save_config(app.config)
    assert app.config["sslVerify"] is False
    api = Api()
    assert api.verify is False
    assert api.session.verify is False
    # os.remove(app.config_file)


def test_ssl_verify_true_config():
    """Test that SSL verification setting is passed to the session init.yaml"""
    app = Application(config={"sslVerify": True})
    assert app.config["sslVerify"] is True
    api = Api()
    assert api.session.verify is True
