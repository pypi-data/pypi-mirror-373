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
from topqad_sdk.models import (
    Circuit,
    PipelineRequest,
    PipelineResponse,
    PipelineSolutionResponse,
    DemoNoiseProfilerSpecs,
)

DEFAULT_QRE_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class QREClient(TopQADClient):
    """QREClient provides methods for QRE pipeline endpoints.

    This class facilitates the submission of circuit data and hardware parameters to the
    QRE pipeline. It manages authentication headers through the Auth Manager
    and ensures proper handling of responses and errors returned by the QRE
    pipeline.

    Attributes:
        _polling_interval (int): Interval in seconds between polling attempts.
        _polling_max_attempts (int): Maximum number of polling attempts.
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
        """Initialize QREClient with polling and retry configuration.

        Args:
            retries (int, optional): Number of retries. Default is 3.
            retry_delay (int, optional): Delay between retries (sec). Default is 10.
            polling_interval (int, optional): Polling interval (sec). Default is 10.
            polling_max_attempts (int, optional): Max polling attempts. Default is 20.

        Raises:
            TopQADValueError: If polling_interval or polling_max_attempts are
                negative integers.
        """
        service_url = os.environ.get("QRE_URL", DEFAULT_QRE_URL)
        super().__init__(
            service_url=service_url,
            retries=retries,
            retry_delay=retry_delay,
        )
        self._polling_interval = polling_interval
        self._polling_max_attempts = polling_max_attempts
        if not isinstance(self._polling_interval, int) or self._polling_interval < 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")
        if (
            not isinstance(self._polling_max_attempts, int)
            or self._polling_max_attempts < 0
        ):
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )
        self._logger.debug(
            f"Initializing QREClient with "
            f"retries={retries}, retry_delay={retry_delay}, "
            f"polling_interval={polling_interval}, "
            f"polling_max_attempts={polling_max_attempts}"
        )

    def run(
        self,
        circuit: Circuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineResponse:
        """Run a new QRE pipeline.

        Args:
            circuit (Circuit): The quantum circuit to be processed.
            hardware_params (HardwareParameters | DemoNoiseProfilerSpecs):
                Hardware parameters or demo spec.
            global_error_budget (float): The global error budget for the pipeline.
            timeout (str, optional): Timeout for pipeline execution.
                Defaults to "0".
            number_of_repetitions (int, optional): Number of repetitions.
                Defaults to 1.
            cost (float, optional): Cost for the pipeline.
                Defaults to 0.
            remove_clifford_gates (bool, optional): Whether to remove Clifford gates.
                Defaults to True.
            insights_only (bool, optional): Whether to generate a schedule only.
                Defaults to False.

        Returns:
            PipelineResponse: The response from the QRE pipeline containing
                the pipeline ID.

        Raises:
            TopQADSchemaError: If hardware parameters or circuit are invalid.
            TopQADValueError: If circuit or global_error_budget is not provided.
            TopQADSchemaError: If the response is not of type PipelineResponse.
            TopQADError: If the request to run the QRE pipeline fails.
        """
        if not hardware_params or not isinstance(
            hardware_params, (HardwareParameters, DemoNoiseProfilerSpecs)
        ):
            raise TopQADSchemaError("Invalid hardware parameters provided.")
        if not circuit or not isinstance(circuit, Circuit):
            raise TopQADValueError("Invalid circuit provided.")
        if not global_error_budget:
            raise TopQADValueError("Global error budget must be provided.")
        if isinstance(hardware_params, HardwareParameters):
            ftqc_params = hardware_params.as_dict
        else:
            ftqc_params = hardware_params.value  # DemoNoiseProfilerSpecs
        payload = {
            "circuit_path": circuit.circuit_path,
            "ftqc_params": ftqc_params,
            "global_error_budget": global_error_budget,
            "timeout": timeout,
            "number_of_repetitions": number_of_repetitions,
            "cost": cost,
            "bypass_optimization": not remove_clifford_gates,
            "generate_schedule": insights_only,
        }
        self._logger.info("Submitting QRE pipeline job...")
        try:
            validated_request = PipelineRequest.model_validate(payload)
            request_as_dict = validated_request.model_dump()
            response = self._post("/pipeline", json=request_as_dict)
            self._logger.info("QRE pipeline job submitted successfully.")
            validated_response = PipelineResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error("Failed to run QRE pipeline.")
            raise TopQADError(f"Failed to run QRE pipeline. \n{e}") from e

    def get_result(self, pipeline_id: str) -> PipelineSolutionResponse:
        """Get results for a specific QRE pipeline solution by ID.

        Args:
            request_id (str): The ID of the QRE pipeline solution to retrieve.

        Returns:
            PipelineSolutionResponse: The response containing the result of
                the QRE pipeline job.

        Raises:
            TopQADValueError: If request_id is not provided.
            TopQADError: If the request to get the result fails.
            TopQADSchemaError: If the response is not of type PipelineSolutionResponse.
        """
        if not pipeline_id:
            raise TopQADValueError("Request ID must be provided.")
        self._logger.info(f"Fetching result for pipeline ID {pipeline_id}...")
        try:
            response = self._get(f"/pipeline/{pipeline_id}")
            self._logger.info(
                f"Result fetched successfully for pipeline ID {pipeline_id}."
            )
            validated_response = PipelineSolutionResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error(f"Failed to fetch result for pipeline ID {pipeline_id}.")
            raise TopQADError(
                f"Failed to get result for pipeline ID {pipeline_id}. \n{e}"
            ) from e

    def list_results(self) -> list[PipelineSolutionResponse]:
        """List all QRE pipeline solutions for the authenticated user.

        Returns:
            list[PipelineSolutionResponse]: A list of QRE pipeline solutions
            for the user.

        Raises:
            TopQADValueError: If user_id is not provided.
            TopQADSchemaError: If the response is not of type
            list[PipelineSolutionResponse].
            TopQADError: If the request to list results fails.
        """
        self._logger.info("Listing QRE pipeline results...")
        try:
            user_id = self._client._auth_manager.get_user_id()
            response = self._get(f"/pipeline/user/{user_id}")
            validated_response = [
                PipelineSolutionResponse.model_validate(item) for item in response
            ]
            return validated_response
        except Exception as e:
            self._logger.error(f"Failed to list results for user ID {user_id}.")
            raise TopQADError(
                f"Failed to get result for user ID {user_id}. \n{e}"
            ) from e

    def run_and_get_result(
        self,
        circuit: Circuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineSolutionResponse:
        """Submit a QRE pipeline job and poll for its result until completion.

        Args:
            circuit (Circuit): The quantum circuit to be processed.
            hardware_params (HardwareParameters | DemoNoiseProfilerSpecs):
                Hardware parameters or demo spec.
            global_error_budget (float): The global error budget for the pipeline.
            timeout (str): The timeout for the pipeline execution.
                Defaults to "0".
            number_of_repetitions (int): The number of repetitions for the pipeline.
                Defaults to 1.
            cost (float): The cost for the pipeline.
                Defaults to 0.
            remove_clifford_gates (bool): Whether to remove clifford gates.
                Defaults to True.
            insights_only (bool): Whether to generate a schedule.
                Defaults to False.

        Returns:
            PipelineSolutionResponse: Final result of the QRE pipeline job.

        Raises:
            TopQADSchemaError: Invalid hardware parameters or circuit provided.
            TopQADValueError: If circuit or global_error_budget is not provided.
            TopQADRuntimeError: If the job submission or polling fails.
            TopQADRuntimeError: If the request to run the QRE pipeline fails.
        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            # Submit the job
            response = self.run(
                circuit=circuit,
                hardware_params=hardware_params,
                global_error_budget=global_error_budget,
                timeout=timeout,
                number_of_repetitions=number_of_repetitions,
                cost=cost,
                remove_clifford_gates=remove_clifford_gates,
                insights_only=insights_only,
            )
            pipeline_id = getattr(response, "pipeline_id", None)
            if not pipeline_id:
                raise TopQADValueError("Pipeline ID not found in response.")
            self._logger.info(f"Polling for pipeline ID {pipeline_id} result...")
            # Poll for the result with retry logic
            attempts = 0
            while attempts < self._polling_max_attempts:
                polling_attempt_message = (
                    f"Polling for pipeline ID {pipeline_id}: attempt {attempts + 1}/"
                    f"{self._polling_max_attempts}."
                )
                self._logger.warning(polling_attempt_message)
                result = self.get_result(pipeline_id)
                if getattr(result, "status") == "done":
                    self._logger.info(
                        f"Pipeline ID {pipeline_id} completed successfully."
                    )
                    return result
                elif getattr(result, "status") == "failed":
                    pipeline_failure_message = getattr(result, "message", None)
                    message = (
                        f"Pipeline {pipeline_id} failed: "
                        f"{pipeline_failure_message}."
                    )
                    self._logger.error(message)
                    raise TopQADRuntimeError(message)
                # Wait before the next attempt
                time.sleep(self._polling_interval)
                attempts += 1
            polling_timeout_message = (
                f"The job with ID {pipeline_id} timed out before the results"
                f" were ready."
            )
            self._logger.error(polling_timeout_message)
            raise TopQADTimeoutError(polling_timeout_message)
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for QRE pipeline.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for QRE pipeline. \n{e}"
            ) from e
