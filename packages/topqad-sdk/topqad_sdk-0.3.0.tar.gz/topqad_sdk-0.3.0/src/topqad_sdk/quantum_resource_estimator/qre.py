import logging
from typing import Tuple, Dict
from pathlib import Path

from topqad_sdk.clients.qre_client import QREClient
from topqad_sdk.models import Circuit, DemoNoiseProfilerSpecs
from topqad_sdk.library import HardwareParameters
from topqad_sdk.quantum_resource_estimator.qre_output import (
    QREOutputs,
    build_report_views,
    download_reports,
)
from topqad_sdk.quantum_resource_estimator.report import Report
from topqad_sdk._exceptions import (
    TopQADSchemaError,
    TopQADBetaVersionError,
    TopQADTimeoutError,
)


class QuantumResourceEstimator:
    """
    Wrapper class for TopQAD's Quantum Resource Estimator (QRE) API.

    Provides a simple interface to estimate quantum resources for a circuit
    on specified hardware parameters.
    """

    def __init__(self):
        """
        Initialize the QRE client and logger.
        """
        self._client = QREClient()
        self._logger = logging.getLogger(__name__)

    def run(
        self,
        circuit: Circuit,
        hardware_parameters: HardwareParameters | str,
        global_error_budget: float,
        async_mode: bool = False,
        *,
        download_reports_flag: bool = False,
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
        reports_output_file: str | Path = "reports.json",
    ) -> QREOutputs:
        """
        Estimate quantum resources for a given circuit.

        Args:
            circuit_name (str): Name of the circuit for reference.
            circuit (Circuit): The quantum circuit to estimate.
            hardware_parameters (Union[HardwareParameters, DemoNoiseProfilerSpecs]):
                A HardwareParameters object or one of the strings: "baseline", "desired", or "target".
            global_error_budget (float): Maximum allowable error for the circuit.
            async_mode (bool, optional): When enabled, allows asynchronous execution. Defaults to False. This feature is not available in the Beta version.
            download_reports_flag (bool, optional): When enabled, download detailed reports to the path specified in the reports_output_file. Defaults to False.
            number_of_repetitions (int, optional): Number of repetitions. Defaults to 1.
            cost (float, optional): Cost for QRE execution. Defaults to 0.
            remove_clifford_gates (bool, optional): Whether to remove Clifford gates. Defaults to True.
            insights_only (bool, optional): Whether to only generate insights (skip scheduling). Defaults to False.
            reports_output_file (str | Path, optional): Output file for downloaded reports. Only applicable if download_reports_flag is True. Defaults to "reports.json".

        Returns:
            QREOutputs: Contains the generated reports, viewable as an HTML table in Jupyter or as the raw dictionary.

        Raises:
            RuntimeError: If the QRE job fails or polling times out.
        """
        # Check if hardware_parameters is a valid type
        valid_specs = [spec.value for spec in DemoNoiseProfilerSpecs]
        if not isinstance(hardware_parameters, (HardwareParameters, str)):
            raise TypeError(
                f"Invalid hardware_parameters type. Expected HardwareParameters or one of the strings: {', '.join(valid_specs)}."
            )
        # If a string is provided, validate and convert to DemoNoiseProfilerSpecs
        if isinstance(hardware_parameters, str):
            if hardware_parameters not in valid_specs:
                raise ValueError(
                    f"Invalid hardware_parameters string '{hardware_parameters}'. "
                    f"Expected one of: {', '.join(valid_specs)}."
                )
            # Convert string to DemoNoiseProfilerSpecs enum
            hardware_parameters = DemoNoiseProfilerSpecs(hardware_parameters)

        circuit_name = circuit.circuit_name
        self._logger.info(
            f"Starting quantum resource estimation for circuit '{circuit_name}'..."
        )
        if async_mode:
            # Call self._client.run() when we allow asynchronous execution
            raise TopQADBetaVersionError(
                "Asynchronous mode is not available in the Beta version. "
                "Please use synchronous mode instead."
            )
        try:
            response = self._client.run_and_get_result(
                circuit=circuit,
                hardware_params=hardware_parameters,
                global_error_budget=global_error_budget,
                number_of_repetitions=number_of_repetitions,
                cost=cost,
                remove_clifford_gates=remove_clifford_gates,
                insights_only=insights_only,
            )

            summary_view, full_reports = build_report_views(response)

            if download_reports_flag:
                download_reports(full_reports, reports_output_file)

        except TopQADTimeoutError as e:
            timeout_message = (
                f" Please check the portal or call run() again to"
                f" see the status of this job and, upon completion, to obtain"
                f" your results."
            )
            self._logger.error(timeout_message)
            raise TopQADTimeoutError(f"{e} {timeout_message}")
        except Exception as e:
            self._logger.error(
                f"QuantumResourceEstimator failed for circuit '{circuit_name}': {e}"
            )
            raise RuntimeError(
                f"QuantumResourceEstimator failed for circuit '{circuit_name}'."
            ) from e

        self._logger.info(
            f"QuantumResourceEstimator completed for circuit '{circuit_name}'."
        )
        return summary_view
