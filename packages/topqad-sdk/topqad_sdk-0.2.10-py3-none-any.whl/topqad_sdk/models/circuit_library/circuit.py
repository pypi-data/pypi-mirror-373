import logging


class Circuit:
    """Represents a quantum circuit."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        id: str,
        status: str,
        circuit_name: str,
        client=None,
    ):
        """Initialize Circuit.

        Args:
            id (str): Circuit ID.
            status (str): Status of the circuit.
            circuit_name (str): Name of the circuit.
            client (CircuitLibrary, optional): Client to fetch circuit details.
                Defaults to None.
        """
        self.id = id
        self.circuit_name = circuit_name
        self.status = status
        self._client = client  # Pass CircuitLibrary instance here
        self._circuit_path = None

    @property
    def circuit_path(self) -> str:
        """Fetch and return the circuit_path for this circuit.

        Returns:
            str: The circuit file path.

        Raises:
            TopQADError: If the circuit cannot be retrieved.
        """
        if not self._client:
            self._logger.error("No client set for Circuit object.")
            raise RuntimeError(
                "Unable to retrieve circuit path: no client set for Circuit object."
            )
        self._logger.info(f"Fetching circuit path for circuit ID: {self.id}")
        circuit = self._client.get_circuit(self.id)
        self._circuit_path = getattr(circuit, "_circuit_path", "")
        return self._circuit_path or ""

    @property
    def as_dict(self) -> dict:
        """Return a dictionary representation of the Circuit object.

        Returns:
            dict: Dictionary with circuit fields.
        """
        return {
            "id": self.id,
            "status": self.status,
            "circuit_name": self.circuit_name,
            "circuit_path": self.circuit_path,
        }
