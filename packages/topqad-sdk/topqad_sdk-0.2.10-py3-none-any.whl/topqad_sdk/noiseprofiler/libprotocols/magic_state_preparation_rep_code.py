import numpy as np
from pydantic import BaseModel, field_validator, model_validator

from topqad_sdk.noiseprofiler.libprotocols.protocol_handler import (
    ProtocolHandler,
    FitSpecification,
)


class ModelMagicStatePreparationRepCode(BaseModel):
    distances: list[int]
    rounds: list[int]
    inject_state: str

    @field_validator("distances")
    @classmethod
    def is_distances(cls, distances: list[int]):
        if len(distances) != 2:
            raise ValueError("length of distances must be 2.")

        for i, value in enumerate(distances):
            if type(value) is not int or value < 3 or value % 2 == 0:
                raise ValueError(
                    "Each distance must be an odd integer greater than or equal to 3."
                )

            if i >= 1 and distances[i] < distances[i - 1]:
                raise ValueError(
                    "Each subsequent distance must be larger than the previous distance."
                )

        return distances

    @field_validator("rounds")
    @classmethod
    def is_rounds(cls, rounds: list[int]):
        if len(rounds) != 2:
            raise ValueError("length of rounds must be 2.")

        for value in rounds:
            if value < 1:
                raise ValueError(
                    "rounds must be an integer greater than or equal to 1."
                )

        return rounds

    @field_validator("inject_state")
    @classmethod
    def is_inject_state(cls, inject_state: str):
        if inject_state not in ["X", "Y"]:
            raise ValueError("inject_state can only have value 'X' or 'Y'.")

        return inject_state

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.distances[-1] > 15:
            raise ValueError(
                f"Simulations with `distances` = {self.distances} > 15 are not allowed."
            )
        if self.rounds[-1] > 15:
            raise ValueError(
                f"Simulations with `rounds` = {self.rounds} > 15 are not allowed."
            )

        return self


## Add observable to the protocol
class MagicStatePreparationRepCode(ProtocolHandler):
    """This protocol prepares a logical magic state. It is inspired by Ref. [1]. Unlike in Ref. [1], this implementation
    is on the CSS rotated surface code with odd distances. This protocol has two stages. First a two-qubit repetition
    code is created and its state is rotated with the aid of a two-qubit rotation gate to create a logical magic state.
    Next, the repetition code is deformed/expanded into a surface code patch. If, during this expansion, any of the
    detectors trigger, the protocol is restarted. In the second stage, the logical state is grown to some final desired
    distance.

    In this implementation, an analogous protocol is constructed suitable for simulation on a Clifford simulator.
    Instead of creating a logical $T$ state, a logical $X$ or $Y$ state is created.

    ### References

    [1] Singh et al., High-Fidelity Magic-State Preparation with a Biased-Noise Architecture, Phys. Rev. A 105, 052410 (2022)
    """

    protocol_category: str = "magic_state_preparation_unit"
    protocol_subcategory: str = "two-stage"
    protocol_name: str = "magic_state_preparation_rep_code"
    protocol_parameters: BaseModel = ModelMagicStatePreparationRepCode
    includes_postselection: bool = True

    fit_options: dict[tuple[str, str], FitSpecification] = {
        (("distances", 1), "ler"): FitSpecification(
            fit_ansatz="p_0 + p_1*d_2",
            param_bounds=([-np.inf, -np.inf], [np.inf, np.inf]),
            y_scale="linear",
            fit_ansatz_latex=r"{p_0} + {p_1}*d_2",
            ind_math_symbol=r"d_2",
        ),
        (("distances", 0), "dr"): FitSpecification(
            fit_ansatz="p_0 + 0*d_1",
            param_bounds=([0], [np.inf]),
            y_scale="linear",
            fit_ansatz_latex=r"{p_0} + {p_1}*d",
            ind_math_symbol=r"d_1",
        ),
    }

    def __init__(self):
        """Create handler for the Magic State Preparation Rep Code protocol."""
        super().__init__()

        self.simulation_table.fields["distances"].full_label = "Distance"
        self.simulation_table.fields["rounds"].full_label = "Rounds"
        self.simulation_table.fields["inject_state"].full_label = "Injection State"

        self.simulation_table.fields["distances"].math_symbol = "d"
        self.simulation_table.fields["rounds"].math_symbol = "r"

    def add_instance(
        self,
        distances: list[int | tuple[int, int]],
        rounds: list[int],
        inject_state: str = "X",
        noise_model_labels: str | list[str] | None = None,
        decoder="pymatching",
    ):
        """Add instance of protocol parameters to be simulated.

        Args:
            distances (list[int | tuple[int, int]]): The distances for each of the two stages. Must be odd. If any distance is a tuple, it is treated as (d_x, d_z) for that stage.
            rounds (list[int]): The number of rounds for each of the two stages.
            inject_state (str, optional): Clifford simulation can be run with either the 'X' or 'Y' basis states. Defaults to 'X'.
            noise_model_label (str | list[str] | None, optional): The noise model label(s) for this instance. If None, then all
                added noise models are used. Default is None.
            decoder (str, optional): The decoder to use. "pymatching" is the only option.
        """
        super().add_instance(
            distances=distances,
            rounds=rounds,
            inject_state=inject_state,
            noise_model_labels=noise_model_labels,
            decoder=decoder,
        )
