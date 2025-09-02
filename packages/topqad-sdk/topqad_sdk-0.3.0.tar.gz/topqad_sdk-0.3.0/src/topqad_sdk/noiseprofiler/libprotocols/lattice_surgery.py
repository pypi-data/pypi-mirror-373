from itertools import combinations
import numpy as np
from pydantic import BaseModel, field_validator, model_validator
from uncertainties.core import Variable

from topqad_sdk.noiseprofiler.libprotocols.protocol_handler import (
    ProtocolHandler,
    FitSpecification,
)


valid_observables = {
    (("X", "X"), ("Z", "Z"), ("Z", "Z")): [("Z0", "Z1", "BDZ")],
    (("X", "X"), ("Z", "Z"), ("Z", "X")): [],
    (("X", "X"), ("Z", "Z"), ("X", "Z")): [],
    (("X", "X"), ("Z", "Z"), ("X", "X")): [("X0", "X1", "BSX")],
    (("X", "X"), ("X", "X"), ("Z", "Z")): ["BSX"],
    (("X", "X"), ("X", "X"), ("Z", "X")): ["X1", "BSX"],
    (("X", "X"), ("X", "X"), ("X", "Z")): ["X0", "BSX"],
    (("X", "X"), ("X", "X"), ("X", "X")): ["X0", "X1", "BSX"],
    (("X", "X"), ("X", "Z"), ("Z", "Z")): [],
    (("X", "X"), ("X", "Z"), ("Z", "X")): [("X1", "BSX")],
    (("X", "X"), ("X", "Z"), ("X", "Z")): ["X0"],
    (("X", "X"), ("X", "Z"), ("X", "X")): ["X0", ("X1", "BSX")],
    (("X", "X"), ("Z", "X"), ("Z", "Z")): [],
    (("X", "X"), ("Z", "X"), ("Z", "X")): ["X1"],
    (("X", "X"), ("Z", "X"), ("X", "Z")): [("X0", "BSX")],
    (("X", "X"), ("Z", "X"), ("X", "X")): ["X1", ("X0", "BSX")],
    (("Z", "Z"), ("X", "X"), ("X", "X")): [("X0", "X1", "BDX")],
    (("Z", "Z"), ("X", "X"), ("X", "Z")): [],
    (("Z", "Z"), ("X", "X"), ("Z", "X")): [],
    (("Z", "Z"), ("X", "X"), ("Z", "Z")): [("Z0", "Z1", "BSZ")],
    (("Z", "Z"), ("Z", "Z"), ("X", "X")): ["BSZ"],
    (("Z", "Z"), ("Z", "Z"), ("X", "Z")): ["Z1", "BSZ"],
    (("Z", "Z"), ("Z", "Z"), ("Z", "X")): ["Z0", "BSZ"],
    (("Z", "Z"), ("Z", "Z"), ("Z", "Z")): ["Z0", "Z1", "BSZ"],
    (("Z", "Z"), ("Z", "X"), ("X", "X")): [],
    (("Z", "Z"), ("Z", "X"), ("X", "Z")): [("Z1", "BSZ")],
    (("Z", "Z"), ("Z", "X"), ("Z", "X")): ["Z0"],
    (("Z", "Z"), ("Z", "X"), ("Z", "Z")): ["Z0", ("Z1", "BSZ")],
    (("Z", "Z"), ("X", "Z"), ("X", "X")): [],
    (("Z", "Z"), ("X", "Z"), ("X", "Z")): ["Z1"],
    (("Z", "Z"), ("X", "Z"), ("Z", "X")): [("Z0", "BSZ")],
    (("Z", "Z"), ("X", "Z"), ("Z", "Z")): ["Z1", ("Z0", "BSZ")],
}


def _flatten_obs_combinations(input_set: list[set]) -> set[str]:
    """Flatten nested observable combinations into a single set."""
    str_obs = {item for item in input_set if isinstance(item, str)}
    comb_obs = {
        item
        for sublist in input_set
        for item in sublist
        if not isinstance(sublist, str)
    }
    return str_obs.union(comb_obs)


def validate_observable(
    merge_observable: tuple[str, str],
    preparation_basis: tuple[str, str],
    measurement_basis: tuple[str, str],
    logical_observable: tuple[str, ...],
) -> bool:
    """Validate if requested combination is valid.

    Returns:
        bool: True if combination is valid, else False.
    """
    # extract the observables
    lst = valid_observables.get(
        (merge_observable, preparation_basis, measurement_basis)
    )
    if lst is None:
        return False
    # Generate all valid combinations of observables.
    allowed = [
        _flatten_obs_combinations(comb)
        for r in range(1, len(lst) + 1)
        for comb in combinations(lst, r)
    ]
    return set(logical_observable) in allowed


