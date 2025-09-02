from typing import Union

import numpy as np
from pydantic import field_validator, model_validator

from topqad_sdk.noiseprofiler.libnoise.noisemodel import (
    NoiseModel,
    NoiseModelParameters,
    Quantity,
)


class NoiseModelParameters_PhysicalDepolarizing(NoiseModelParameters):
    preparation_error: Quantity
    reset_error: Quantity
    measurement_error: Quantity
    one_qubit_gate_error: Quantity
    two_qubit_gate_error: Quantity
    T1_longitudinal_relaxation_time: Quantity
    T2_transverse_relaxation_time: Quantity
    preparation_time: Quantity
    reset_time: Quantity
    measurement_time: Quantity
    one_qubit_gate_time: Quantity
    two_qubit_gate_time: Quantity

    @field_validator(
        "preparation_error",
        "reset_error",
        "measurement_error",
        "one_qubit_gate_error",
        "two_qubit_gate_error",
    )
    @classmethod
    def is_error(cls, param: Quantity) -> Quantity:
        if param.value < 0 or param.value > 1:
            raise ValueError(f"Error value must be between 0 and 1, got {param.value}.")

        if param.unit != "":
            raise ValueError(f"Error unit must be empty string, got '{param.unit}'.")

        return param

    @field_validator(
        "T1_longitudinal_relaxation_time",
        "T2_transverse_relaxation_time",
        "preparation_time",
        "reset_time",
        "measurement_time",
        "one_qubit_gate_time",
        "two_qubit_gate_time",
    )
    @classmethod
    def is_time(cls, param: Quantity) -> Quantity:
        if param.value <= 0:
            raise ValueError(f"Time value must be positive, got {param.value}.")

        valid_time_units = {"ns", "μs", "ms"}
        if param.unit not in valid_time_units:
            raise ValueError(
                f"Time unit must be one of {valid_time_units}, got '{param.unit}.'"
            )

        return param

    @field_validator("one_qubit_gate_error")
    @classmethod
    def validate_one_qubit_gate_error(cls, one_qubit_gate_error: Quantity) -> Quantity:
        if one_qubit_gate_error.value > 1 - 1 / 2**1:
            raise ValueError(
                f"One-qubit gate error must be less than or equal to 1 - 1/2^1 = 0.5, got {one_qubit_gate_error.value}."
            )

        return one_qubit_gate_error

    @field_validator("two_qubit_gate_error")
    @classmethod
    def validate_two_qubit_gate_error(cls, two_qubit_gate_error: Quantity) -> Quantity:
        if two_qubit_gate_error.value > 1 - 1 / 2**2:
            raise ValueError(
                f"Two-qubit gate error must be less than or equal to 1 - 1/2^2 = 0.75, got {two_qubit_gate_error.value}."
            )

        return two_qubit_gate_error

    @model_validator(mode="after")
    def check_T1_T2_relation(self):
        T1 = float(self.T1_longitudinal_relaxation_time)
        T2 = float(self.T2_transverse_relaxation_time)

        if T2 < T1 or T2 > 2 * T1:
            raise ValueError(
                f"T2 must be greater than or equal to T1 and less than or equal to 2*T1, got T1={T1} and T2={T2}."
            )

        return self


