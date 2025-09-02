from typing import Optional
from enum import Enum

from pydantic import BaseModel, model_validator

from topqad_sdk.noiseprofiler.libnoise.models import NoiseModelSpecificationModel
from topqad_sdk.noiseprofiler.libnoise.noisemodel import Quantity
from topqad_sdk.noiseprofiler.simtable import SimTableModel


class ProtocolName(str, Enum):
    """Names of the protocols."""

    LATTICE_SURGERY = "lattice_surgery"
    MAGIC_STATE_PREPARATION_HOOK_INJECTION = "magic_state_preparation_hook_injection"
    MAGIC_STATE_PREPARATION_REP_CODE = "magic_state_preparation_rep_code"
    MAGIC_STATE_PREPARATION_CULTIVATION = "magic_state_preparation_cultivation"
    MEMORY = "memory"
    STABILITY = "stability"


class CodeName(str, Enum):
    """Names of the codes."""

    ROTATED_SURFACE_CODE = "rotated_surface_code"


class CodeModel(BaseModel):
    """Code model for noise profiler protocols."""

    name: CodeName


class SimulationParametersModel(BaseModel):
    """Simulation parameters for noise profiler protocols."""

    max_n_samples: int
    signal_to_noise: int

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.max_n_samples > 1e8:
            raise ValueError(
                f"Simulations with `max_n_samples` = {self.max_n_samples} > 1e8 are not allowed."
            )

        if self.signal_to_noise > 100:
            raise ValueError(
                f"Simulations with `signal_to_noise' = {self.signal_to_noise} > 100 are not allowed."
            )

        return self


class FitParametersModel(BaseModel):
    """Parameters for fitting data in noise profiler protocols."""

    value: float
    error: float


class FitDataModel(BaseModel):
    """Data for fitting in noise profiler protocols."""

    noise_model_label: str
    ind: str | tuple[str, int]
    dep: str
    functional_form: Optional[str] = None
    ind_math_symbol: Optional[str] = None
    fit_bounds: Optional[dict[str, list[int | float]]] = None
    fit_parameters: Optional[dict[str, FitParametersModel]] = None


class PlotParametersModel(BaseModel):
    """Parameters for plotting in noise profiler protocols."""

    ind: str
    dep: str
    fit: bool
    extrapolate: bool
    extrapolate_to_dep: float
    save_fig: Optional[bool] = None
    save_fig_dir: Optional[str] = None
    save_fig_filename: Optional[str] = None


class StabilizationTime(BaseModel):
    """Stabilization time for noise profiler protocols."""

    noise_model_label: str
    stabilization_time: Quantity


class ProtocolSpecificationModel(BaseModel):
    """Specification model for noise profiler protocols."""

    protocol_category: Optional[str] = None
    protocol_subcategory: Optional[str] = None
    protocol_name: ProtocolName
    code: CodeModel
    simulation_table: SimTableModel
    noise_models: list[NoiseModelSpecificationModel]
    simulation_parameters: Optional[SimulationParametersModel] = None
    fits: Optional[list[FitDataModel]] = None
    plots: Optional[list[PlotParametersModel]] = None
    stabilization_times: Optional[list[StabilizationTime]] = None
