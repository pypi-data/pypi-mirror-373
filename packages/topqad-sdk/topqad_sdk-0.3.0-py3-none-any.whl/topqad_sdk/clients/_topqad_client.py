import logging
from typing import Optional
from topqad_sdk._utils import Validator
from topqad_sdk._exceptions import (
    TopQADValueError,
)
from topqad_sdk._http_request import HTTPClient


class TopQADClient:
    """Base client for interacting with TopQAD pipeline endpoints.

    This client manages authentication, retry logic, logging, and provides
    methods for making authorized HTTP requests to TopQAD APIs.

    Attributes:
        _client (HTTPClient): Instance of HTTPClient for managing HTTP requests.
        _logger (logging.Logger): A logger instance for logging request and
            response details.

        Note: Additional attributes are managed by the `HTTPClient` instance.
            Refer to its documentation for details.
    """

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        service_url: str,
        retries: int = 3,
        retry_delay: int = 10,
    ):
        """Initializes the TopQADClient.

        Args:
            service_url (str): The service URL for API requests.
            retries (int, optional): Number of retries. Defaults to 3.
            retry_delay (int, optional): Delay between retries in seconds.
                Defaults to 10.

        Raises:
            TopQADValueError: If retries or retry_delay are negative integers.
            TopQADValueError: If the service URL is invalid.
        """
        self._client = HTTPClient(
            service_url=service_url,
            retries=retries,
            retry_delay=retry_delay,
        )
        self._logger.debug(
            "Initializing TopQADClient with "
            f"retries={retries}, retry_delay={retry_delay}"
        )

    @property
    def service_url(self):
        """Returns the service URL for the API."""
        return self._client._get_service_url()

    def set_service_url(self, url: str):
        """Set the service URL for the API.

        Args:
            url (str): The new service URL.

        Raises:
            TopQADValueError: If the provided URL is invalid.
        """
        self._client._set_service_url(url)

    def _post(self, endpoint: str, json: dict) -> dict:
        """Sends a POST request to the specified endpoint.

        Args:
            endpoint (str): API endpoint path.
            json (dict): JSON payload to send in the request body.

        Returns:
            dict: The JSON response from the API.

        Raises:
            TopQADValueError: If the payload is not a dictionary.
            TopQADRuntimeError: If the request fails after all retries.
            TopQADHTTPError: If an HTTP error occurs.
        """
        if not Validator.is_dict(json):
            raise TopQADValueError("Payload must be a dictionary.")
        self._logger.debug(f"Preparing POST request to {endpoint} with payload={json}.")
        return self._client._request("post", endpoint, json=json)

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Sends an GET request to the specified endpoint with retry logic.

        Args:
            endpoint (str): API endpoint path.
            params (Optional[dict]): Query parameters for the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            TopQADValueError: If the query parameters are not a dictionary.
            TopQADRuntimeError: If the request fails after all retries.
            TopQADHTTPError: If an HTTP error occurs.
        """
        if params and not Validator.is_dict(params):
            raise TopQADValueError("Params must be a dictionary.")
        self._logger.debug(f"Preparing GET request to {endpoint} with params={params}.")
        return self._client._request("get", endpoint, params=params)
