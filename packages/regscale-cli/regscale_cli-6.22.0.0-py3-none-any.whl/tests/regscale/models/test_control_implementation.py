import unittest
from unittest.mock import MagicMock, patch

from regscale.models import ControlImplementation


class TestControlImplementation(unittest.TestCase):
    @patch("regscale.models.regscale_models.control_implementation.ControlImplementation._get_api_handler().get")
    def test_get_control_map_by_plan_lower_case_keys(self, mock_get):
        # Create a mock response object with 'ok' attribute and 'json' method
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {"control": {"controlId": "CA-1"}, "id": 1},
            {"control": {"controlId": "AC-6"}, "id": 2},
        ]

        mock_get.return_value = mock_response

        # Expected result should have lower case control IDs as keys
        expected_result = {"ca-1": 1, "ac-6": 2}

        # Call the method under test
        result = ControlImplementation.get_control_label_map_by_plan(plan_id=123)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)
