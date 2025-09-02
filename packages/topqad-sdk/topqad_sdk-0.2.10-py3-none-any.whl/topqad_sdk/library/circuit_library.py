import logging
import os
import configparser
from pathlib import Path

from topqad_sdk._http_request import HTTPClient
from topqad_sdk._exceptions import TopQADError, TopQADValueError
from topqad_sdk.models import (
    Circuit,
    RetrieveCircuitByIdResponse,
    RetrieveCircuitResponse,
)

DEFAULT_CIRCUIT_LIBRARY_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class CircuitLibrary:
    """Base class for managing circuits in the TopQAD pipeline.

    Provides methods to access example circuits, retrieve and list circuits
    for persistent reuse and lookup.

    Attributes:
        _client (HTTPClient): Instance of HTTPClient for managing HTTP requests.
        _logger (logging.Logger): Logger instance for logging operations.
        _example_circuits (list): List of example circuit names.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Initializes the CircuitLibrary instance."""
        service_url = os.environ.get("TOPQAD_DOMAIN_URL", DEFAULT_CIRCUIT_LIBRARY_URL)
        self._client = HTTPClient(service_url=service_url)
        self._logger.debug(f"Initializing CircuitLibrary with URL={service_url}")
        self._example_circuits = []

    @property
    def service_url(self):
        """Returns the URL for the CircuitLibrary."""
        return self._client._get_service_url()

    def set_service_url(self, url: str):
        """Set the URL for the CircuitLibrary.

        Args:
            url (str): The new URL.

        Raises:
            TopQADValueError: If the provided URL is invalid.
        """
        self._client._set_service_url(url)

    def get_circuit(self, circuit_id: str) -> Circuit:
        """Retrieves a circuit by its ID.

        Args:
            circuit_id (str): The ID of the circuit.

        Returns:
            Circuit: The response containing circuit details.

        Raises:
            TopQADError: If the retrieval fails.
        """
        self._logger.info(f"Retrieving circuit with ID: {circuit_id}")
        if not circuit_id:
            raise TopQADValueError("Request ID must be provided.")
        try:
            response = self._client._request(
                "get", f"/circuit_library/example/{circuit_id}"
            )
            self._logger.debug(f"Response for get_circuit: {response}")
            retrieve_response = RetrieveCircuitByIdResponse.model_validate(response)
            circuit_info = retrieve_response.circuit
            circuit = Circuit(
                id=circuit_info.id,
                status=retrieve_response.status,
                circuit_name=circuit_info.circuit_name,
                client=self,
            )
            circuit._circuit_path = getattr(circuit_info, "circuit_path", "")
            self._logger.info(f"Circuit with ID {circuit_id} retrieved successfully.")
            return circuit
        except Exception as e:
            self._logger.error(f"Failed to retrieve circuit by ID {circuit_id}.")
            raise TopQADError(
                f"Failed to retrieve circuit by ID {circuit_id}. \n{e}"
            ) from e

    def list_examples(self) -> list:
        """Fetches and updates the list of all available example circuits.

        Returns:
            list: A list of example circuits.

        Raises:
            TopQADError: If the request to list examples fails.
        """
        self._logger.info("Listing all example circuits.")
        try:
            response = self._client._request("get", "/circuit_library/examples")
            self._logger.debug(f"Response for list_examples: {response}")
            validated_response = RetrieveCircuitResponse.model_validate(response)
            circuits = getattr(validated_response, "circuits", [])
            if not circuits:
                self._logger.warning("No example circuits found.")
                self._example_circuits = []
                return []
            circuit_objs = [
                Circuit(
                    id=circuit.id,
                    circuit_name=circuit.circuit_name,
                    status=validated_response.status,
                    client=self,
                )
                for circuit in circuits
            ]
            self._example_circuits = circuit_objs
            self._logger.info("Example circuits listed successfully.")
            return circuits
        except Exception as e:
            self._logger.error("Failed to list example circuits.")
            raise TopQADError(f"Failed to list example circuits. \n{e}") from e

    @property
    def example_circuits(self) -> list[Circuit]:
        """Returns a list of example circuits.

        Returns:
            list[Circuit]: A list of example circuits.
        """
        if not self._example_circuits:
            self.list_examples()
        return self._example_circuits
