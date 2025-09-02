import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class NanCategorical_V1_0_1(Serialiser):
    """Values used to designate not-a-number (NaN) for integral values. Can be used for error codes."""

    SCHEMA_ID = "/components/nan-categorical/1.0.1/nan-categorical.schema.json"

    values: list[int]
    """An array of integral values that represent not-a-number (NaN)."""

    def __post_init__(self):
        if not isinstance(self.values, list):
            raise ValidationFailed("self.values is not a list")
        for v in self.values:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
