"""utils.py.

This module contains shared utility functions used across the SDK.
"""

from urllib.parse import urlparse
from typing import Any
import logging
import os


class Validator:
    """Utility class for common validation methods."""

    # Add a class-level logger
    logger = logging.getLogger(__name__)

    @staticmethod
    def is_url(url: str) -> bool:
        """Validates if the given string is a valid HTTP or HTTPS URL.

        Args:
            url (str): The URL string to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            parsed_url = urlparse(url)
            is_valid_scheme = parsed_url.scheme in ("http", "https")
            has_netloc = bool(parsed_url.netloc)
            # Check for double slashes after the scheme (excluding the initial '://')
            path_and_query = parsed_url.path + (
                "?" + parsed_url.query if parsed_url.query else ""
            )
            has_double_slash = "//" in path_and_query
            return all([is_valid_scheme, has_netloc, not has_double_slash])
        except Exception:
            Validator.logger.error(f"URL validation failed for {url}")
            return False

    @staticmethod
    def is_dict(data: Any) -> bool:
        """Checks if the input is a dictionary.

        Args:
            data: The object to check.

        Returns:
            bool: True if data is a dict, False otherwise.
        """
        return isinstance(data, dict)


class Logger:
    """Utility class for logging."""

    @staticmethod
    def setup_logging():
        """Set up logging configuration for the SDK.

        Configures the root logger and sets a specific logger for the SDK to a level
        based on the environment variable `TOPQAD_LOG_LEVEL`.
        """
        log_level_str = os.environ.get("TOPQAD_LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        # Configure the root logger
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        # Set httpcore logger to WARNING to reduce httpx logs
        httpcore_logger = logging.getLogger("httpcore")
        httpcore_logger.setLevel(logging.WARNING)
        # Set the SDK-specific logger level
        logger_sdk = logging.getLogger("topqad_sdk")
        logger_sdk.setLevel(log_level)
        logger_sdk.info(f"Logging level set to {log_level_str}")
