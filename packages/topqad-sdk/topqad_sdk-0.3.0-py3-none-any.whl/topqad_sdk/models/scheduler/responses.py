from typing import Dict, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field, field_validator

from ..enums import LayoutType, StatusEnum


class SchedulerResponse(BaseModel):
    """Scheduler Response Object."""

    request_id: str = Field(description="The ID of the submitted job")
    status: StatusEnum = Field(description="The current status of the job.")
    progress_msg: Optional[str] = Field(
        default=None, description="The progress update message for the request"
    )
    progress_percentage: Optional[int] = Field(
        default=None, description="The percentage of the current progress step"
    )
    progress_step: Optional[int] = Field(
        default=None, description="The progress step of the request"
    )
    request_received_at: str = Field(
        default=None, description="Timestamp when the request was received."
    )
    name: str = Field(description="Name of the request.")
    description: Optional[str] = Field(
        description="Description of the request.", default=""
    )


class ScheduleMetadata(BaseModel):
    """Schedule Metadata Model."""

    circuit_filename: str = Field(description="The filename of the circuit.")
    expected_number_of_ticks: float = Field(
        description="The expected number of ticks for the schedule"
    )
    bounds: Tuple[float, float] = Field(
        description="""The upper and lower bounds of the number of steps for the
        circuit as a tuple of two floats."""
    )
    lattice_surgery_sizes: Dict[int, Dict[int, int]] = Field(
        description="""Histogram data for the frequency of the number of patches used
        for the lattice surgery. The format is {num_tiles: {num_bus_tiles: frequency}}
        In other words, the keys are the total number of tiles used and the values
        are dictionaries where the keys are the number of bus tiles used and the
        values are the number of times that combination of tiles was used.""",
        default={},
    )

    @field_validator("bounds")
    def validate_bounds(cls, value: Tuple[float, float]):
        """Validate the bounds."""
        if len(value) != 2:
            raise ValueError("bounds must be a tuple of two floats")
        return value

    @field_validator("lattice_surgery_sizes")
    def validate_keys(cls, histogram: Dict[int, Dict[int, int]]):
        """Validate the keys of the lattice surgery sizes."""
        errors = []
        for num_tiles, num_bus_tiles_dict in histogram.items():
            for num_bus_tiles in num_bus_tiles_dict.keys():
                if num_bus_tiles > num_tiles:
                    errors.append(
                        f"lattice_surgery_sizes: number of bus tiles {num_bus_tiles}"
                        f" can't be greater than number of tiles {num_tiles}"
                    )
        if errors:
            raise ValueError(str(errors))
        return histogram


class LogicalQubits(BaseModel):
    """Logical Qubits Model."""

    data: Optional[int] = Field(
        default=0, description="The number of logical data qubits."
    )
    ancillary: Optional[int] = Field(
        default=0, description="The number of logical ancillary qubits."
    )
    storage: Optional[int] = Field(
        default=0, description="The number of logical magic state storage qubits."
    )
    magic: Optional[int] = Field(
        default=0, description="The number of logical distilling port qubits."
    )
    bus: Optional[int] = Field(
        default=0, description="The number of logical bus qubits."
    )
    growth: Optional[int] = Field(
        default=0, description="The number of logical growth qubits."
    )
    cstorage: Optional[int] = Field(
        default=0, description="The number of logical correction storage qubits."
    )
    total: int = Field(description="The total number of logical qubits.")

    @field_validator("total", mode="before")
    def check_total(cls, v, info):
        """Validate that 'total' equals the sum of all logical qubit types."""
        total_sum = sum(info.data.values())
        if v != total_sum:
            raise ValueError(
                f"'total' should be equal to the sum of "
                f"all different types of logical qubits."
                f" Total reported as {v}, expected {total_sum}."
                f" Values: data={info.data.get('data')}, "
                f"ancillary={info.data.get('ancillary')}, "
                f"storage={info.data.get('storage')}, "
                f"magic={info.data.get('magic')}, "
                f"bus={info.data.get('bus')}"
                f"growth={info.data.get('growth')}, "
                f"cstorage={info.data.get('cstorage')}."
            )
        return v


class NumLogicalQubits(BaseModel):
    """Logical Qubits Model."""

    memory: LogicalQubits = Field(description="The number of logcial qubits in memory.")
    buffer: LogicalQubits = Field(
        description="The number of logcial qubits in buffer fabric."
    )


class HLALayoutMetadata(BaseModel):
    """HLA Layout Metadata Model."""

    type: Literal[LayoutType.HLA]
    layout_filename: str = Field(description="The filename of the layout.")
    num_buffers: int = Field(description="The number of buffers in the layout.")
    num_logical_qubits: NumLogicalQubits = Field(
        description="The number of logical qubits in the layout."
    )
    buffer_type: str = Field(description="The type of the buffer")
    # TODO bug in calculation causing an issue with validation
    # num_tiles: NumLogicalQubits = Field(description="Number of tiles in layout map")


class CustomLayoutMetadata(BaseModel):
    """Custom Layout Metadata Model."""

    type: Literal[LayoutType.CUSTOM]
    layout_filename: str = Field(description="The filename of the layout.")
    num_bus_qubits: int = Field(description="The number of bus qubits in the layout.")
    num_data_qubits: int = Field(description="The number of data qubits in the layout.")
    num_ancillary_qubits: int = Field(
        description="The number of ancillary qubits in the layout."
    )
    num_storage_qubits: int = Field(
        description="The number of storage qubits in the layout."
    )
    total_logical_qubits: int = Field(
        description="The number of total logical qubits in the layout."
    )


class CircuitDetails(BaseModel):
    """Circuit Details Model."""

    circuit_name: str = Field(description="The name of the circuit")
    instruction_set: str = Field(description="The instruction set")
    num_data_qubits_required: int = Field(
        description="The number of data qubits required"
    )
    total_num_operations: int = Field(description="The total number of operations")
    num_non_clifford_operations: int = Field(
        description="The number of non-Clifford operations"
    )
    num_clifford_operations: int = Field(
        description="The number of Clifford operations"
    )
    num_logical_measurements: int = Field(
        description="The number of logical measurements"
    )



class SchedulerSolutionResponse(SchedulerResponse):
    """Scheduler Solution Response Object.

    This object is returned from the GET compile/{request_id} endpoint.
    """

    layout_metadata: Optional[Union[HLALayoutMetadata, CustomLayoutMetadata]] = Field(
        default=None, description="The metadata of layout map", discriminator="type"
    )
    schedule_metadata: Optional[ScheduleMetadata] = Field(
        default=None, description="The metadata of the generated schedule."
    )
    schedule_filepath: Optional[str] = Field(
        default=None, description="The file path of the generated schedule in JSON"
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The elapsed time of the tool in seconds"
    )
    circuit: Optional[CircuitDetails] = Field(
        default=None, description="The metadata of the circuit"
    )
    message: Optional[str] = Field(
        default=None, description="Error message when status is failed."
    )
