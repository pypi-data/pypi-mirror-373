import dataclasses

from .binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ColorArray_V1_0_1(Serialiser):
    """Array of RGBA colors. The channels are arranged in memory in such manner that a single 32-bit unsigned integer has the alpha sample in the highest 8 bits, followed by the blue sample, green sample and finally the red sample in the lowest 8 bits."""

    SCHEMA_ID = "/elements/color-array/1.0.1/color-array.schema.json"

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    data_type: str = "uint32"
    """data type"""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "uint32":
            raise ValidationFailed('self.data_type == "uint32" failed')
