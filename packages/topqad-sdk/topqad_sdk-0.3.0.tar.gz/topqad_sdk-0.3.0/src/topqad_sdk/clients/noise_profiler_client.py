import os
import time
import configparser
from pathlib import Path

from ._topqad_client import TopQADClient
from topqad_sdk.library import HardwareParameters
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADValueError,
    TopQADRuntimeError,
    TopQADSchemaError,
    TopQADTimeoutError,
)
from topqad_sdk.models import FTQCResponse, FTQCSolutionResponse

DEFAULT_NOISE_PROFILER_URL = "https://ftqc.portal.topqad.1qbit-dev.com"


class NoiseProfilerClient(TopQADClient):
    """NoiseProfilerClient provides methods for Noise Profiler endpoints.

    This class facilitates the submission of circuit data and hardware parameters to the
    Noise Profiler. It manages authentication headers through the Auth Manager
    and ensures proper handling of responses and errors returned by the Noise Profiler
    pipeline.

    Attributes:
        polling_interval (int): Interval in seconds between polling attempts.
        polling_max_attempts (int): Maximum number of polling attempts.
        _logger (logging.Logger): A logger instance for logging request and
            response details.

        Note: Additional attributes are managed by the `HTTPClient` instance.
            Refer to its documentation for details.
    """

    def __init__(
        self,
        retries: int = 3,
        retry_delay: int = 10,
        polling_interval: int = 10,
        polling_max_attempts: int = 20,
    ):
        """Initialize NoiseProfilerClient with polling and retry config.

        Args:
            retries (int, optional): Number of retries. Default is 3.
            retry_delay (int, optional): Delay between retries (sec). Default is 10.
            polling_interval (int, optional): Polling interval (sec). Default is 10.
            polling_max_attempts (int, optional): Max polling attempts. Default is 20.

        Raises:
            TopQADValueError: If polling_interval or polling_max_attempts are
                negative integers.
        """
        service_url = os.environ.get("NOISE_PROFILER_URL", DEFAULT_NOISE_PROFILER_URL)
        super().__init__(
            service_url=service_url,
            retries=retries,
            retry_delay=retry_delay,
        )
        self.polling_interval = polling_interval
        self.polling_max_attempts = polling_max_attempts
        self._logger.debug(
            f"Initializing NoiseProfilerClient with "
            f"retries={retries}, retry_delay={retry_delay}, "
            f"polling_interval={polling_interval}, "
            f"polling_max_attempts={polling_max_attempts}"
        )
        if not isinstance(self.polling_interval, int) or self.polling_interval < 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")
        if (
            not isinstance(self.polling_max_attempts, int)
            or self.polling_max_attempts < 0
        ):
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )

    def run(self, hardware_params: HardwareParameters) -> FTQCResponse:
        """Run a new Noise Profiler.

        Args:
            hardware_params (HardwareParameters): The hardware parameters for the FTQC
            emulator.

        Returns:
            FTQCResponse: The response from Noise Profiler containing request ID.

        Raises:
            TopQADSchemaError: If hardware_params is not an instance of
            HardwareParameters.
            TopQADSchemaError: If the response is not of type FTQCResponse.
            TopQADError: If the request to run the Noise Profiler fails.
        """
        self._logger.info("Submitting Noise Profiler job...")
        if not isinstance(hardware_params, HardwareParameters):
            raise TopQADSchemaError(
                "hardware_params must be an instance of HardwareParameters."
            )
        payload = hardware_params.as_dict
        try:
            response = self._post("/emulate", json=payload)
            validated_response = FTQCResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error("Failed to run Noise Profiler.")
            raise TopQADError(f"Failed to run Noise Profiler. \n{e}") from e

    def get_result(self, request_id: str) -> FTQCSolutionResponse:
        """Get results for a specific FTQC solution by ID.

        Args:
            request_id (str): The ID of the Noise Profiler solution to retrieve.

        Returns:
            FTQCSolutionResponse: The response containing the result of the FTQC
            emulator job.

        Raises:
            TopQADValueError: If request_id is not provided.
            TopQADError: If the request to get the result fails.
            TopQADSchemaError: If the response is not of type FTQCSolutionResponse.
        """
        self._logger.info(f"Fetching result for request ID {request_id}...")
        if not request_id:
            raise TopQADValueError("Request ID must be provided.")
        try:
            response = self._get(f"/emulate/{request_id}")
            validated_response = FTQCSolutionResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error(f"Failed to get result for request ID {request_id}.")
            raise TopQADError(
                f"Failed to get result for request ID {request_id}. \n{e}"
            ) from e

    def list_results(self) -> list[FTQCSolutionResponse]:
        """List all Noise Profiler solutions for the authenticated user.

        Returns:
            list[FTQCSolutionResponse]: A list of Noise Profiler solutions for the user.

        Raises:
            TopQADValueError: If user_id is not provided.
            TopQADSchemaError: If the response is not of type
            list[FTQCSolutionResponse].
            TopQADError: If the request to list results fails.
        """
        self._logger.info("Listing Noise Profiler results...")
        try:
            user_id = self._client._auth_manager.get_user_id()
            response = self._get(f"/emulate/user/{user_id}")
            validated_response = [
                FTQCSolutionResponse.model_validate(item) for item in response
            ]
            return validated_response
        except Exception as e:
            self._logger.error(f"Failed to list results for user ID {user_id}.")
            raise TopQADError(
                f"Failed to get result for user ID {user_id}. \n{e}"
            ) from e

    def run_and_get_result(
        self, hardware_params: HardwareParameters
    ) -> FTQCSolutionResponse:
        """Submit a Noise Profiler job and poll for its result until completion.

        Note:
            Default polling interval is 10 seconds, and maximum attempts is 20.
            In case of timeout, increase the values of 'self.polling_interval'
            and 'self.polling_max_attempts'.

        Args:
            hardware_params (HardwareParameters): The hardware parameters for
            the Noise Profiler.

        Returns:
            FTQCSolutionResponse: Final result of the Noise Profiler job.

        Raises:
            TopQADValueError: If hardware_params is not an instance of
            HardwareParameters.
            TopQADRuntimeError: If the job submission or polling fails.
            TopQADRuntimeError: If the request to run the Noise Profiler fails.
        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            # Submit the job
            response = self.run(hardware_params=hardware_params)
            request_id = getattr(response, "request_id", None)
            if not request_id:
                raise TopQADValueError("Request ID not found in response.")
            # Poll for the result with retry logic
            self._logger.info(f"Polling for request {request_id} result...")
            attempts = 0
            while attempts < self.polling_max_attempts:
                self._logger.warning(
                    f"Polling for request {request_id}: "
                    f"attempt {attempts + 1}/"
                    f"{self.polling_max_attempts}"
                )
                result = self.get_result(request_id)
                if getattr(result, "status") == "done":
                    return result
                elif getattr(result, "status") == "failed":
                    raise TopQADRuntimeError(
                        f"Pipeline {request_id} failed: "
                        f"{getattr(result, 'message', None)}"
                    )
                # Wait before the next attempt
                time.sleep(self.polling_interval)
                attempts += 1

            polling_timeout_message = (
                f"The job with ID {request_id} timed out before the results"
                f" were ready."
            )
            self._logger.error(polling_timeout_message)
            raise TopQADTimeoutError(polling_timeout_message)
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for Noise Profiler.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for Noise Profiler. \n{e}"
            ) from e
