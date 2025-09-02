import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class NanContinuous_V1_0_1(Serialiser):
    """Values used to designate not-a-number (NaN) for floating point values. Can be used for error codes."""

    SCHEMA_ID = "/components/nan-continuous/1.0.1/nan-continuous.schema.json"

    values: list[float]
    """An array of floating point values that represent not-a-number (NaN). IEEE-754 NaN is always considered NaN and should not be specified."""

    def __post_init__(self):
        if not isinstance(self.values, list):
            raise ValidationFailed("self.values is not a list")
        for v in self.values:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
