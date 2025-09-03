"""
Test the Application class used by the RegScale CLI.
"""

import os
from unittest.mock import patch, MagicMock
import pytest

from requests import Response

from regscale.core.app.application import Application


class TestApplication:
    test_config_file = "test_application_config.yaml"
    os.environ["REGSCALE_CONFIG_FILE"] = test_config_file
    app = Application()
    app.config_file = test_config_file
    test_domain = "https://example.com"
    test_token = "Bearer test_token"

    @pytest.fixture(autouse=True)
    def save_config(self):
        original_conf = self.app.config
        yield
        self.app.config = original_conf
        self.app.save_config(original_conf)

    def teardown_method(self, method):
        """
        Remove the test config file after each test
        """
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)

    def test_init(self):
        assert isinstance(self.app, Application)
        assert isinstance(self.app, Application)
        assert self.app.config != {}
        assert self.app.local_config is True
        assert self.app.running_in_airflow is False

    def test_singleton(self):
        test_config = {"key": "value"}
        app2 = Application()
        assert self.app == app2
        app3 = Application(config=test_config)
        assert test_config["key"] == app3["key"]
        assert app3 != self.app
        assert app3 != app2

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_success(self, mock_get, mock_parse_user_id):
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = '{"key": "value"}'
        mock_get.return_value = mock_response
        with patch.object(self.app, "_decrypt_config", return_value='{"key": "value"}'):
            config = self.app._fetch_config_from_regscale(config=self.app.config)
            assert "domain" in config
            assert config["userId"] == "test_user_id"
            assert config["key"] == "value"

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_success_with_envars(self, mock_get, mock_parse_user_id):
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = '{"key": "value"}'
        mock_get.return_value = mock_response
        envars = os.environ.copy()
        envars["REGSCALE_DOMAIN"] = self.test_domain
        envars["REGSCALE_TOKEN"] = self.test_token
        with patch.dict(os.environ, envars, clear=True):
            with patch.object(self.app, "_decrypt_config", return_value='{"key": "value"}'):
                config = self.app._fetch_config_from_regscale(config={})
                assert config["domain"] == self.test_domain
                assert config["token"] == self.test_token
                assert config["userId"] == "test_user_id"
                assert config["key"] == "value"

    @patch("requests.get")
    def test_fetch_config_from_regscale_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = "Not found."
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        envars = os.environ.copy()
        envars["REGSCALE_DOMAIN"] = self.test_domain
        envars["REGSCALE_TOKEN"] = self.test_token
        with patch.dict(os.environ, envars, clear=True):
            with patch.object(self.app.logger, "error") as mock_logger_error:
                empty_config = self.app._fetch_config_from_regscale()
                assert empty_config == {}
                mock_logger_error.assert_called()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_unencrypted_dict(self, mock_get, mock_parse_user_id):
        """Test the case where the response is already a dictionary (not encrypted)"""
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value", "userId": "test_user_id"}
        mock_get.return_value = mock_response
        config = self.app._fetch_config_from_regscale(config=self.app.config)
        assert "domain" in config
        assert config["userId"] == "test_user_id"
        assert config["key"] == "value"

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_no_cli_config(self, mock_get, mock_parse_user_id):
        """Test error handling when the cliConfig field is missing from the response"""
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = ""
        mock_get.return_value = mock_response
        with patch.object(self.app.logger, "warning") as mock_logger_warning:
            config = self.app._fetch_config_from_regscale(config={})
            mock_logger_warning.assert_called_once()
            assert config == {}

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_with_existing_user_id(self, mock_get, mock_parse_user_id):
        """Test that existing userId in response is preserved"""
        mock_response = MagicMock()
        mock_response.json.return_value = '{"key": "value", "userId": "existing_user"}'
        mock_get.return_value = mock_response

        with patch.object(self.app, "_decrypt_config", return_value='{"key": "value", "userId": "existing_user"}'):
            config = self.app._fetch_config_from_regscale(config=self.app.config)
            assert config["userId"] == "existing_user"
            # parse_user_id_from_jwt should not be called since userId already exists
            mock_parse_user_id.assert_not_called()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_empty_response(self, mock_get, mock_parse_user_id):
        """Test handling of empty response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        with patch.object(self.app.logger, "warning") as mock_logger_warning:
            config = self.app._fetch_config_from_regscale(config=self.app.config)
            assert config == {}
            mock_logger_warning.assert_called_once()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_no_token(self, mock_get, mock_parse_user_id):
        """Test handling when no token is provided"""
        envars = os.environ.copy()
        envars.pop("REGSCALE_TOKEN", None)
        envars.pop("REGSCALE_DOMAIN", None)

        with patch.dict(os.environ, envars, clear=True):
            config = self.app._fetch_config_from_regscale(config={})
            assert config == {}
            mock_get.assert_not_called()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_no_domain(self, mock_get, mock_parse_user_id):
        """Test handling when no domain is provided"""
        envars = os.environ.copy()
        envars["REGSCALE_TOKEN"] = self.test_token
        envars.pop("REGSCALE_DOMAIN", None)

        with patch.dict(os.environ, envars, clear=True):
            with patch.object(self.app, "retrieve_domain", return_value="https://default.com"):
                _ = self.app._fetch_config_from_regscale(config={})
                # Should still attempt to make the request with default domain
                mock_get.assert_called_once()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_request_exception(self, mock_get, mock_parse_user_id):
        """Test handling of request exceptions"""
        mock_get.side_effect = Exception("Network error")

        with patch.object(self.app.logger, "error") as mock_logger_error:
            config = self.app._fetch_config_from_regscale(config=self.app.config)
            assert config == {}
            mock_logger_error.assert_called_once()

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_correct_endpoint(self, mock_get, mock_parse_user_id):
        """Test that the correct API endpoint is called"""
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = {"cliConfig": '{"key": "value"}'}
        mock_get.return_value = mock_response

        with patch.object(self.app, "_decrypt_config", return_value='{"key": "value"}'):
            self.app._fetch_config_from_regscale(config=self.app.config)

            # Verify the correct endpoint was called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "/api/tenants/getDetailedCliConfig" in call_args[1]["url"]

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_headers_verification(self, mock_get, mock_parse_user_id):
        """Test that the correct headers are sent with the request"""
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = {"cliConfig": '{"key": "value"}'}
        mock_get.return_value = mock_response

        with patch.object(self.app, "_decrypt_config", return_value='{"key": "value"}'):
            self.app._fetch_config_from_regscale(config=self.app.config)

            # Verify the correct headers were sent
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"
            assert headers["Authorization"] == self.app.config.get("token")

    def test_fetch_config_from_regscale_json_decode_error(self):
        """Test handling of JSON decode errors in decrypted config"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"cliConfig": "encrypted_data"}

        with patch("requests.get", return_value=mock_response):
            with patch.object(self.app, "_decrypt_config", return_value="invalid json"):
                with patch.object(self.app.logger, "error") as mock_logger_error:
                    config = self.app._fetch_config_from_regscale(config=self.app.config)
                    assert config == {}
                    mock_logger_error.assert_called_once()

    def test_decrypt_config(self):
        """Test the _decrypt_config method with a mock encrypted string"""
        # Mock the cryptography imports
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.side_effect = [
                            b"iv_data_cipher_text",  # First call for combined data
                            b"key_data",  # Second call for token
                        ]
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        mock_decryptor.update.return_value = b'{"key": "value"}'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config(
                            "encrypted_string", os.getenv("REGSCALE_TOKEN", self.app.config["token"])
                        )

                        # Verify the result
                        assert result == '{"key": "value"}'

                        # Verify the mocks were called correctly
                        mock_b64decode.assert_called()
                        mock_sha256.assert_called_once()
                        mock_cipher.assert_called_once()

    def test_decrypt_config_with_trailing_characters(self):
        """Test the _decrypt_config method handles trailing control characters"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.side_effect = [
                            b"iv_data_cipher_text",  # First call for combined data
                            b"key_data",  # Second call for token
                        ]
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Simulate decrypted data with trailing control characters
                        mock_decryptor.update.return_value = b'{"key": "value"}\x00\x08\x07'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config("encrypted_string", "Bearer test_token")

                        # Verify the result is cleaned
                        assert result == '{"key": "value"}'

    def test_decrypt_config_invalid_base64(self):
        """Test _decrypt_config with invalid base64 input"""
        with patch("base64.b64decode", side_effect=Exception("Invalid base64")):
            with patch.object(self.app.logger, "error") as mock_logger_error:
                result = self.app._decrypt_config("invalid_base64", "Bearer test_token")
                # Should raise an exception that gets caught by the calling method
                assert result is None or mock_logger_error.called
                assert mock_logger_error.call_count == 1

    def test_decrypt_config_short_data(self):
        """Test _decrypt_config with data too short for IV extraction"""
        with patch("base64.b64decode", return_value=b"short"):
            with patch.object(self.app.logger, "error") as mock_logger_error:
                result = self.app._decrypt_config("short_data", "Bearer test_token")
                # Should handle the short data gracefully
                assert result is None or mock_logger_error.called

    def test_decrypt_config_decryption_failure(self):
        """Test _decrypt_config when decryption fails"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_cipher.side_effect = Exception("Decryption failed")

                        with patch.object(self.app.logger, "error") as mock_logger_error:
                            result = self.app._decrypt_config("encrypted_string", "Bearer test_token")
                            # Should handle decryption failure gracefully
                            assert result is None or mock_logger_error.called
                            assert mock_logger_error.call_count == 1

    def test_decrypt_config_unicode_decode_error(self):
        """Test _decrypt_config when UTF-8 decode fails"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Return bytes that can't be decoded as UTF-8
                        mock_decryptor.update.return_value = b"\xff\xfe\xfd"
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        with patch.object(self.app.logger, "error") as mock_logger_error:
                            result = self.app._decrypt_config("encrypted_string", "Bearer test_token")
                            # Should handle decode error gracefully
                            assert result is None or mock_logger_error.called

    def test_decrypt_config_multiple_null_bytes(self):
        """Test _decrypt_config with multiple trailing null bytes"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Simulate decrypted data with multiple null bytes
                        mock_decryptor.update.return_value = b'{"key": "value"}\x00\x08\x07\x0f\x1b\x1c\x1d'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config("encrypted_string", "Bearer test_token")

                        # Verify the result is cleaned
                        assert result == '{"key": "value"}'

    def test_decrypt_config_mixed_trailing_characters(self):
        """Test _decrypt_config with mixed trailing characters"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Simulate decrypted data with mixed trailing characters
                        mock_decryptor.update.return_value = b'{"key": "value"} \t\n\r\x00\x08\x07\x0f'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config("encrypted_string", "Bearer test_token")

                        # Verify the result is cleaned
                        assert result == '{"key": "value"} '

    def test_decrypt_config_with_trailing_backslash(self):
        """Test _decrypt_config with trailing backslash and characters after it"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Simulate decrypted data with trailing backslash and characters
                        mock_decryptor.update.return_value = b'{"key": "value"}\\abc123'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config("encrypted_string", "Bearer test_token")

                        # Verify the result is cleaned - should remove \abc123
                        assert result == '{"key": "value"}'

    def test_decrypt_config_with_multiple_backslashes(self):
        """Test _decrypt_config with multiple backslashes in the string"""
        with patch("cryptography.hazmat.primitives.ciphers.Cipher") as mock_cipher:
            with patch("cryptography.hazmat.backends.default_backend") as mock_backend:
                with patch("base64.b64decode") as mock_b64decode:
                    with patch("hashlib.sha256") as mock_sha256:
                        # Setup mocks
                        mock_backend.return_value = "backend"
                        mock_b64decode.return_value = b"iv_data_cipher_text"
                        mock_sha256_instance = MagicMock()
                        mock_sha256_instance.digest.return_value = b"key" * 8  # 32 bytes for AES-256
                        mock_sha256.return_value = mock_sha256_instance

                        mock_decryptor = MagicMock()
                        # Simulate decrypted data with multiple backslashes but only remove trailing one
                        mock_decryptor.update.return_value = b'{"key": "value\\nested"}\\trailing'
                        mock_decryptor.finalize.return_value = b""

                        mock_cipher_instance = MagicMock()
                        mock_cipher_instance.decryptor.return_value = mock_decryptor
                        mock_cipher.return_value = mock_cipher_instance

                        # Test the method
                        result = self.app._decrypt_config("encrypted_string", "Bearer test_token")

                        # Verify the result - should keep nested backslash but remove trailing one
                        assert result == '{"key": "value\\nested"}'

    def test_gen_config(self):
        self.app.local_config = True
        self.app.config_file = "test_gen_config.yaml"
        config = self.app._gen_config()
        assert "key" not in config
        assert "domain" in config
        assert "token" in config

        small_config = {"key": "value", "domain": self.test_domain}
        config = self.app._gen_config(small_config)
        assert config["key"] == "value"
        assert config["domain"] == self.test_domain
        os.remove(self.app.config_file)

    def test_gen_config_airflow(self):
        self.app.running_in_airflow = True
        test_config = {"key": "value"}
        with patch.object(self.app, "_fetch_config_from_regscale", return_value=test_config):
            config = Application(config=test_config).config
            assert len(config) > len(test_config)  # ensure the template values are being added
            assert config["key"] == "value"

    def test_gen_config_with_provided_config(self):
        self.app.local_config = True
        config = {"key": "value"}
        with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
            with patch.object(self.app, "verify_config", return_value={"key": "value", "env_key": "env_value"}):
                with patch.object(self.app, "save_config") as mock_save_config:
                    result = self.app._gen_config(config)
                    assert result == {"key": "value", "env_key": "env_value"}
                    mock_save_config.assert_called_once()

    def test_decrypting_config(self):
        """
        Test to decrypt an actual encrypted config string and verify the output.
        """
        import json

        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjpbImFiZWxhcmRvIiwiYWJlbGFyZG8iXSwiaWQiOiIzOGJhZWJkYS03ZTI5LTRlZDYtYThiZi1mNzA0NjYyYzUwOGYiLCJyb2wiOiJhcGlfYWNjZXNzIiwic3ViIjoiYWJlbGFyZG8iLCJqdGkiOiJhODlmNTVmYy04YzU3LTRjNTktYmMzNy00ZmNhZjdkYjMxOGUiLCJpYXQiOjE3NTM5ODM0MjEsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiMzhiYWViZGEtN2UyOS00ZWQ2LWE4YmYtZjcwNDY2MmM1MDhmIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9wcmltYXJ5Z3JvdXBzaWQiOiIxIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQWRtaW5pc3RyYXRvciIsIm5iZiI6MTc1Mzk4MzQyMCwiZXhwIjoxNzU0MDY5ODIwLCJpc3MiOiJSZWdTY2FsZSIsImF1ZCI6Imh0dHBzOi8vd3d3LnJlZ3NjYWxlLmlvLyJ9.WG-xraZXNpmxs1x_LmoHFKY2RyLDOrLhZJSlZyYQb3U"
        encrypted_string = "RPslDQj8r2NE5zwFnXRPHwJdgU8T6CPOWg+pQ+HEk+emPF7BV1jLKR3RHvqXO3LM8X+TTAMbfj+AoW6rV+unK0XVU4a9lI5aGYBQ7PbO4zEal7gMO+u88QM9fY0u3GqB"
        decrypted_string = self.app._decrypt_config(encrypted_string, token)
        parsed_config = json.loads(decrypted_string)
        assert isinstance(decrypted_string, str)
        assert isinstance(parsed_config, dict)
        assert len(parsed_config) == 3
        assert parsed_config["maxThreads"] == "20"
        assert parsed_config["assessmentDays"] == "10"
        assert parsed_config["test"] == "Just a test though."

    def test_gen_config_without_local_config(self):
        self.app.local_config = False
        with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
            with patch.object(self.app, "verify_config", return_value={"env_key": "env_value"}):
                with patch.object(self.app, "save_config") as mock_save_config:
                    result = self.app._gen_config()
                    assert result == {"env_key": "env_value"}
                    mock_save_config.assert_called_once()

    def test_gen_config_with_file_config(self):
        self.app.local_config = True
        with patch.object(self.app, "_get_conf", return_value={"file_key": "file_value"}):
            with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
                with patch.object(
                    self.app, "verify_config", return_value={"file_key": "file_value", "env_key": "env_value"}
                ):
                    with patch.object(self.app, "save_config") as mock_save_config:
                        result = self.app._gen_config()
                        assert result == {"file_key": "file_value", "env_key": "env_value"}
                        mock_save_config.assert_called_once()

    def test_gen_config_scanner_error(self):
        from yaml.scanner import ScannerError

        self.app.local_config = True
        with patch.object(self.app, "_get_conf", side_effect=ScannerError):
            with patch.object(self.app, "save_config") as mock_save_config:
                result = self.app._gen_config()
                assert result == self.app.template
                # called twice because the first call is to save the default config
                mock_save_config.assert_called_once()

    def test_get_airflow_config_with_dict(self):
        config = {"key": "value"}
        with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
            result = self.app._get_airflow_config(config)
            assert result == {"key": "value"}

    def test_get_airflow_config_with_str(self):
        config = "{'key': 'value'}"
        with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
            result = self.app._get_airflow_config(config)
            assert result == {"key": "value"}

    def test_get_airflow_config_with_env_vars(self):
        envars = os.environ.copy()
        envars["REGSCALE_TOKEN"] = self.test_token
        envars["REGSCALE_DOMAIN"] = self.test_domain
        with patch.dict(os.environ, envars, clear=True):
            with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
                result = self.app._get_airflow_config()
                assert result == {"key": "value"}

    def test_get_airflow_config_no_config(self):
        envars = os.environ.copy()
        envars.pop("REGSCALE_TOKEN")
        envars.pop("REGSCALE_DOMAIN")
        assert envars.get("REGSCALE_TOKEN") is None
        assert envars.get("REGSCALE_DOMAIN") is None
        with patch.dict(os.environ, envars, clear=True):
            result = self.app._get_airflow_config()
            assert result is None

        envars["REGSCALE_TOKEN"] = self.test_token
        envars["REGSCALE_DOMAIN"] = self.test_domain
        with patch.dict(os.environ, envars, clear=True):
            with patch.object(
                self.app,
                "_fetch_config_from_regscale",
                return_value={"token": self.test_token, "domain": self.test_domain},
            ):
                result = self.app._get_airflow_config()
                assert result["token"] == self.test_token
                assert result["domain"] == self.test_domain

    def test_get_airflow_config_invalid_json(self):
        config = "{'key': 'value'"
        with patch.object(self.app.logger, "debug") as mock_logger_debug:
            result = self.app._get_airflow_config(config)
            assert result is None
            mock_logger_debug.assert_called()

    def test_get_env_with_matching_keys(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1", "key2": "env_value2"}):
                result = self.app._get_env()
                assert result == {"key1": "env_value1", "key2": "env_value2"}

    def test_get_env_with_no_matching_keys(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key3": "env_value3"}):
                result = self.app._get_env()
                assert result == {"key1": "value1", "key2": "value2"}

    def test_get_env_with_key_error(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1"}):
                with patch.object(self.app.logger, "error") as mock_logger_error:
                    result = self.app._get_env()
                    assert result == {"key1": "env_value1", "key2": "value2"}
                    mock_logger_error.assert_not_called()

    def test_get_env_with_template_match(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "value1", "key2": "value2"}):
                result = self.app._get_env()
                assert result == {"key1": "value1", "key2": "value2"}
                assert self.app.templated is True

    def test_get_env_without_template_match(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1"}):
                result = self.app._get_env()
                assert result == {"key1": "env_value1", "key2": "value2"}
                assert self.app.templated is False

    def test_get_conf(self):
        self.app.config_file = self.test_config_file
        self.app = Application(config={"key": "value"})
        with patch("yaml.safe_load", return_value={"key": "value"}):
            config = self.app._get_conf()
            assert config == {"key": "value"}
        with patch("yaml.safe_load", side_effect=FileNotFoundError):
            config = self.app._get_conf()
            assert config is None

    def test_save_config(self):
        from regscale.core.app.utils.api_handler import APIHandler

        self.app.config_file = "test_save_config.yaml"
        test_config = {"key": "value"}
        with patch.object(self.app, "running_in_airflow", True):
            self.app.save_config(test_config)
            config = self.app.load_config()
            assert "key" not in config

        self.app.running_in_airflow = False
        self.app.save_config(test_config)
        config = self.app.load_config()
        assert config is not None
        assert config["key"] == "value"
        assert "domain" not in config

        test_api_handler = APIHandler()
        self.app.api_handler = test_api_handler
        test_config = {"api_handler": "testing_api_handler", "domain": self.test_domain}
        self.app.save_config(test_config)
        config = self.app.load_config()
        assert config["api_handler"] == "testing_api_handler"
        assert test_api_handler.domain == self.test_domain
        assert test_api_handler.config == test_config

        with patch.object(self.app.logger, "error") as mock_logger_error:
            with patch("yaml.dump", side_effect=OSError):
                self.app.save_config({})
                mock_logger_error.assert_called_once()

        os.remove(self.app.config_file)

    def test_get_regscale_license(self):
        with patch("requests.get"):
            regscale_license = self.app.get_regscale_license(MagicMock())
            assert isinstance(regscale_license, MagicMock)

    def test_load_config(self):
        self.app.config_file = self.test_config_file
        with patch("yaml.safe_load", side_effect=FileNotFoundError):
            config = self.app.load_config()
            assert config == {}

        self.app.save_config({"key": "value"})
        config = self.app.load_config()
        assert config == {"key": "value"}

    def test_get_regscale_license_with_config(self):
        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.return_value = Response()
        self.app.config = api.config

        with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
            response = self.app.get_regscale_license(api)
            api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
            assert isinstance(response, Response)

    def test_get_regscale_license_without_config(self):
        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.return_value = Response()
        self.app.config = None

        with patch.object(self.app, "_gen_config", return_value={"domain": self.test_domain}):
            with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
                response = self.app.get_regscale_license(api)
                api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
                assert isinstance(response, Response)

    def test_get_regscale_license_with_airflow_config(self):
        api = MagicMock()
        api.config = None
        api.get.return_value = Response()
        self.app.config = None
        self.app.running_in_airflow = True

        with patch.object(self.app, "_get_airflow_config", return_value={"domain": self.test_domain}):
            with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
                response = self.app.get_regscale_license(api)
                api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
                assert isinstance(response, Response)

    def test_get_regscale_license_with_suppressed_exception(self):
        import requests

        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.side_effect = requests.RequestException
        self.app.config = {"domain": self.test_domain}

        with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
            response = self.app.get_regscale_license(api)
            api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
            assert response is None

    def test_retrieve_domain(self):
        possible_envars = ["REGSCALE_DOMAIN", "PLATFORM_HOST", "domain"]
        for envar in possible_envars:
            with patch("os.environ", {envar: self.test_domain}):
                domain = self.app.retrieve_domain()
                assert domain == self.test_domain
            with patch("os.environ", {envar: "www.example.com"}):
                domain = self.app.retrieve_domain()
                assert domain == self.app.template["domain"]

    def test_verify_config(self):
        template = {"key": "value"}
        config = {"key": "other_value"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == {"key": "other_value"}

    def test_verify_config_with_missing_keys(self):
        template = {"key1": "value1", "key2": "value2"}
        config = {"key1": "value1"}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_type_mismatch(self):
        template = {"key1": "value1", "key2": 2}
        config = {"key1": "value1", "key2": "wrong_type"}
        expected_config = {"key1": "value1", "key2": 2}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_nested_dict(self):
        template = {"key1": "value1", "key2": {"subkey1": "subvalue1"}}
        config = {"key1": "value1", "key2": {"subkey1": "wrong_value"}}
        expected_config = {"key1": "value1", "key2": {"subkey1": "wrong_value"}}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_additional_keys(self):
        template = {"key1": "value1"}
        config = {"key1": "value1", "key2": "value2"}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_empty_config(self):
        template = {"key1": "value1", "key2": "value2"}
        config = {}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_getitem(self):
        self.app.config = {"key": "value"}
        assert self.app["key"] == "value"

    def test_setitem(self):
        self.app.config = {}
        self.app["key"] = "value"
        assert self.app.config == {"key": "value"}

    def test_delitem(self):
        self.app.config = {"key": "value"}
        del self.app["key"]
        assert self.app.config == {}

    def test_iter(self):
        self.app.config = {"key1": "value1", "key2": "value2"}
        assert list(self.app) == ["key1", "key2"]

    def test_len(self):
        self.app.config = {"key1": "value1", "key2": "value2"}
        assert len(self.app) == 2

    def test_contains(self):
        self.app.config = {"key": "value"}
        assert "key" in self.app
        assert "nonexistent_key" not in self.app
