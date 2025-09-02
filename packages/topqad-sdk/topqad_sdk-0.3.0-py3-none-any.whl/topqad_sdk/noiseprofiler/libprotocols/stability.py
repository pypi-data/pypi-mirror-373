import numpy as np
from pydantic import BaseModel, field_validator, model_validator

from topqad_sdk.noiseprofiler.libprotocols.protocol_handler import (
    ProtocolHandler,
    FitSpecification,
)


class ModelStability(BaseModel):
    rounds: int
    diameter: int | tuple[int, int]

    @field_validator("rounds")
    @classmethod
    def is_round(cls, value: int):
        if type(value) is not int or value < 1:
            raise ValueError("rounds must be an integer greater than or equal to 1.")

        return value

    @field_validator("diameter")
    @classmethod
    def is_diameter(cls, value: int | tuple[int, int]):
        if type(value) is int:
            if value < 2 or value % 2 == 1:
                raise ValueError(
                    "diameter must be an even integer greater than or equal to 2."
                )
        elif type(value) is tuple and len(value) == 2:
            if value[0] < 2 or value[0] % 2 == 1 or value[1] < 2 or value[1] % 2 == 1:
                raise ValueError(
                    "x and z diameters must be an even integers greater than or equal to 2."
                )
        else:
            raise ValueError("Unrecognized value for diameter.")

        return value

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.rounds > 16:
            raise ValueError(
                f"Simulations with `rounds` = {self.rounds} > 16 are not allowed."
            )
        if self.diameter > 16:
            raise ValueError(
                f"Simulations with `diameter` = {self.diameter} > 16 are not allowed."
            )

        return self


class Stability(ProtocolHandler):
    """The stability protocol [1] is used to estimate how well a fault-tolerant system can move logical observables
    through space or, equivalently, determine the product of a large region of stabilizers. Logical observables are, for
    example, moved through space in lattice surgery operations.

    ### References

    [1] Gidney et al, Stability Experiments: The Overlooked Dual of Memory Experiments, Quantum 6, 786 (2022)
    """

    protocol_category: str = "stability"
    protocol_subcategory: str = "emulated"
    protocol_name: str = "stability"
    protocol_parameters: BaseModel = ModelStability
    includes_postselection: bool = False

    fit_options: dict[tuple[str, str], FitSpecification] = dict()

    def __init__(self):
        """Create handler for the Stability protocol."""
        super().__init__()

        self.simulation_table.fields["rounds"].full_label = "Rounds"
        self.simulation_table.fields["diameter"].full_label = "Diameter"

        self.simulation_table.fields["rounds"].math_symbol = "r"
        self.simulation_table.fields["diameter"].math_symbol = "d"

    def add_instance(
        self,
        rounds: int,
        diameter: int | tuple[int, int],
        *,
        noise_model_labels: str | list[str] | None = None,
        decoder="pymatching",
    ):
        """Add instance of protocol parameters to be simulated.

        Args:
            rounds (int): Number of rounds (temporal distance).
            diameter (int | tuple[int, int]): Spatial distance of code. Must be even. Can separately specify (d_x, d_z).
            noise_model_label (str | list[str] | None, optional): The noise model label(s) for this instance. If None, then all added noise models are
                used. Default is None.
            decoder (str, optional): The decoder to use. "pymatching" is the only option.
        """
        super().add_instance(
            rounds=rounds,
            diameter=diameter,
            noise_model_labels=noise_model_labels,
            decoder=decoder,
        )
