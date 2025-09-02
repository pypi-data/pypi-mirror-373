import dataclasses

from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Intervals_V1_0_1(Serialiser):
    """Intervals are a set of ranges between 2 numbers."""

    SCHEMA_ID = "/components/intervals/1.0.1/intervals.schema.json"

    start_and_end: FloatArray2_V1_0_1
    """A set of intervals"""

    def __post_init__(self):
        if not isinstance(self.start_and_end, FloatArray2_V1_0_1):
            raise ValidationFailed("self.start_and_end is not FloatArray2_V1_0_1")
