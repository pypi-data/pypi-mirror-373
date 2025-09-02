import dataclasses

from .integer_array_md import IntegerArrayMd_V1_0_1
from .serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class IntegerArray1_V1_0_1(IntegerArrayMd_V1_0_1):
    """Array of integers."""

    SCHEMA_ID = "/elements/integer-array-1/1.0.1/integer-array-1.schema.json"

    width: int = 1
    """number of columns"""

    def __post_init__(self):
        IntegerArrayMd_V1_0_1.__post_init__(self)
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 1:
            raise ValidationFailed("self.width == 1 failed")
