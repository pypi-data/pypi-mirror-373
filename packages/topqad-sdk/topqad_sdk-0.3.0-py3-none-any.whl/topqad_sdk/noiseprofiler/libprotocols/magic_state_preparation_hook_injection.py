import numpy as np
from pydantic import BaseModel, field_validator, model_validator

from topqad_sdk.noiseprofiler.libprotocols.protocol_handler import (
    ProtocolHandler,
    FitSpecification,
)


class ModelMagicStatePreparationHookInjection(BaseModel):
    d_1: int
    d_2: int
    r_2: int
    inject_state: str

    @field_validator("d_1", "d_2")
    @classmethod
    def is_distance(cls, d_i: int):
        if d_i < 3 or d_i % 2 == 0:
            raise ValueError(
                "d_1, d_2 must be odd integers greater than or equal to 3."
            )

        return d_i

    @model_validator(mode="after")
    def check_distances(self):
        if self.d_2 <= self.d_1:
            raise ValueError("d_2 must be greater than d_1.")

        return self

    @field_validator("r_2")
    @classmethod
    def is_round(cls, r_2: int):
        if r_2 < 1:
            raise ValueError("r_2 must be an integer greater than or equal to 1.")

        return r_2

    @field_validator("inject_state")
    @classmethod
    def is_inject_state(cls, value: str):
        if value != "X":
            raise ValueError("inject_state can only have value 'X'.")

        return value

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.d_1 > 27:
            raise ValueError(
                f"Simulations with `d_1` = {self.d_1} > 27 are not allowed."
            )
        if self.d_2 > 29:
            raise ValueError(
                f"Simulations with `d_1` = {self.d_2} > 29 are not allowed."
            )
        if self.r_2 > 29:
            raise ValueError(
                f"Simulations with `r_2` = {self.r_2} > 29 are not allowed."
            )

        return self


class MagicStatePreparationHookInjection(ProtocolHandler):
    """This protocol prepares a logical magic state. It has two stages [1]. In the first stage, two things happen
    simultaneously. First, a distance 2 surface code patch is created. However, in this process an intentional hook
    error is introduced that rotates the logical state of the code into the $T$ state. Second, a surface code of
    distance $d_1$ is created. Consequently, a $T$ logical state is created in a distance $d_1$ surface code. If any
    detectors trigger in this stage, the protocol is restarted. Otherwise, the second stage proceeds, in which the magic
    state is grown to a final distance $d_2$.

    In this implementation, an analogous protocol is constructed suitable for simulation on a Clifford simulator.
    Instead of creating a logical $T$ state, a logical $X$ state is created.

    ### References

    [1] C. Gidney, Cleaner Magic States with Hook Injection, arXiv:2302.12292.
    """

    protocol_category: str = "magic_state_preparation_unit"
    protocol_subcategory: str = "two-stage"
    protocol_name: str = "magic_state_preparation_hook_injection"
    protocol_parameters: BaseModel = ModelMagicStatePreparationHookInjection
    includes_postselection: bool = True

    fit_options: dict[tuple[str, str], FitSpecification] = {
        ("d_2", "ler"): FitSpecification(
            fit_ansatz="p_0*d_2 + p_1",
            param_bounds=([-np.inf, -np.inf], [np.inf, np.inf]),
            y_scale="linear",
            fit_ansatz_latex="{p_0} d_2 + {p_1}",
            ind_math_symbol="d_2",
        ),
        ("d_1", "dr"): FitSpecification(
            fit_ansatz="p_0 + 0*d_1",
            param_bounds=([0], [np.inf]),
            y_scale="linear",
            fit_ansatz_latex="{p_0}",
            ind_math_symbol="d_1",
        ),
    }

    def __init__(self):
        """Create handler for the Magic State Preparation Hook Injection protocol."""
        super().__init__()

        self.simulation_table.fields["d_1"].full_label = "Stage I Distance"
        self.simulation_table.fields["d_2"].full_label = "Stage II Distance"
        self.simulation_table.fields["r_2"].full_label = "Stage II Rounds"
        self.simulation_table.fields["inject_state"].full_label = "Injection State"

        self.simulation_table.fields["d_1"].math_symbol = "d_1"
        self.simulation_table.fields["d_2"].math_symbol = "d_2"
        self.simulation_table.fields["r_2"].math_symbol = "r_2"

    def add_instance(
        self,
        d_1: int,
        d_2: int,
        r_2: int,
        inject_state: str = "X",
        *,
        noise_model_labels: str | list[str] | None = None,
        decoder: str = "pymatching",
    ):
        """Add instance of protocol parameters to be simulated.

        Args:
            d_1 (int): The distance of the injection patch created in stage I. Must be odd.
            d_2 (int): The distance of the target patch created during state II. Must be odd and larger than d_1.
            r_2 (int): The number of rounds during stage II.
            inject_state (str, optional): Clifford simulation can be run with either the 'X' or 'Y' basis states. Defaults to
                'X'. Currently, 'Y' is not implemented.
            noise_model_label (str | list[str] | None, optional): The noise model label(s) for this instance. If None, then all added noise models are
                used. Default is None.
            decoder (str, optional): The decoder to use. "pymatching" is the only option.
        """
        super().add_instance(
            d_1=d_1,
            d_2=d_2,
            r_2=r_2,
            inject_state=inject_state,
            noise_model_labels=noise_model_labels,
            decoder=decoder,
        )
