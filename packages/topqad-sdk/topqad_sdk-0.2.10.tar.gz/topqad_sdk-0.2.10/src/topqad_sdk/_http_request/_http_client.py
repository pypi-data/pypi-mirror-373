import logging
import os
import httpx
from time import sleep
import platform
import hashlib

from topqad_sdk._auth._auth_manager import AuthManager
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADHTTPError,
    TopQADRuntimeError,
    TopQADValueError,
)
from topqad_sdk._utils import Validator

DEFAULT_AUTH_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class HTTPClient:
    """Custom HTTPX client with retry logic for 401 and 5xx errors.

    This client provides methods for making HTTP requests with retry logic
    for handling authentication errors (401) and server errors (5xx). It also
    manages authorization headers using the AuthManager.

    Attributes:
        _service_url (str): The service URL for API requests.
        _retries (int): Number of retry attempts for failed requests.
        _retry_delay (int): Delay in seconds between retry attempts.
        _auth_manager (AuthManager): Manages authentication and token retrieval.
        _client (httpx.Client): The HTTPX client instance for making requests.
        _logger (logging.Logger): A logger instance for logging request and
            response details.
    """

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        service_url: str,
        retries: int = 3,
        retry_delay: int = 10,
    ):
        """Initialize the HTTPClient.

        Args:
            service_url (str): The service URL for API requests.
            retries (int): Number of retry attempts. Defaults to 3.
            retry_delay (int): Delay between retries in seconds. Defaults to 5.

        Raises:
            TopQADValueError: If retries or retry_delay are negative integers.
            TopQADValueError: If the domain or base URL is invalid.
        """
        super().__init__()
        # Get the auth URL from environment variable or use default
        auth_url = os.environ.get("TOPQAD_DOMAIN_URL", DEFAULT_AUTH_URL)

        # Initialize components
        self._service_url = service_url
        self._retries = retries
        self._retry_delay = retry_delay
        self._auth_manager = AuthManager(domain=auth_url)
        self._client = httpx.Client(timeout=30.0)  # Set a global timeout of 30 seconds

        # Validate inputs
        if not isinstance(self._retries, int) or self._retries < 0:
            raise TopQADValueError("Retries must be a non-negative integer.")
        if not isinstance(self._retry_delay, int) or self._retry_delay < 0:
            raise TopQADValueError("Retry delay must be a non-negative integer.")
        if not Validator.is_url(self._service_url):
            raise TopQADValueError(f"Invalid service URL: {self._service_url}")

        self._logger.debug(
            f"Initializing HTTPClient with "
            f"URL={self._service_url}, retries={self._retries}, "
            f"retry_delay={self._retry_delay}"
        )

    def _get_service_url(self) -> str:
        """Returns the service URL for API requests.

        Returns:
            str: The service URL for API requests.
        """
        return self._service_url

    def _set_service_url(self, url: str):
        """Set a new service URL for API requests.

        Args:
            url (str): The new service URL.

        Raises:
            TopQADValueError: If the provided URL is not valid.
        """
        if not Validator.is_url(url):
            self._logger.error(f"Invalid service URL provided: {url}")
            raise TopQADValueError(f"Invalid service URL: {url}")
        self._service_url = url
        self._logger.info(f"Service URL successfully set to {url}")

    def _get_device_fingerprint(self) -> str:
        """Generates a device fingerprint.

        This method creates a unique identifier for the device based on
        its platform information. You can customize this to include more
        specific details.

        Returns:
            str: A SHA256 hash representing the device fingerprint, or an
                 empty string if generation fails.
        """
        self._logger.debug("Generating device fingerprint.")
        try:
            fingerprint_data = (
                f"{platform.architecture()[0]}-{platform.architecture()[1]}-"
                f"{platform.machine()}-{platform.processor()}-"
                f"{platform.system()}-{platform.node()}"
            )
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            self._logger.debug("Device fingerprint generated successfully.")
            return fingerprint
        except Exception as e:
            self._logger.warning(f"Could not generate device fingerprint: {e}")
            return ""

    def _authorized_headers(self) -> dict:
        """Generate authorization headers for API requests.

        Returns:
            dict: Headers including the Bearer token, content type, and
                  device fingerprint.

        Raises:
            TopQADError: If the token cannot be retrieved.
        """
        try:
            token = self._auth_manager.get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            # Add device fingerprint
            device_fingerprint = self._get_device_fingerprint()
            if device_fingerprint:
                headers["X-Device-Fingerprint"] = device_fingerprint

            self._logger.debug("Authorization headers successfully generated.")
            return headers
        except TopQADError as e:
            self._logger.error(f"Failed to retrieve authorization token.\n{e}")
            raise e

    def _request(self, method: str, endpoint: str, **kwargs):
        """Send an HTTP request with retry logic.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            TopQADValueError: If the constructed URL is invalid.
            TopQADHTTPError: If HTTP errors other than 401 (Unauthorized)
                and 5xx (Server errors) occur.
            TopQADRuntimeError: If the request fails after all retries.
        """
        url = f"{self._service_url}{endpoint}"
        if not Validator.is_url(url):
            raise TopQADValueError(f"Invalid URL: {url}")
        attempt = 0
        while attempt < self._retries:
            headers = self._authorized_headers()
            self._logger.info(f"{method.upper()} {url}")
            try:
                response = self._client.request(
                    method=method, url=url, headers=headers, **kwargs
                )
                # Retry logic for handling 401 and 500 level status codes
                if response.status_code == 401 and attempt == 0:
                    self._logger.warning("Received 401. Attempting token refresh.")
                    attempt += 1
                    continue
                if response.status_code >= 500 and attempt < self._retries:
                    self._logger.warning(
                        f"Server error {response.status_code}. Retrying in "
                        f"{self._retry_delay} seconds..."
                    )
                    sleep(self._retry_delay)
                    attempt += 1
                    continue
                response.raise_for_status()
                self._logger.info(f"Received response [{response.status_code}]")
                return response.json()
            except httpx.HTTPStatusError as e:
                self._logger.error(f"HTTP error: {e}")
                self._logger.error(f"Response content: {response.text}")
                raise TopQADHTTPError(
                    f"Failed request to {url} with status {response.status_code}"
                ) from e
        self._logger.error(
            f"Failed to {method.upper()} {url} after {self._retries} retries."
        )
        raise TopQADRuntimeError(
            f"Failed to {method.upper()} {url} after {self._retries} retries."
        )