class PhysicalDepolarizing(NoiseModel):
    r"""A physical depolarizing noise model, based on the model described in Appendix E of Ref. [1].

    It consists of three types of errors: gate errors, idling errors, and state preparation and measurement (SPAM) errors.

    ### Gate Errors

    Imperfect gates are modelled by adding a depolarizing noise channel at rate $p$ to the gate qubits after the
    application of each gate, where the parameterization assumes that $1 - p$ is the probability of leaving the input
    state unaltered.

    The rate $p$ is determined by utilizing the formula for the depolarizing channel's average gate fidelity,
    $$
    F_{\text{dep}, n} = 1 - \frac{(2^n - 1) 2^n}{2^{2n} - 1} p,
    $$
    where $n$ is the number of gate qubits.

    ### Idling Errors

    Any qubit that is idling experiences an error, dependent on both the $T_1$ (longitudinal relaxation time) and the
    $T_2$ (transverse relaxation time) of the qubit, as well as the time $t$ it takes to apply the gate(s) to the active
    qubits.

    The error is modelled with a one-qubit stochastic Pauli noise channel defined by the parameter vector
    $$
    (p_x, p_y, p_z) = \left(\frac{1}{4} (1 - e^{-t/T_1}), \frac{1}{4} (1 - e^{-t/T_1}), \frac{1}{4} (1 + e^{-t/T_1} - 2 e^{-t/T_2})\right),
    $$
    where $p_x, p_y, p_z$ are the probabilities of $X, Y, Z$ errors, respectively.

    ### SPAM Errors

    The errors in state preparation and reset are captured by assuming that, with rate $p$, the orthogonal state is
    produced, that is, $|0\rangle$ is prepared instead of $|1\rangle$ and vice versa. Similarly, measurements in the $Z$
    basis are flipped at rate $p$. In all three cases, the fidelity of the operation is
    $$
    F_{\text{SPAM}} = \frac{P(0|0) + P(1|1)}{2},
    $$
    from which we directly determine the rate $p = 1 - F_{\text{SPAM}}$.

    ### References

    [1] M. Mohseni et al., How to Build a Quantum Supercomputer: Scaling Challenges and Opportunities, (2024)
    arXiv:2411.10406.

    """

    noise_model_name = "physical_depolarizing"

    def __init__(
        self,
        *,
        preparation_error: Quantity,
        reset_error: Quantity,
        measurement_error: Quantity,
        one_qubit_gate_error: Quantity,
        two_qubit_gate_error: Quantity,
        T1_longitudinal_relaxation_time: Quantity,
        T2_transverse_relaxation_time: Quantity,
        preparation_time: Quantity,
        reset_time: Quantity,
        measurement_time: Quantity,
        one_qubit_gate_time: Quantity,
        two_qubit_gate_time: Quantity,
        noise_channel_prescription: str = "circuit",
    ):
        """Initialize the noise model

        Args:
            preparation_error (Quantity): The error with which a qubit is prepared.
            reset_error (Quantity): The error of the reset operation.
            measurement_error (Quantity): The error of the measurement operation.
            one_qubit_gate_error (Quantity): The error of any one-qubit gate.
            two_qubit_gate_error (Quantity): The error of any two-qubit gate.
            T1_longitudinal_relaxation_time (Quantity): The T1 time of a qubit.
            T2_transverse_relaxation_time (Quantity): The T2 time of a qubit.
            preparation_time (Quantity): The time to prepare a qubit in a computational basis state.
            reset_time (Quantity): The time to reset a qubit to the zero state.
            measurement_time (Quantity): The time to measure a qubit.
            one_qubit_gate_time (Quantity): The time it takes to execute any one-qubit gate.
            two_qubit_gate_time (Quantity): The time it takes to execute any two-qubit gate.
            noise_channel_prescription (str, optional): Name of prescription. Current option are ['circuit']. Defaults
                to 'circuit'.
        """
        self.input_noise_parameters: NoiseModelParameters_PhysicalDepolarizing = (
            NoiseModelParameters_PhysicalDepolarizing(
                preparation_error=preparation_error,
                reset_error=reset_error,
                measurement_error=measurement_error,
                one_qubit_gate_error=one_qubit_gate_error,
                two_qubit_gate_error=two_qubit_gate_error,
                T1_longitudinal_relaxation_time=T1_longitudinal_relaxation_time,
                T2_transverse_relaxation_time=T2_transverse_relaxation_time,
                preparation_time=preparation_time,
                reset_time=reset_time,
                measurement_time=measurement_time,
                one_qubit_gate_time=one_qubit_gate_time,
                two_qubit_gate_time=two_qubit_gate_time,
            )
        )
        # set noise channel prescription
        self.noise_channel_prescription = noise_channel_prescription

    @classmethod
    def from_dict(
        cls,
        noise_parameter_dictionary: dict[str, dict[str, Union[float, str]]],
        noise_channel_prescription: str = "circuit",
    ) -> "PhysicalDepolarizing":
        """Create noise model from a dictionary of parameters.

        Args:
            noise_parameter_dictionary (dict[str, dict[str, Union[float, str]]]): The dictionary of parameters. Each key
                should be a parameter, and the value itself a dictionary with two keys: 'value' and 'unit'. For unitless
                quantities set 'unit' to ''.
            noise_channel_prescription (str, optional): Name of prescription. Current option are ['circuit']. Defaults
                to 'circuit'.

        Returns:
            PhysicalDepolarizing: The noise model.
        """
        noise_params_model = NoiseModelParameters_PhysicalDepolarizing(
            **noise_parameter_dictionary
        )

        params_dict = {
            field: getattr(noise_params_model, field)
            for field in noise_params_model.model_fields
        }

        return cls(**params_dict, noise_channel_prescription=noise_channel_prescription)

    @classmethod
    def from_preset(
        cls, parameter_set_name: str, noise_channel_prescription: str = "circuit"
    ) -> "PhysicalDepolarizing":
        """Create noise model from inbuilt sets of parameters.

        Args:
            parameter_set_name (str): One of "baseline", "target", "desired", which are parameters sets from Ref. [1].
            noise_channel_prescription (str, optional): Name of prescription. Current option are ['circuit']. Defaults
                to 'circuit'.

        Returns:
            PhysicalDepolarizing: The noise model.
        """
        match parameter_set_name:
            case "baseline":
                params_dict = {
                    "preparation_error": {"value": 0.02, "unit": ""},
                    "reset_error": {"value": 0.01, "unit": ""},
                    "measurement_error": {"value": 0.01, "unit": ""},
                    "one_qubit_gate_error": {"value": 0.0004, "unit": ""},
                    "two_qubit_gate_error": {"value": 0.003, "unit": ""},
                    "T1_longitudinal_relaxation_time": {"value": 100, "unit": "μs"},
                    "T2_transverse_relaxation_time": {"value": 100, "unit": "μs"},
                    "preparation_time": {"value": 1000, "unit": "ns"},
                    "reset_time": {"value": 200, "unit": "ns"},
                    "measurement_time": {"value": 200, "unit": "ns"},
                    "one_qubit_gate_time": {"value": 25, "unit": "ns"},
                    "two_qubit_gate_time": {"value": 25, "unit": "ns"},
                }

            case "target":
                params_dict = {
                    "preparation_error": {"value": 0.01, "unit": ""},
                    "reset_error": {"value": 0.005, "unit": ""},
                    "measurement_error": {"value": 0.005, "unit": ""},
                    "one_qubit_gate_error": {"value": 0.0002, "unit": ""},
                    "two_qubit_gate_error": {"value": 0.0005, "unit": ""},
                    "T1_longitudinal_relaxation_time": {"value": 200, "unit": "μs"},
                    "T2_transverse_relaxation_time": {"value": 200, "unit": "μs"},
                    "preparation_time": {"value": 1000, "unit": "ns"},
                    "reset_time": {"value": 100, "unit": "ns"},
                    "measurement_time": {"value": 100, "unit": "ns"},
                    "one_qubit_gate_time": {"value": 25, "unit": "ns"},
                    "two_qubit_gate_time": {"value": 25, "unit": "ns"},
                }

            case "desired":
                params_dict = {
                    "preparation_error": {"value": 0.00588, "unit": ""},
                    "reset_error": {"value": 0.00294, "unit": ""},
                    "measurement_error": {"value": 0.00294, "unit": ""},
                    "one_qubit_gate_error": {"value": 0.00012, "unit": ""},
                    "two_qubit_gate_error": {"value": 0.00029, "unit": ""},
                    "T1_longitudinal_relaxation_time": {"value": 340, "unit": "μs"},
                    "T2_transverse_relaxation_time": {"value": 340, "unit": "μs"},
                    "preparation_time": {"value": 1000, "unit": "ns"},
                    "reset_time": {"value": 100, "unit": "ns"},
                    "measurement_time": {"value": 100, "unit": "ns"},
                    "one_qubit_gate_time": {"value": 25, "unit": "ns"},
                    "two_qubit_gate_time": {"value": 25, "unit": "ns"},
                }

        return cls.from_dict(
            noise_parameter_dictionary=params_dict,
            noise_channel_prescription=noise_channel_prescription,
        )

    @staticmethod
    def strength_idle_qubit_noise_channel(
        T1_longitudinal_relaxation_time: float, t: float
    ) -> float:
        """Calculate the strength p of a single qubit depolarizing noise channel on an idle qubit.

        This is equivalent to the decay/dephasing channel with the thermal equilibrium state
        alpha_0 = 1/2 (see Eq. (7.144) of Ref. [1]). The physical meaning of alpha_0 = 1/2 is
        that it corresponds to the limit where the equilibrium temperature is infinite.
        The depolarizing channel parameterization assumes that (1 - p) is the probability of
        leaving the input state unaltered. It is assumed that the T2 (dephasing time) is equal
        to the T1 (relaxation time).

        [1] M. A. Nielsen and I. L. Chuang, Quantum Computation and Quantum Information, 10th anniversary ed (Cambridge University Press, 2010).


        Args:
            T1_relaxation_time (float): The T1 of a qubit.
            t (float): The idling duration of the qubit.
        """
        p = 3 / 4 * (1 - np.exp(-t / T1_longitudinal_relaxation_time))
        return p

    @staticmethod
    def strength_idle_qubit_stochastic_noise_channel(
        T1_longitudinal_relaxation_time: float,
        T2_transverse_relaxation_time: float,
        t: float,
    ) -> tuple[float, float, float]:
        """Calculate the strength p of a single qubit stochastic Pauli noise channel on an idle qubit.

        This is equivalent to the decay/dephasing channel with the thermal equilibrium state
        alpha_0 = 1/2 (see Eq. (7.144) of Ref. [1]). The physical meaning of alpha_0 = 1/2 is
        that it corresponds to the limit where the equilibrium temperature is infinite.
        The stochastic Pauli channel parameterization assumes that (1 - px - py - pz) is the
        probability of leaving the input state unaltered.

        [1] M. A. Nielsen and I. L. Chuang, Quantum Computation and Quantum Information, 10th anniversary ed (Cambridge
        University Press, 2010).


        Args:
            T1_longitudinal_relaxation_time (float): The T1 of a qubit.
            T2_transverse_relaxation_time (float): The T2 of a qubit.
            t (float): The idling duration of the qubit.
        """
        px = 1 / 4 * (1 - np.exp(-t / T1_longitudinal_relaxation_time))
        py = 1 / 4 * (1 - np.exp(-t / T1_longitudinal_relaxation_time))
        pz = (
            1
            / 4
            * (
                1
                + np.exp(-t / T1_longitudinal_relaxation_time)
                - 2 * np.exp(-t / T2_transverse_relaxation_time)
            )
        )
        p = (px, py, pz)
        return p

    @staticmethod
    def strength_spam_operation_noise_channel(F: float) -> float:
        """Calculate the strength p of a Pauli X noise channel whose average fidelity is F.

        F is assumed to be:
            F = 1 - (P(1|0) + P(0|1))/2

        i.e. one minus the average probability that the desired/prepared state has indeed been prepared/measured. The
        channel parameterization assumes that (1-p_x) is the probability of leaving the input state unaltered, and p_x
        is the probability that X error has been applied.

        Args:
            F (float): Fidelity of the SPAM operation.
        """

        p_x = 1 - F
        return p_x

    @staticmethod
    def strength_gate_operation_noise_channel(F: float, n: int) -> float:
        """Calculate the strength p of a depolarizing noise channel whose average gate fidelity is F.

        The channel parameterization assumes that (1-p) is the probability of leaving the input state unaltered.

        Args:
            F (float): Average gate fidelity.
            n (float): number of gate qubits.
        """
        p = (1 - F) * (4**n - 1) / (2**n - 1) / 2**n
        return p

    def calculate_stabilization_time(self, unit="μs"):
        """Calculate the stabilization time.

        Args:
            unit (str): An acceptable unit of time.

        Returns:
            Quantity: stabilization time.
        """
        t1 = float(self.input_noise_parameters.one_qubit_gate_time)
        t2 = float(self.input_noise_parameters.two_qubit_gate_time)
        tM = float(self.input_noise_parameters.measurement_time)
        tR = float(self.input_noise_parameters.reset_time)

        stabilization_time = Quantity.from_raw_value(
            raw_value=4 * t2 + 2 * t1 + tM + tR, unit=unit
        )

        return stabilization_time
