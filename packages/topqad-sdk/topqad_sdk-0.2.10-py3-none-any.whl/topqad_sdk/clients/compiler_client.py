import os
import time
import configparser
from pathlib import Path
from pydantic import ValidationError

from topqad_sdk.clients._topqad_client import TopQADClient
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADValueError,
    TopQADRuntimeError,
    TopQADTimeoutError,
)
from topqad_sdk.models import (
    Circuit,
    CompilerPipelineRequest,
    CompilerPipelineResponse,
    CompilerPipelineSolutionResponse,
)

DEFAULT_COMPILER_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class CompilerClient(TopQADClient):
    """Client for interacting with the Compiler pipeline endpoint.

    This class is responsible for:
    - Sending circuit data and hardware parameters to the Compiler pipeline
    - Handling authentication headers using the AuthManager
    - Processing responses and errors from the Compiler pipeline
    """

    def __init__(
        self,
        retries: int = 3,
        retry_delay: int = 10,
        polling_interval: int = 10,
        polling_max_attempts: int = 3,
    ):
        service_url = os.environ.get("COMPILER_URL", DEFAULT_COMPILER_URL)
        super().__init__(
            service_url=service_url, retries=retries, retry_delay=retry_delay
        )

        if polling_interval <= 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")

        if polling_max_attempts <= 0:
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )

        self.polling_interval = polling_interval
        self.polling_max_attempts = polling_max_attempts

        self._logger.debug(
            f"Initializing CompilerClient with "
            f"retries={retries}, retry_delay={retry_delay}, "
            f"polling_interval={polling_interval}, "
            f"polling_max_attempts={polling_max_attempts}"
        )

    def run(
        self,
        circuit: Circuit,
        error_budget: float,
        remove_clifford_gates: bool = False,
        insights_only: bool = False,
    ) -> CompilerPipelineResponse:
        """Run the Compilation Pipeline.

        Args:
            circuit: The quantum circuit to be processed.

            error_budget: Allowed synthesis error to be used

            remove_clifford_gates: Flag to determine whether or not to bypass
                the optimization stage

            insights_only: Flag to determine if the output of the
                scheduler is produced

        Returns:
            CompilerPipelineResponse: Compiler pipeline response object
                contains compiler_pipeline_id and status

        Raises:
            TopQADValueError: if there are missing or incorrect fields
            TopQADError: for server errors

        """
        if not circuit or not isinstance(circuit, Circuit):
            raise TopQADValueError("Invalid circuit provided.")
        if not error_budget:
            raise TopQADValueError("Error budget must be provided.")
        payload = {
            "circuit_path": circuit.circuit_path,
            "global_error_budget": error_budget,
            "remove_clifford_gates": remove_clifford_gates,
            "insights_only": insights_only,
        }
        try:
            payload_model = CompilerPipelineRequest.model_validate(payload)
        except ValidationError as e:
            raise TopQADValueError(
                f"Some fields are missing or incorrect: \n{e.errors()}"
            ) from e

        request_payload = payload_model.model_dump()
        try:
            response = self._post("/compiler", json=request_payload)
            response_model = CompilerPipelineResponse.model_validate(response)
            return response_model
        except ValidationError as e:
            self._logger.error("Error in server response")
            raise TopQADError(f"Error on server response\n{e}")
        except Exception as e:
            self._logger.error("Failed to run compilation pipeline.")
            raise TopQADError(f"Failed to run compilation pipeline. \n{e}") from e

    def get_result(self, compiler_pipeline_id: str) -> CompilerPipelineSolutionResponse:
        """Get results of a compilation pipeline run.

        Args:
            compiler_pipeline_id: id of the instance, provided in the response
                object of the pipeline instance submission

        Returns:
            CompilerPipelineSolutionResponse: Compiler pipeline response object
                containing the results of the steps of the compiler pipeline

        Raises:
            TopQADError: for server errors
        """
        if not compiler_pipeline_id:
            raise TopQADValueError("Request ID must be provided")

        self._logger.info(
            "Fetching result for compilation pipeline ID {compiler_pipeline_id}..."
        )
        try:
            response = self._get(f"/compiler/{compiler_pipeline_id}")
            print(response)
            response_model = CompilerPipelineSolutionResponse.model_validate(response)
            return response_model
        except ValidationError as e:
            raise TopQADError(f"Invalid response from server:\n{e.errors()}") from e
        except Exception as e:
            self._logger.error(
                f"Failed to get result for compiler pipeline ID {compiler_pipeline_id}."
            )
            raise TopQADError(
                f"Failed to get result for compiler pipeline ID {compiler_pipeline_id}.\n{e}"
            ) from e

    def run_and_get_results(
        self,
        circuit: Circuit,
        error_budget: float,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> CompilerPipelineSolutionResponse:
        """Run the Compilation Pipeline and poll the server for a result.

        Args:
            circuit: The circuit to be compiled

            error_budget: Allowed synthesis error to be used

            remove_clifford_gates: Flag to determine whether or not to bypass
                the optimization stage

            insights_only: Flag to determine if the output of the
                scheduler is produced

        Returns:
            CompilerPipelineSolutionResponse: Compiler pipeline response object
                containing the results of the steps of the compiler pipeline

        Raises:
            TopQADValueError: if the request has missing or incorrect fields,
                or if the server response is missing a request id

            TopQADError: for server errors

        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            response = self.run(
                circuit,
                error_budget,
                remove_clifford_gates,
                insights_only,
            )
        except TopQADError as e:
            raise e from None
        except Exception as e:
            raise TopQADError(f"Server error while submitting job\n{e}") from e

        try:
            compiler_pipeline_id = getattr(response, "compiler_pipeline_id", None)
            if not compiler_pipeline_id:
                raise TopQADValueError("Request ID not found in response.")

            self._logger.info("Polling results for request {compiler_pipeline_id}...")
            attempts = 0
            while attempts < self.polling_max_attempts:
                time.sleep(self.polling_interval)

                self._logger.warning(
                    f"Polling for request {compiler_pipeline_id}: "
                    f"attempt {attempts + 1}/"
                    f"{self.polling_max_attempts}"
                )
                result = self.get_result(compiler_pipeline_id)
                status = getattr(result, "status")
                if status == "done":
                    return result
                elif status == "failed":
                    # throw failed run error
                    raise TopQADRuntimeError(
                        f"Compilation pipeline {compiler_pipeline_id} failed: "
                    )

                time.sleep(self.polling_interval)
                attempts += 1
            polling_timeout_message = (
                f"The job with ID {compiler_pipeline_id} timed out before the results"
                f" were ready."
            )
            self._logger.error(polling_timeout_message)
            raise TopQADTimeoutError(polling_timeout_message)
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for the Compiler.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for compilation pipeline. \n{e}"
            ) from e
