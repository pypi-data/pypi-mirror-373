import json
from typing import Any
from topqad_sdk.models import FTQCRequest
from topqad_sdk._exceptions import TopQADError, TopQADValueError
from pydantic import ValidationError
import logging


class HardwareParameters:
    """HardwareParameters class.

    Provides default hardware parameters, allows user customization via keyword
    arguments, supports loading configuration from a dictionary or JSON file,
    and can serialize the configuration into a dictionary for pipeline input.

    Attributes:
        _params (HardwareParameterModel): The current hardware parameters.
    """

    def __init__(self, **kwargs):
        """Initialize the HardwareParameters with default values.

        Allows overriding via keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to override default parameters.

        Raises:
            TopQADValueError: If the provided keyword arguments do not match the
            expected parameter names or types.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.debug("Initializing HardwareParameters with default values.")
        try:
            self._params = FTQCRequest(**kwargs)
        except ValidationError as e:
            raise TopQADValueError("Invalid hardware parameters.") from e

    def load_from_dict(self, params: dict):
        """Override current parameters using a dictionary.

        Args:
            params (dict): A dictionary containing hardware parameters to override
            the current settings.

        Raises:
            TopQADValueError: If the provided dictionary does not match the expected
            parameter names or types.
        """
        self._logger.info("Loading parameters from dictionary...")
        try:
            self._params = FTQCRequest(**{**self._params.model_dump(), **params})
        except ValidationError as e:
            self._logger.error("Failed to load parameters from dictionary.")
            raise TopQADValueError(f"Invalid hardware parameters. \n{e}") from e

    def load_from_json_file(self, file_path: str):
        """Override current parameters using a JSON file.

        Args:
            file_path (str): Path to the JSON file containing hardware parameters.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
            TopQADValueError: If the JSON content does not match the expected parameter
            names or types.
        """
        self._logger.info(f"Loading parameters from JSON file: {file_path}...")
        with open(
            file_path, "r", encoding="utf-8"
        ) as f:  # modification for Windows OS compatibility
            data = json.load(f)
        try:
            self.load_from_dict(data)
        except TopQADError as e:
            self._logger.error(
                f"Failed to load parameters from JSON file: {file_path}."
            )
            raise e

    def load_from_json_string(self, json_str: str):
        """Override current parameters using a JSON string.

        Args:
            json_str (str): JSON string containing hardware parameters.

        Raises:
            json.JSONDecodeError: If the string is not valid JSON.
            TopQADValueError: If the JSON content does not match the expected parameter
            names or types.
        """
        self._logger.info("Loading parameters from JSON string...")
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            self._logger.error("Invalid JSON string provided.")
            raise e
        try:
            self.load_from_dict(data)
        except TopQADError as e:
            self._logger.error("Failed to load parameters from JSON string.")
            raise e


    @property
    def as_dict(self) -> dict[str, Any]:
        """Return the parameters as a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current hardware
            parameters.
        """
        return self._params.model_dump()
