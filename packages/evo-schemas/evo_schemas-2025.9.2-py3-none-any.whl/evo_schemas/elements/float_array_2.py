import dataclasses

from .float_array_md import FloatArrayMd_V1_0_1
from .serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FloatArray2_V1_0_1(FloatArrayMd_V1_0_1):
    """Array of 2 floats."""

    SCHEMA_ID = "/elements/float-array-2/1.0.1/float-array-2.schema.json"

    width: int = 2
    """number of columns"""

    def __post_init__(self):
        FloatArrayMd_V1_0_1.__post_init__(self)
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 2:
            raise ValidationFailed("self.width == 2 failed")
