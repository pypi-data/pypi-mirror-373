import random
from typing import Optional
from unittest.mock import patch, MagicMock

import pytest

from regscale.models.regscale_models.regscale_model import RegScaleModel


@pytest.fixture
def mock_api_handler():
    """
    Fixture to mock the API handler for testing.

    :yield: A mocked API handler
    """
    with patch(
        "regscale.models.regscale_models.regscale_model.RegScaleModel._api_handler",
        spec=RegScaleModel._api_handler,  # noqa
    ) as mock:

        def mock_post(endpoint: str, data: dict) -> MagicMock:
            """
            Mock the post method of the API handler.

            :param str endpoint:
            :param dict data:
            :rtype: MagicMock
            :return: A mocked response object
            """
            mock_response = MagicMock()
            mock_response.ok = True
            response_data = data.copy()
            response_data["id"] = random.randint(1, 1000)
            mock_response.json.return_value = response_data
            return mock_response

        def mock_put(endpoint: str, data: dict) -> MagicMock:
            """
            Mock the put method of the API handler.

            :param str endpoint:
            :param dict data:
            :rtype: MagicMock
            :return: A mocked response object
            """

            mock_response = MagicMock()
            mock_response.ok = True
            response_data = data.copy()
            mock_response.json.return_value = response_data
            return mock_response

        def mock_graph(query: str, variables: Optional[dict] = None) -> MagicMock:
            """
            Mock the graph method of the API handler.

            :param str query:
            :param Optional[dict] variables:
            :rtype: MagicMock
            :return: A mocked response object
            """
            # Extract the model name from the query
            model_name = query.split("{", 1)[1].split("(", 1)[0].strip()

            # Create a mock response object
            mock_response = MagicMock()
            mock_response.ok = True

            # Set up the response data structure
            setattr(
                mock_response,
                model_name,
                {
                    "items": [],
                    "pageInfo": {"hasNextPage": False},
                    "totalCount": 0,
                },
            )

            return mock_response

        mock.post.side_effect = mock_post
        mock.put.side_effect = mock_put
        mock.graph.side_effect = mock_graph
        mock.regscale_version = "5.66.0"
        yield mock
