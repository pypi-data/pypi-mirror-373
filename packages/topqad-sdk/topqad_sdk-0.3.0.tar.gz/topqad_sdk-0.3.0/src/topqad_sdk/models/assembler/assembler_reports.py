from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, List


class PRENumLogicalQubits(BaseModel):
    """Number of logical qubits in the layout."""

    transfer: Dict[str, int]


class Runtime(BaseModel):
    """Runtime model for representing time durations."""

    value: float
    unit: str


class Summary(BaseModel):
    """Summary of the PRE report."""

    expected_runtime: Runtime
    num_physical_qubits: int
    computation_cost: Optional[float] = Field(description="The computation cost.")


class InputErrorBudget(BaseModel):
    """Input error budget details."""

    target_error_bound: float


class OutputErrorBudget(BaseModel):
    """Output error budget details."""

    accumulated_error_bound: float
    synthesis_error: float
    core_processor_error: float
    magic_state_factory_error: float


class ErrorBudgets(BaseModel):
    """Error budgets for input and output errors."""

    input: InputErrorBudget
    output: OutputErrorBudget


class CoreProcessorInfo(BaseModel):
    """Information about core processor info."""

    code_distance: int
    physical_qubits_per_logical_tile: int
    total_number_physical_qubits: int


class MagicStateFactoryInfo(BaseModel):
    """Information about magic state factory."""

    code_distance: List[int]
    physical_qubits_per_logical_tile: List[int]
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
    required_logical_magic_state_error_rate: float
    logical_magic_state_error_rate: List[str]
    slowdown_factor: float
    distillation_rate: str


class CoreProcessorEmulation(BaseModel):
    """Emulation information for algorithmic data."""

    required_logical_qubit_error_rate: str
    logical_qubit_error_rate: str
    logical_cycle_time: Runtime
    reaction_time_memory: Runtime
    reaction_time_lattice_surgery: Runtime
    decoder_bandwidth: Runtime


class LogicalCycleTime(BaseModel):
    """Logical Cycle Time."""

    functional_form: str
    zones: Dict[str, Runtime]


class LogicalErrorRate(BaseModel):
    """Logical Error Rate."""

    functional_form: str
    zones: Dict[str, float]


class ReactionTime(BaseModel):
    """Reaction Time."""

    functional_form: str
    zones: Dict[str, Runtime]


class Memory(BaseModel):
    """Memory model for logical qubits."""

    protocol: str
    logical_error_rate: LogicalErrorRate
    reaction_time: ReactionTime


class FunctionalValue(BaseModel):
    """Functional value with a functional form and a value."""

    functional_form: str
    value: float


class MagicStatePreparation(BaseModel):
    """Magic State Preparation details."""

    protocol: str
    target_code_distance: int
    logical_error_rate: FunctionalValue
    discard_rate: FunctionalValue


class FunctionalOnly(BaseModel):
    """Functional form only without a value."""

    functional_form: str


class LatticeSurgery(BaseModel):
    """Lattice Surgery details."""

    protocol: str
    logical_error_rate: FunctionalOnly
    reaction_time: ReactionTime


class MagicStatePreparationUnits(BaseModel):
    """Details about Magic state preparation units."""

    target_code_distance: int
    error_rate: float


class MagicStateFactoryInfoEmulation(BaseModel):
    """Emulation information for magic state factory."""

    logical_magic_state_preparation_error_rate: float
    # TODO: Add this in the next release
    # magic_state_preparation_units: MagicStatePreparationUnits
    distillation_clifford_error_rate: List[str]
    logical_cycle_time: List[Runtime]
    reaction_time_memory_per_level: List[Runtime]
    decoder_bandwidth: List[Runtime]


class DeviceEmulation(BaseModel):
    """Emulation details about the device."""

    logical_cycle_time: LogicalCycleTime
    memory: Memory
    magic_state_preparation: MagicStatePreparation
    lattice_surgery: LatticeSurgery


class LogicalTile(BaseModel):
    """Logical Tile Model."""

    data: Optional[int] = Field(default=0, description="Number of logical data qubits.")
    ancillary: Optional[int] = Field(
        default=0, description="Number of logical ancillary qubits."
    )
    storage: Optional[int] = Field(
        default=0, description="Number of magic‑state storage qubits."
    )
    magic: Optional[int] = Field(
        default=0, description="Number of distilling magic qubits."
    )
    bus: Optional[int] = Field(default=0, description="Number of logical bus qubits.")
    growth: Optional[int] = Field(
        default=0, description="Number of logical growth qubits."
    )
    cstorage: Optional[int] = Field(
        default=0, description="Number of correction‑storage qubits."
    )
    magic_state_preparation_unit: Optional[int] = Field(
        default=0, description="Number of magic‑state prep‑unit qubits."
    )
    total: int = Field(description="Total logical qubits in this tile.")

    @field_validator("total", mode="before")
    def check_total(cls, v, info):
        """Ensure that 'total' is equal to the sum of all other fields."""
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
                f"cstorage={info.data.get('magic_state_preparation_unit')}."
            )
        return v

    @model_validator(mode="before")
    def replace_none_with_zero(cls, values: dict) -> dict:
        """Force the count to be returned for each type even if its value is 0."""
        if not isinstance(values, dict):
            return values
        for key, val in values.items():
            if isinstance(val, list):
                values[key] = [v if v is not None else 0 for v in val]
        return values


class GateCount(BaseModel):
    """Gate count model for circuit compilation."""

    pi4: int
    pi8: int
    measure: int


class CircuitCompilation(BaseModel):
    """Circuit compilation details."""

    name: str
    computational_qubit_count: int
    instruction_set: str
    gate_count: GateCount
    synthesis_accumulated_error: float


class CompilationData(BaseModel):
    """Compilation data model."""

    circuit: CircuitCompilation
    schedule: str


class LayoutMetaData(BaseModel):
    """Layout details report model."""

    num_logical_qubits: PRENumLogicalQubits


class PREReports(BaseModel):
    """PREReports Schema."""

    summary: Optional[Summary]
    error_budgets: Optional[ErrorBudgets]
    physical_resources_estimation: Optional[PhysicalResourcesEstimation]
    magic_state_factory: Optional[MagicStateFactory]
    device_emulation: Optional[DeviceEmulation]
    logical_tiles: Optional[Dict[str, LogicalTile]]
    compilation_data: Optional[CompilationData]
    pareto_point: Optional[str]

    @field_validator("logical_tiles")
    def whitelist_types_of_tiles(cls, logical_tiles):
        """Ensure the logical_tiles dict keys represent supported tile types."""
        layout_area_types = ["memory", "buffer"]
        allowed_prefixes = ["msf_level_"]
        for tile_type in logical_tiles.keys():
            if tile_type in layout_area_types:
                continue
            for prefix in allowed_prefixes:
                if tile_type.startswith(prefix):
                    break
            else:
                raise ValueError(
                    f"Unexpected key in logical_tiles: {tile_type}. Expected value "
                    f"to be one of {layout_area_types} or start with one of "
                    f"{allowed_prefixes}"
                )
        return logical_tiles
