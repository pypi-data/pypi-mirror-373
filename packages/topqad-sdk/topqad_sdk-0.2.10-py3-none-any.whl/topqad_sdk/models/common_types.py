from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ValueUnit(BaseModel):
    """Value with an associated unit."""

    value: float = 0.0
    unit: str = "None"


class Runtime(BaseModel):
    """Runtime value with an associated unit."""

    value: float
    unit: str


class GlobalErrorBudget(BaseModel):
    """Input error budget details."""

    target_error_bound: str
    num_repetitions: int


class InputErrorBudget(BaseModel):
    """Input error budget details."""

    target_error_bound: str


class OutputErrorBudget(BaseModel):
    """Output error budget details."""

    accumulated_error_bound: float
    solovay_kitaev_error: float
    algorithmic_error: float
    factory_error: float


class UnitErrorBudget(BaseModel):
    """Unit error budget details."""

    input: InputErrorBudget
    output: OutputErrorBudget


class ErrorBudgets(BaseModel):
    """Error budgets for global and unit errors."""

    global_: GlobalErrorBudget = Field(alias="global", validate_default=True)
    unit: UnitErrorBudget


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
        default=0, description="The number of logical distilling magic qubits."
    )
    bus: Optional[int] = Field(
        default=0, description="The number of logical bus qubits."
    )
    total: int = Field(description="The total number of logical qubits.")

    @field_validator("total", mode="before")
    def check_total(cls, v, info):
        """Validate that 'total' equals the sum of all other logical qubit fields."""
        # Access validated fields using info.data
        total_sum = sum(info.data.values())
        if v != total_sum:
            raise ValueError(
                "'total' should be equal to the sum of all other fields. "
                f"Got {v}, expected {total_sum}."
            )
        return v
