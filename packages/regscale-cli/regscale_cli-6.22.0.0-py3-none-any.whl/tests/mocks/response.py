"""Create mocked requests.Response objects."""

from unittest.mock import Mock

import requests


def create_mock_response(
    status_code=200,
    json_data=None,
    text_data=None,
    headers=None,
    ok=True,
):
    """
    Generate a custom requests.Response object using unittest.mock.

    :status_code (int, optional): The HTTP status code for the response.
    :json_data (dict, optional): The JSON data to be returned by the response's json() method.
    :text_data (str, optional): The text data to be returned by the response's text attribute.
    :headers (dict, optional): The headers for the response.
    :ok (bool, optional): The response.ok value.

    :returns Mock: A unittest.mock.Mock instance with the specified attributes and behavior.
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data
    mock_response.text = text_data
    mock_response.headers = headers or {}
    mock_response.ok = ok
    return mock_response
