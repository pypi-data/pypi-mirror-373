import logging
from enum import Enum
from functools import cached_property
from topqad_sdk.models import (
    CompilerPipelineSolutionResponse,
    Circuit,
)
from topqad_sdk.clients.compiler_client import CompilerClient
from topqad_sdk._exceptions import TopQADTimeoutError


class FiletypeEnum(str, Enum):
    decomposed_qasm = "decomposed_qasm"
    rotations_circuit = "rotations_circuit"
    scheduled_file = "scheduled_file"


class CompilationResult:
    """Result of the Compilation service run."""

    def __init__(self, response: CompilerPipelineSolutionResponse):
        steps = getattr(response, "steps")
        decomposer = steps.decomposer
        optimizer = steps.optimizer
        scheduler = steps.scheduler

        self._decomposed_circuit_path = decomposer.sk_circuit_path
        self._sk_accumulated_error = decomposer.accumulated_error
        self._num_clifford_operations = optimizer.num_clifford_operations
        self._num_non_clifford_operations = optimizer.num_non_clifford_operations
        self._total_num_operations = optimizer.total_num_operations
        self._rotations_circuit_path = optimizer.optimized_circuit_path
        self._num_logical_measurements = optimizer.num_logical_measurements
        self._scheduled_output_filepath = scheduler.schedule_filepath

    @property
    def decomposed_circuit_path(self):
        """Path to the decomposed circuit"""
        return self._decomposed_circuit_path

    @property
    def sk_accumulated_error(self):
        """Error induced by decomposition of gates"""
        return self._sk_accumulated_error

    @property
    def num_non_clifford_operations(self):
        """Number of non clifford gates"""
        return self._num_non_clifford_operations

    @property
    def total_num_operations(self):
        """Total number of gates"""
        return self._total_num_operations

    @property
    def rotations_circuit_path(self):
        """Path to the circuit decomposed into Pauli rotations"""
        return self._rotations_circuit_path

    @property
    def num_logical_measurements(self):
        """Number of logical measurements"""
        return self._num_logical_measurements

    @property
    def scheduled_output_filepath(self):
        """Path to the assembled schedule file"""
        return self._scheduled_output_filepath


class Compiler:
    """Wrapper class for interacting with the Compiler service."""

    def __init__(self):
        self._client = CompilerClient()
        self._logger = logging.getLogger(__name__)

    def compile(
        self,
        circuit: Circuit,
        error_budget: float,
        bypass_optimization: bool = False,
        insights_only: bool = False,
    ) -> CompilationResult:
        """Run the Compilation Pipeline.

        Args:
            circuit: The quantum circuit to be processed.

            error_budget: Allowed synthesis error to be used

            remove_clifford_gates: Flag to determine whether or not to bypass
                the optimization stage

            insights_only: Flag to determine if the output of the
                scheduler is produced

        Returns:
            CompilationResult: Result of the compilation run execution

        Raises:
            RuntimeError: If the Compiler service fails to execute

        """
        circuit_name = circuit.circuit_name
        self._logger.info(f"Starting compilation for circuit '{circuit_name}'...")
        try:
            result = self._client.run_and_get_results(
                circuit,
                error_budget,
                bypass_optimization,
                insights_only,
            )
        except TopQADTimeoutError as e:
            timeout_message = (
                f" Please check the portal or call compile() again to"
                f" see the status of this job and, upon completion, to obtain"
                f" your results."
            )
            self._logger.error(timeout_message)
            raise TopQADTimeoutError(f"{e} {timeout_message}")
        except Exception as e:
            self._logger.error(f"Compilation failed for circuit '{circuit_name}': {e}")
            raise RuntimeError(
                f"Compilation failed for circuit '{circuit_name}'."
            ) from e

        return CompilationResult(result)
