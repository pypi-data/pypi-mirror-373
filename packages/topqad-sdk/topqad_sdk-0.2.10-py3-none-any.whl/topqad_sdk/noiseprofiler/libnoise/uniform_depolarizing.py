from pydantic import field_validator

from topqad_sdk.noiseprofiler.libnoise.noisemodel import (
    NoiseModel,
    NoiseModelParameters,
    Quantity,
)


class NoiseModelParameters_UniformDepolarizing(NoiseModelParameters):
    p: float
    stabilization_time: Quantity

    @field_validator("p")
    @classmethod
    def is_probability(cls, p: float) -> float:
        if p < 0 or p > 1:
            raise ValueError(f"{p=} is not a valid probability value.")
        elif p > 3 / 4:
            raise ValueError(
                f"{p=} > 3/4 causes over-mixing in the one-qubit depolarizing channel."
            )
        return p

    @field_validator("stabilization_time")
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


class UniformDepolarizing(NoiseModel):
    """A simple uniform depolarizing noise model, in which all noise channels have the same strength $p$. The noise
    channels added before or after every circuit operations are as follows.

    - Preparation and reset are followed by bit or phase flip errors, depending on the basis.
    - Measurements are noisy with probability $p$ of error, and are followed by a one-qubit depolarizing noise channel.
    - One-qubit gates are followed by a one-qubit depolarizing noise channel.
    - Two-qubit gates are followed by a two-qubit depolarizing noise channel.
    - Idle qubits experience a one-qubit depolarizing noise channel at each tick.

    This model was inspired by the model described in Appendix A of Ref. [1].

    ### References

    [1] C. Gidney, N. Shutty, and C. Jones, Magic State Cultivation: Growing T States as Cheap as CNOT Gates, (2024)
        arXiv:2409.17595.
    """

    noise_model_name = "uniform_depolarizing"

    def __init__(
        self,
        *,
        p: float,
        stabilization_time: Quantity = Quantity(value=1, unit="μs"),
        noise_channel_prescription: str = "circuit",
    ):
        """Initialize uniform depolarizing noise model.

        See class docs for details.

        Args:
            p (float): Strength of noise channel. Should be between 0 and 3/4.
            stabilization_time (Quantity): The stabilization time.
            noise_channel_prescription (str, optional): Name of prescription. Current option are ['circuit']. Defaults
                to 'circuit'.

        Raises:
            ValueError: If p is not between 0 and 3/4.
        """
        self.input_noise_parameters: NoiseModelParameters_UniformDepolarizing = (
            NoiseModelParameters_UniformDepolarizing(
                p=p, stabilization_time=stabilization_time
            )
        )
        # set noise channel prescription
        self.noise_channel_prescription = noise_channel_prescription

    @classmethod
    def from_dict(
        cls,
        noise_parameter_dictionary: dict[str, float],
        noise_channel_prescription: str = "circuit",
    ):
        """Create noise model from a dictionary of parameters.

        Args:
            noise_parameter_dictionary (dict[str, float]): The dictionary of parameters. Dictionary is of the form
                `{"p": 0.01}`.
            noise_channel_prescription (str, optional): Name of prescription. Current option are ['circuit']. Defaults
                to 'circuit'.
        """
        noise_params_model = NoiseModelParameters_UniformDepolarizing(
            **noise_parameter_dictionary
        )

        params_dict = {
            field: getattr(noise_params_model, field)
            for field in noise_params_model.model_fields
        }

        return cls(**params_dict, noise_channel_prescription=noise_channel_prescription)

    def calculate_stabilization_time(self, unit="μs"):
        """Calculate the stabilization time.

        Args:
            unit (str): An acceptable unit of time.

        Returns:
            Quantity: stabilization time.
        """
        stabilization_time = Quantity.from_raw_value(
            raw_value=float(self.input_noise_parameters.stabilization_time), unit=unit
        )

        return stabilization_time
