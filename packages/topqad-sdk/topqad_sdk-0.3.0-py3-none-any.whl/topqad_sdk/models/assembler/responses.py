from typing import List, Optional
from pydantic import BaseModel, Field
from ..common_types import Runtime
from ..enums import StatusEnum


class Summary(BaseModel):
    """Summary of resource estimation results."""

    expected_runtime: Runtime
    num_physical_qubits: int
    computation_cost: Optional[int] = Field(
        default=None, description="The computation cost"
    )


class CoreProcessorInfo(BaseModel):
    """Information about core processor info."""

    code_distance: int
    physical_qubits_per_logical_qubit: int
    total_number_physical_qubits: int


class MagicStateFactoryInfo(BaseModel):
    """Information about magic state factory."""

    code_distance: List[int]
    physical_qubits_per_logical_qubit: List[int]
    num_physical_qubits: List[int]
    total_number_of_physical_qubits: int


class PhysicalResourcesEstimation(BaseModel):
    """Estimation of physical resources required."""

    core_processor_info: CoreProcessorInfo
    magic_state_factory_info: MagicStateFactoryInfo


class MagicStateFactory(BaseModel):
    """Details about the magic state factory."""

    distillation_levels: int
    distillation_protocol_per_level: List[str]
    num_distillation_units: List[int]
    distillation_runtime: List[Runtime]
    acceptance_probability: List[str]
    required_logical_magic_state_error_rate: str
    logical_magic_state_error_rate: List[str]


class CoreProcessorEmulation(BaseModel):
    """Emulation information for algorithmic data."""

    required_logical_qubit_error_rate: str
    logical_qubit_error_rate: str
    logical_cycle_time: Runtime
    decoder_bandwidth: Runtime


class MagicStateFactoryInfoEmulation(BaseModel):
    """Emulation information for magic state factory."""

    logical_magic_state_preparation_error_rate: float
    # TODO: Add this in the next release
    # magic_state_preparation_units: MagicStatePreparationUnits
    distillation_clifford_error_rate: List[str]
    logical_cycle_time: List[Runtime]
    decoder_bandwidth: List[Runtime]


class DeviceEmulation(BaseModel):
    """Emulation details about the device."""

    core_processor_info: CoreProcessorEmulation
    magic_state_factory_info: MagicStateFactoryInfoEmulation


class PREResponse(BaseModel):
    """PRE response model."""

    request_id: str = Field(description="Id of the PRE job request.")
    status: StatusEnum = Field(description="Current status of PRE job.")


class PREReport(PREResponse):
    """PREReport model containing information of Assembler reports."""

    elapsed_time: Optional[float] = Field(
        default=None, description="The elapsed time of the tool in seconds"
    )
    message: Optional[str] = Field(
        default=None, description="Error message when status is failed."
    )
    report_ids: Optional[List[str]] = Field(
        default_factory=list, description="The id of the Assembler reports."
    )
    plot_data_file_path: Optional[str] = Field(
        default=None, description="File path of space time plot data"
    )
