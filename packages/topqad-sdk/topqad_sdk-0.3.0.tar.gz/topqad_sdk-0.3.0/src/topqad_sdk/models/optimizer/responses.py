from typing import Optional
from pydantic import BaseModel, Field
from ..enums import StatusEnum


class OptimizerResponse(BaseModel):
    """Optimizer response model."""

    request_id: str = Field(description="Id of the optimizer circuit job request.")
    status: StatusEnum = Field(description="Current status of circuit job.")
    request_received_at: str = Field(
        description="Timestamp when the request was received."
    )
    name: str = Field(description="Name of the request.")
    description: Optional[str] = Field(
        default=None, description="Description of the request."
    )


class OptimizerSolutionResponse(OptimizerResponse):
    """Optimizer solution response model."""

    optimized_circuit_path: Optional[str] = Field(
        default=None, description="Path of the optimized circuit."
    )
    circuit_name: Optional[str] = Field(
        default=None, description="Name of the circuit."
    )
    instruction_set: Optional[str] = Field(
        default=None, description="Instruction set of circuit."
    )
    num_data_qubits_required: Optional[int] = Field(
        default=None, description="Number of data qubits required."
    )
    total_num_operations: Optional[int] = Field(
        default=None, description="Total number of operations."
    )
    num_non_clifford_operations: Optional[int] = Field(
        default=None, description="Number of non clifford operations."
    )
    num_clifford_operations: Optional[int] = Field(
        default=None, description="Number of clifford operations."
    )
    num_logical_measurements: Optional[int] = Field(
        default=None, description="Number of logical measurements."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The elapsed time of the tool in seconds"
    )
    bypass_optimization: Optional[bool] = Field(
        default=None,
        description="Flag to determine whether or not to bypass optimization "
        "and use basis conversion only",
    )
    message: Optional[str] = Field(
        default=None, description="Error message when status is failed."
    )
