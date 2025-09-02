import numpy as np
from pydantic import BaseModel, field_validator, model_validator
from uncertainties.core import Variable

from topqad_sdk.noiseprofiler.libprotocols.protocol_handler import (
    ProtocolHandler,
    FitSpecification,
)


class ModelMemory(BaseModel):
    distance: int
    rounds: int
    basis: str

    @field_validator("distance")
    @classmethod
    def is_distance(cls, value: int):
        if type(value) is not int or value < 3 or value % 2 == 0:
            raise ValueError(
                "distance must be an odd integer greater than or equal to 3."
            )

        return value

    @field_validator("rounds")
    @classmethod
    def is_round(cls, value: int):
        if type(value) is not int or value < 1:
            raise ValueError("rounds must be an integer greater than or equal to 1.")

        return value

    @field_validator("basis")
    @classmethod
    def is_basis(cls, basis: str):
        if basis not in ["X", "Z"]:
            raise ValueError("basis must be either 'X' or 'Z'.")

        return basis

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.distance > 15:
            raise ValueError(
                f"Simulations with `distance` = {self.distance} > 15 are not allowed."
            )
        if self.rounds > 15:
            raise ValueError(
                f"Simulations with `rounds` = {self.rounds} > 15 are not allowed."
            )

        return self


class Memory(ProtocolHandler):
    r"""This protocol is used to protect idle qubits from noise. For simulation, a logical basis state of the rotated surface
    code of distance $d$ is simultaneously created and stabilized for $r$ rounds. A logical zero state $|0\rangle_L$ is created by first
    indiviually preparing all the physical data qubits in the zero state $|0\rangle$ and then the $r$ stabilization rounds are
    conducted. A plus state $|+\rangle_L$ is created similarly, except that the physical data qubits are individually prepared in the plus
    state $|+\rangle$.

    To verify that the state was correctly preserved in memory, after `r` rounds, all data qubits are measured. Then, the
    value of the logical observable is extracted. For example, to verify that the $|0\rangle_L$ was preserved, the logical $Z$
    operator is determined by multiplying the value of all data qubits along the top row of the surface code grid. If the
    value is $+1$, then no logical $X$ error occured to flip the value of the state.
    """

    protocol_category: str = "memory"
    protocol_subcategory: str = "emulated"
    protocol_name: str = "memory"
    protocol_parameters: BaseModel = ModelMemory
    includes_postselection: bool = False

    fit_options: dict[tuple[str, str], FitSpecification] = {
        ("distance", "ler"): FitSpecification(
            fit_ansatz="p_0 * d**2 * p_1**(-(d+1)/2)",
            param_bounds=([0, 0], [np.inf, np.inf]),
            y_scale="log",
            fit_ansatz_latex=r"{p_0} d^2 \times {p_1}^{{-\frac{{d+1}}{{2}}}}",
            ind_math_symbol=r"d",
        ),
        ("distance", "reaction_time"): FitSpecification(
            fit_ansatz="p_0 * d**p_1",
            param_bounds=([0, 0], [np.inf, np.inf]),
            y_scale="linear",
            fit_ansatz_latex=r"{p_0} d^{p_1}",
            ind_math_symbol=r"d",
        ),
    }

    def __init__(self):
        """Create handler for the Memory protocol."""
        super().__init__()

        self.simulation_table.fields["distance"].full_label = "Distance"
        self.simulation_table.fields["rounds"].full_label = "Rounds"
        self.simulation_table.fields["basis"].full_label = "Basis"

        self.simulation_table.fields["distance"].math_symbol = "d"
        self.simulation_table.fields["rounds"].math_symbol = "r"

    def add_instance(
        self,
        distance: int,
        rounds: int,
        basis: str = "Z",
        *,
        noise_model_labels: str | list[str] | None = None,
        decoder: str = "pymatching",
    ):
        """Add instance of protocol parameters to be simulated.

        Args:
            distance (int): Distance of code. Must be odd.
            rounds (int): Number of rounds.
            basis (str, optional): The memory basis. Defaults to 'Z'.
            noise_model_label (str | list[str] | None, optional): The noise model label(s) for this instance. If None, then all added noise models are
                used. Default is None.
            decoder (str, optional): The decoder to use. "pymatching" is the only option.
        """
        super().add_instance(
            distance=distance,
            rounds=rounds,
            basis=basis,
            noise_model_labels=noise_model_labels,
            decoder=decoder,
        )

    def fit_data(
        self,
        ind: str,
        dep: str,
        noise_model_label: str = "noise_model",
        SNR_threshold: float = 5,
        Abs_threshold: float = np.inf,
    ) -> tuple[Variable, ...]:
        """Fit data for some combination of variables.

        Args:
            ind (str): The independent variable name.
            dep (str): The dependent variable name.
            noise_model_label (str): The noise model for which to fit data. Defaults to "noise_model".
            SNR_threshold (float): Points with signal-to-noise below this threshold are discarded. Defaults to 5.
            Abs_threshold (float): Points whose value is higher than this absolute threshold are discarded. Defaults to `np.inf`.


        Raises:
            ValueError: If (ind, dep) is not a key in self.fit_options.

        Returns:
            tuple[Variable, ...]: The fit parameters as uncertainities Variable types. Use p.nominal_value and p.std_dev
            to access the stored values.

        ind="distance" and dep="reaction_time" will return the reaction time for a SOTA decoder model.
        """

        if ind == "distance" and dep == "reaction_time":
            return (Variable(1.71e-9, 0), Variable(3.4, 0))
        else:
            return super().fit_data(
                ind=ind,
                dep=dep,
                noise_model_label=noise_model_label,
                SNR_threshold=SNR_threshold,
                Abs_threshold=Abs_threshold,
            )
