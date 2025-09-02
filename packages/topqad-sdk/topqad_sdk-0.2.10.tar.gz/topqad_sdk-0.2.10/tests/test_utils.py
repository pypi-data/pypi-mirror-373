import os
import logging
from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from topqad_sdk._utils import Validator, Logger
from tests.test_helpers import generate_test_name


class TestValidator(TestCase):
    """Tests for the Validator utility class."""

    @parameterized.expand(
        [
            ("valid_http", "http://example.com", True),
            ("valid_https", "https://example.com", True),
            ("valid_http_path", "http://example.com/path/to/resource", True),
            ("valid_https_query", "https://example.com/path?query=1", True),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_valid(self, name, url, expected):
        """Test valid URLs using the is_url method."""
        self.assertEqual(Validator.is_url(url), expected)

    @parameterized.expand(
        [
            ("invalid_ftp", "ftp://example.com", False),
            ("invalid_http", "http:/example.com", False),
            ("invalid_empty", "http://", False),
            ("invalid_path", "http:///path", False),
            ("invalid_string", "just-a-string", False),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_invalid(self, name, url, expected):
        """Test invalid URLs using the is_url method."""
        self.assertEqual(Validator.is_url(url), expected)

    @parameterized.expand(
        [
            ("none", None, False),
            ("integer", 12345, False),
            ("list", [], False),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_exception(self, name, input_value, expected):
        """Test exceptions for invalid input types using the is_url method."""
        self.assertEqual(Validator.is_url(input_value), expected)

    @parameterized.expand(
        [
            ("empty_dict", {}, True),
            ("valid_dict", {"key": "value"}, True),
            ("list", [], False),
            ("string", "string", False),
            ("integer", 123, False),
        ],
        name_func=generate_test_name,
    )
    def test_is_dict(self, name, input_value, expected):
        """Test the is_dict method for various input types."""
        self.assertEqual(Validator.is_dict(input_value), expected)


class TestLogger(TestCase):
    """Tests for the Logger utility class."""

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_default_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with default log level."""
        if "TOPQAD_LOG_LEVEL" in os.environ:
            del os.environ["TOPQAD_LOG_LEVEL"]

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_custom_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with a custom log level from environment variable."""
        os.environ["TOPQAD_LOG_LEVEL"] = "DEBUG"

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_invalid_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with an invalid log level in environment variable."""
        os.environ["TOPQAD_LOG_LEVEL"] = "INVALID_LEVEL"

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")
