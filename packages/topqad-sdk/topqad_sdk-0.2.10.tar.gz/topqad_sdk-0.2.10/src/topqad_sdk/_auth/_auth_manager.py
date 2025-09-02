import logging
import time
import httpx
import jwt
import os
from topqad_sdk._exceptions import TopQADValueError
from topqad_sdk._utils import Validator
from dotenv import load_dotenv

from topqad_sdk._exceptions import MissingRefreshToken


class AuthManager:
    """Handles authentication and token management for the TopQAD SDK.

    The class provides functionality to retrieve and refresh access tokens,
    extract user metadata from tokens, and ensure token validity for API requests.

    Attributes:
        domain (str): The domain URL for the authentication endpoint.
        refresh_token (str): The refresh token used to obtain new access tokens.
        _access_token (Optional[str]): The current access token.
        _expires_at (Optional[float]): The expiration time of the current access token.
        _client (httpx.Client): The HTTP client used for making requests to the
            authentication endpoint.
        _logger (logging.Logger): A logger instance for logging authentication events.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, domain: str):
        """Initializes the AuthManager with the given domain and refresh token.

        Args:
            domain (str): The domain URL for the authentication endpoint.

        Raises:
            TopQADValueError: If the TOPQAD_REFRESH_TOKEN environment variable is
            missing.
            TopQADValueError: If the domain URL is invalid.
        """
        self.refresh_token = read_token_from_env()
        if not Validator.is_url(domain):
            raise TopQADValueError(f"Invalid auth domain URL: {domain}")
        self.domain = domain
        self._client = httpx.Client()
        self._access_token = None
        self._expires_at = None
        self._logger.debug(f"Initializing AuthManager with domain={domain}.")

    def get_token(self) -> str:
        """Returns a valid access token.

        Refreshes it via the backend API endpoint if expired.

        Returns:
            str: The current access token.

        Raises:
            TopQADValueError: If the access token cannot be obtained or is invalid.
        """
        if self._access_token is None or self._is_token_expired():
            self._refresh_token()
        if self._access_token is None:
            self._logger.error("Failed to obtain a valid access token.")
            raise TopQADValueError("Failed to obtain a valid access token.")
        self._logger.debug("Access token successfully retrieved.")
        return self._access_token

    def _refresh_token(self):
        """Calls the backend to refresh the access token using a valid refresh token.

        Decodes the JWT to extract the expiration time (exp).

        Raises:
            requests.exceptions.RequestException: If the backend request fails.
            jwt.DecodeError: If the token decoding fails.
        """
        url = f"{self.domain}/auth/refresh"
        response = self._client.post(url, json={"refresh_token": self.refresh_token})
        response.raise_for_status()
        token_data = response.json()
        self._access_token = token_data
        self._logger.debug("Token successfully refreshed.")
        try:
            decoded = jwt.decode(
                self._access_token,
                options={"verify_signature": False},
                algorithms=["RS256", "HS256"],
            )
            self._expires_at = decoded.get("exp", time.time() + 3600)
            self._logger.debug(
                "Token expires at: "
                + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._expires_at))
            )
        except jwt.DecodeError as e:
            self._logger.error(f"Failed to decode token: {str(e)}")
            self._expires_at = time.time() + 3600  # Fallback

    def _is_token_expired(self) -> bool:
        """Determines whether the current Auth0 access token has timed out and expired.

        Returns:
            bool: True if the token should be refreshed; False otherwise.
        """
        if not self._expires_at:
            self._logger.debug("Token expiration time not set.")
            return True
        return time.time() >= self._expires_at - 60

    def get_user_id(self) -> str:
        """Extracts the user ID from the access token.

        Returns:
            str: The user ID extracted from the access token.

        Raises:
            jwt.DecodeError: If the token decoding fails.
        """
        self._logger.debug("Extracting user ID from access token.")
        token = self.get_token()
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        self._logger.debug(f"User ID extracted: {user_id}")
        return user_id


def read_token_from_env():
    """Reads the TOPQAD_REFRESH_TOKEN from a .env file in the project's root directory. If the token is not found, raises a MissingRefreshToken exception."""
    # Load variables from the .env file in the project's root directory
    load_dotenv()
    token = os.environ.get("TOPQAD_REFRESH_TOKEN")
    if not token:
        raise MissingRefreshToken(
            "TOPQAD_REFRESH_TOKEN is not set. Please follow the instructions in our documentation: https://topqad.1qbit.com/sdk/installation."
        )
    print("Refresh token detected in environment.")
    return token


def is_refresh_token_set() -> bool:
    """Check if the TOPQAD_REFRESH_TOKEN is set in the environment.

    Returns:
        bool: True if the token is set.

    Raises:
        MissingRefreshToken: If the token is not set.
    """
    read_token_from_env()
    return True