class ModelLatticeSurgery(BaseModel):
    distance: int
    bus_width: int
    rounds: tuple[int, int, int]
    merge_observable: tuple[str, str]
    preparation_basis: tuple[str, str]
    measurement_basis: tuple[str, str]
    logical_observable: tuple[str, ...]

    @field_validator("distance")
    @classmethod
    def is_distance(cls, value: int):
        if value < 3 or value % 2 == 0:
            raise ValueError(
                "distance must be an odd integer greater than or equal to 3."
            )

        return value

    @field_validator("bus_width")
    @classmethod
    def is_bus_width(cls, value: int):
        if value < 1:
            raise ValueError("bus_width must be an integer greater than or equal to 1.")

        return value

    @field_validator("rounds")
    @classmethod
    def is_rounds(cls, value: tuple[int, int, int]):
        if value[0] < 0:
            raise ValueError("rounds[0] must be an integer greater than or equal to 0.")

        if value[1] < 1:
            raise ValueError("rounds[1] must be an integer greater than or equal to 1.")

        if value[2] < 0:
            raise ValueError("rounds[2] must be an integer greater than or equal to 0.")

        return value

    @field_validator("merge_observable")
    @classmethod
    def is_merge_observable(cls, value: str):
        if value not in [("X", "X"), ("Z", "Z")]:
            raise ValueError(
                "merge_observable must be either be ('X', 'X') and ('Z', 'Z')."
            )

        return value

    @field_validator("preparation_basis")
    @classmethod
    def is_preparation_basis(cls, value: tuple[str, str]):
        if value[0] not in ["X", "Z"]:
            raise ValueError("preparation_basis[0] can either be 'X' or 'Z'.")

        if value[1] not in ["X", "Z"]:
            raise ValueError("preparation_basis[1] can either be 'X' or 'Z'.")

        return value

    @field_validator("measurement_basis")
    @classmethod
    def is_measurement_basis(cls, value: tuple[str, str]):
        if value[0] not in ["X", "Z"]:
            raise ValueError("measurement_basis[0] can either be 'X' or 'Z'..")

        if value[1] not in ["X", "Z"]:
            raise ValueError("measurement_basis[1] can either be 'X' or 'Z'.")

        return value

    @field_validator("logical_observable")
    @classmethod
    def is_logical_observable(cls, value: tuple[str, ...]):
        for v in value:
            if v not in ["X0", "X1", "Z0", "Z1", "BSX", "BSZ", "BDX", "BDZ"]:
                raise ValueError("logical_observable has non-valid entries.")

        return value

    @model_validator(mode="after")
    def valid_combination(self):
        if not validate_observable(
            self.merge_observable,
            self.preparation_basis,
            self.measurement_basis,
            self.logical_observable,
        ):
            raise ValueError(
                "The provided combination of bases and observables is not valid. Please see LatticeSurgery.valid_observables."
            )

        return self

    @model_validator(mode="after")
    def enforce_maximum_values(self):
        if self.distance > 11:
            raise ValueError(
                f"Simulations with `distance` = {self.distance} > 11 are not allowed."
            )
        if self.bus_width > 11:
            raise ValueError(
                f"Simulations with `bus_width` = {self.bus_width} > 11 are not allowed."
            )
        if self.rounds[0] > 11 or self.rounds[1] > 11 or self.rounds[1] > 11:
            raise ValueError(
                f"Simulations with `rounds` = {self.rounds} > 11 are not allowed."
            )

        return self


