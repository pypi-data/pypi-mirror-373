"""The base noise model class."""

from pydantic import BaseModel


class Quantity(BaseModel):
    """A basic quantity with a value and unit."""

    value: float
    unit: str

    _unit_scales: dict[str, float] = {
        "ns": 1e-9,
        "μs": 1e-6,
        "ms": 1e-3,
        "": 1,
    }

    def __repr__(self) -> str:
        return f"Quantity(value={self.value}, unit='{self.unit}')"

    def __float__(self) -> float:
        """Get float version of quantity using self.unit_scales map.

        If `type(x)` is Quantity, then `float(x)` returns the unitless value.

        Returns:
            float:
        """
        return self.value * self._unit_scales[self.unit]

    @classmethod
    def from_raw_value(cls, raw_value: float, unit: str) -> "Quantity":
        return cls(
            value=round(raw_value / cls._unit_scales.default[unit], 3), unit=unit
        )


class NoiseModelParameters(BaseModel):
    """Base class for noise model parameters."""

    pass


class NoiseModel:
    pass
