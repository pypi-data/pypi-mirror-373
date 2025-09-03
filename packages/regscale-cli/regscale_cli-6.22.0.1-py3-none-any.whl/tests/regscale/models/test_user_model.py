#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the User model"""

import unittest
from unittest.mock import patch, MagicMock

from regscale.models.regscale_models.user import User


class TestUser(unittest.TestCase):
    """Test cases for the User model"""

    def setUp(self):
        """Set up test cases"""
        self.test_user_data = {
            "userName": "testuser",
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "homePageUrl": "/custom-dashboard",
        }

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_below_min_version(self, mock_api_handler):
        """Test homePageUrl is None when version < 6.14.0.0"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.11.0.0"
        mock_api_handler.return_value = mock_handler

        # Create user instance
        user = User(**self.test_user_data)

        # Verify homePageUrl is None for version < 6.14.0.0
        self.assertIsNone(user.homePageUrl)
        # Verify the underlying field still has the value
        self.assertEqual(user.homePageUrl_, "/custom-dashboard")

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_at_min_version(self, mock_api_handler):
        """Test homePageUrl is accessible when version = 6.14.0.0"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.14.0.0"
        mock_api_handler.return_value = mock_handler

        # Create user instance
        user = User(**self.test_user_data)

        # Verify homePageUrl is accessible for version = 6.14.0.0
        self.assertEqual(user.homePageUrl, "/custom-dashboard")

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_above_min_version(self, mock_api_handler):
        """Test homePageUrl is accessible when version > 6.14.0.0"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.14.0.1"
        mock_api_handler.return_value = mock_handler

        # Create user instance
        user = User(**self.test_user_data)

        # Verify homePageUrl is accessible for version > 6.14.0.0
        self.assertEqual(user.homePageUrl, "/custom-dashboard")

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_setter(self, mock_api_handler):
        """Test homePageUrl setter works correctly"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.14.0.1"
        mock_api_handler.return_value = mock_handler

        # Create user instance
        user = User(**self.test_user_data)

        # Test setting a new value
        new_url = "/new-dashboard"
        user.homePageUrl = new_url

        # Verify both the property and underlying field are updated
        self.assertEqual(user.homePageUrl, new_url)
        self.assertEqual(user.homePageUrl_, new_url)

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_default_value(self, mock_api_handler):
        """Test homePageUrl default value behavior"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.14.0.0"
        mock_api_handler.return_value = mock_handler

        # Create user instance without specifying homePageUrl
        user = User(userName="testuser", email="test@example.com")

        # Verify default value is set correctly
        self.assertEqual(user.homePageUrl, "/workbench")
        self.assertEqual(user.homePageUrl_, "/workbench")

    @patch("regscale.models.regscale_models.user.User._get_api_handler")
    def test_homepage_url_none_value(self, mock_api_handler):
        """Test homePageUrl with None value"""
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.regscale_version = "6.14.0.0"
        mock_api_handler.return_value = mock_handler

        # Create test data with None homePageUrl
        test_data = self.test_user_data.copy()
        test_data["homePageUrl"] = None
        user = User(**test_data)

        # Verify None value is handled correctly
        self.assertIsNone(user.homePageUrl)
        self.assertIsNone(user.homePageUrl_)


if __name__ == "__main__":
    unittest.main()