class LatticeSurgery(ProtocolHandler):
    r"""Lattice surgery is the method by which entangling operations can be performed on surface code qubits. A lattice
    surgery is equivalent to measuring a joint Pauli operator of two or more qubits. For example, two logical surface
    code patches could have their $XX$ operator measured. If they are in the $a|++\rangle + b|--\rangle$ state then the
    outcome would be $+1$, if they are in $a|+-\rangle + b|-+\rangle$ state then the outcome would be $-1$, and if they are
    in any other state, then the outcome would be random.

    In this protocol, a lattice surgery is implemented between two surface code patches. Two distinct logical qubits are created in the
    provided bases. They may be initially stabilized for a few rounds. Then a surface code merge is performed. This
    takes a logical operator of each of the qubits and joins the two surface code patches along these two operators.
    This is accomplished with the aid of a bus connecting the two qubit patches. This may entangle the two qubits
    depending on the bases and operators chosen. The merge code is stabilized for at least $\mathcal{O}(d)$ rounds. Finally, the bus
    region is measured. This is called splitting the code. If done correctly, the stabilizer measurements of the bus yield
    the value of the joint observable of the merge. The two qubits may be stabilized for an additonal number of rounds
    before they too are measured.
    """

    protocol_category: str = "lattice_surgery"
    protocol_subcategory: str = "emulated"
    protocol_name: str = "lattice_surgery"
    protocol_parameters: BaseModel = ModelLatticeSurgery
    includes_postselection: bool = False
    valid_observables: dict = valid_observables

    fit_options: dict[tuple[str, str], FitSpecification] = {
        ("distance", "ler"): FitSpecification(
            fit_ansatz="p_0 * 3 * d**2 * p_1**(-(d+1)/2)",
            param_bounds=([0, 0], [np.inf, np.inf]),
            y_scale="log",
            fit_ansatz_latex=r"{p_0} \times 3d^2 \times {p_1}^{{-\frac{{d+1}}{{2}}}}",
            ind_math_symbol="d",
        ),
        (("rounds", 1), "ler"): FitSpecification(
            fit_ansatz="p_0 * d**2 * p_1**(-(r+1)/2)",
            param_bounds=([0, 0], [np.inf, np.inf]),
            y_scale="log",
            fit_ansatz_latex=r"{p_0} d^2 \times {p_1}^{{-\frac{{r+1}}{{2}}}}",
            ind_math_symbol="r",
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
        """Create handler for the Lattice Surgery protocol."""
        super().__init__()

        self.simulation_table.fields["distance"].full_label = "Distance"
        self.simulation_table.fields["bus_width"].full_label = "Bus Width"
        self.simulation_table.fields["rounds"].full_label = "Rounds"
        self.simulation_table.fields["merge_observable"].full_label = "Merge Observable"
        self.simulation_table.fields["preparation_basis"].full_label = (
            "Preparation Basis"
        )
        self.simulation_table.fields["measurement_basis"].full_label = (
            "Measurement Basis"
        )
        self.simulation_table.fields["logical_observable"].full_label = (
            "Logical Observable"
        )

        self.simulation_table.fields["distance"].math_symbol = "d"
        self.simulation_table.fields["bus_width"].math_symbol = "b"
        self.simulation_table.fields["rounds"].math_symbol = "r"

    def add_instance(
        self,
        distance: int,
        bus_width: int,
        rounds: tuple[int, int, int],
        merge_observable: tuple[str, str] = ("X", "X"),
        preparation_basis: tuple[str, str] = ("X", "Z"),
        measurement_basis: tuple[str, str] = ("Z", "X"),
        logical_observable: tuple[str, ...] = ("X1", "BSX"),
        *,
        noise_model_labels: str | list[str] | None = None,
        decoder="pymatching",
    ):
        """Add instance of protocol parameters to be simulated.

        Args:
            distance (int): Distance of codes used for the two logical qubits.
            bus_width (int): number of row/column of data qubits added in the routing space.
            rounds (tuple[int, int, int]): number of rounds of the pre-merge, merge, and split phases. merge rounds must
                be greater than 0. For example, (1, d, 0) is valid.
            merge_observable (tuple[str, str], optional): Joint observable being measured. Only possiblities are
                ('X', 'X') and ('Z', 'Z'). Defaults to ('X', 'X').
            preparation_basis (tuple[str, str], optional): Logical qubits' initialization basis. Defaults to ('X', 'Z').
            measurement_basis (tuple[str, str], optional): Logical qubits' measurement basis. Defaults to ('Z', 'X').
            logical_observable (tuple[str, ...], optional): The observable used to validate the simulation. It's a tuple
                of strings, each of which specifies measurements that must be included in the observable. Possible
                strings are 'X0', 'X1', 'Z0', 'Z1', 'BSX', 'BSZ', 'BDX' and 'BDZ'. The first four are logical
                observables of the initial qubits. In the last four 'B' stands bus, 'S' stands for stabilizer, and 'D'
                stands for data. Defaults to ('X1', 'BSX').
            noise_model_label (str | list[str] | None, optional): The noise model label(s) for this instance. If None, then all added noise models are
                used. Default is None.
            decoder (str, optional): The decoder to use. "pymatching" is the only option.

        The allowed possibilites of merge_observable, preparation_basis, measurement_basis and logical_observable are
        stored in the self.valid_observables.

        Examples:
        The default values encode performing and checking teleporting a |+> state from the first to the second qubit,
        which is initially prepared in |0> using one stabilization round. So

        >>> lattice_surgery = libprotocols.LatticeSurgery()
        >>> lattice_surgery.add_noise_model(libnoise.UniformDepolarizing(p=5e-3))
        >>> lattice_surgery.add_instance(distance=3,
        ...                             bus_width=3,
        ...                             rounds=(1,3,0),
        ...                             merge_observable=('X', 'X'),
        ...                             preparation_basis=('X', 'Z'),
        ...                             measurement_basis=('Z', 'X'),
        ...                             logical_observable=('X1', 'BSX')
        ...                             )

        Here, an XX surgery is performed to move the qubit over. The initial state |+0> after the surgery is either in
        the |++> or |+-> state. The bus stabilizers should measure +1 or -1 respectively if no errors occur. Hence, to
        validate this, we compute the product of 'X1' and 'BSX'. It must be +1 if no error occurred.

        Another possible lattice surgery is with the combination merge_observable=('X', 'X'),
        preparation_basis=('X', 'X') and measurement_basis=('Z', 'X')). For this key, self.valid_observables stores
        ['X1', 'BSX']. This means that logical_observable can be one of ('X1',), ('BSX', ) or ('X1', 'BSX').
        """
        super().add_instance(
            distance=distance,
            bus_width=bus_width,
            rounds=rounds,
            merge_observable=merge_observable,
            preparation_basis=preparation_basis,
            measurement_basis=measurement_basis,
            logical_observable=logical_observable,
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
            return (Variable(2.85e-9, 0), Variable(3.4, 0))
        else:
            return super().fit_data(
                ind=ind,
                dep=dep,
                noise_model_label=noise_model_label,
                SNR_threshold=SNR_threshold,
                Abs_threshold=Abs_threshold,
            )
