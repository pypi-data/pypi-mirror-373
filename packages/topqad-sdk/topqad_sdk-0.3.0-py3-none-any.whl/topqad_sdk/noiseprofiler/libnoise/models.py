from typing import Union
from enum import Enum

from pydantic import BaseModel, field_validator, model_validator

from topqad_sdk.noiseprofiler.libnoise.physical_depolarizing import (
    NoiseModelParameters_PhysicalDepolarizing,
)
from topqad_sdk.noiseprofiler.libnoise.uniform_depolarizing import (
    NoiseModelParameters_UniformDepolarizing,
)


class NoiseModelName(str, Enum):
    PHYSICAL_DEPOLARIZING = "physical_depolarizing"
    UNIFORM_DEPOLARIZING = "uniform_depolarizing"


# Map noise model names to their corresponding parameter classes
noise_model_name_to_parameter_model_map = {
    NoiseModelName.PHYSICAL_DEPOLARIZING: NoiseModelParameters_PhysicalDepolarizing,
    NoiseModelName.UNIFORM_DEPOLARIZING: NoiseModelParameters_UniformDepolarizing,
}


class NoiseModelSpecificationModel(BaseModel):
    label: str | float | tuple[str, float]
    noise_model_name: NoiseModelName
    parameters: Union[
        NoiseModelParameters_PhysicalDepolarizing,
        NoiseModelParameters_UniformDepolarizing,
    ]

    @model_validator(mode="before")
    @classmethod
    def validate_parameters(cls, values):
        if isinstance(values, dict):
            noise_model_name = values.get("noise_model_name")
            parameters = values.get("parameters")

            if noise_model_name and parameters:
                if noise_model_name in noise_model_name_to_parameter_model_map:
                    param_class = noise_model_name_to_parameter_model_map[
                        noise_model_name
                    ]
                    # Convert parameters dict to the appropriate class if it's not already
                    if isinstance(parameters, dict):
                        values["parameters"] = param_class(**parameters)
                    elif not isinstance(parameters, param_class):
                        raise ValueError(
                            f"Parameters must be of type {param_class.__name__} for noise model {noise_model_name}"
                        )

        return values

    @field_validator("label", mode="before")
    @classmethod
    def convert_label_list_to_tuple(cls, v):
        if isinstance(v, list) and len(v) == 2:
            return tuple(v)
        return v
