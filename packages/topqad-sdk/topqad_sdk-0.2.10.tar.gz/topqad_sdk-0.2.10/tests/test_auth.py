import os
from unittest import TestCase
from unittest.mock import patch
from topqad_sdk._auth import read_token_from_env


class TestTokenValidation(TestCase):
    """Tests for token validation utility functions."""

    @classmethod
    def setUpClass(cls):
        cls.test_refresh_token = "test_refresh_token"

    def setUp(self):
        os.environ["TOPQAD_REFRESH_TOKEN"] = self.test_refresh_token

    def tearDown(self):
        if "TOPQAD_REFRESH_TOKEN" in os.environ:
            del os.environ["TOPQAD_REFRESH_TOKEN"]

    def test_refresh_token_exists_when_set(self):
        """Should return True if TOPQAD_REFRESH_TOKEN is set (which it is in setUp)."""
        result = read_token_from_env()

        self.assertTrue(result)

    @patch("dotenv.load_dotenv")
    def test_refresh_token_not_set_raises_error(self, mock_load_dotenv):
        """Should raise EnvironmentError if TOPQAD_REFRESH_TOKEN is missing."""
        if "TOPQAD_REFRESH_TOKEN" in os.environ:
            del os.environ["TOPQAD_REFRESH_TOKEN"]

        with self.assertRaises(EnvironmentError) as context:
            read_token_from_env()

        self.assertIn("TOPQAD_REFRESH_TOKEN is not set", str(context.exception))

    @patch.dict(os.environ, {"TOPQAD_REFRESH_TOKEN": ""}, clear=True)
    def test_refresh_token_empty_string_raises_error(self):
        """Should raise EnvironmentError if TOPQAD_REFRESH_TOKEN is empty."""
        with self.assertRaises(EnvironmentError) as context:
            read_token_from_env()

        self.assertIn("TOPQAD_REFRESH_TOKEN is not set", str(context.exception))
