import dataclasses

from ..elements.float_array_1 import FloatArray1_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Lengths_V1_0_1(Serialiser):
    """Array of length values."""

    SCHEMA_ID = "/components/lengths/1.0.1/lengths.schema.json"

    lengths: FloatArray1_V1_0_1
    """Length values."""

    def __post_init__(self):
        if not isinstance(self.lengths, FloatArray1_V1_0_1):
            raise ValidationFailed("self.lengths is not FloatArray1_V1_0_1")
