import dataclasses

from .binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class BoolArray1_V1_0_1(Serialiser):
    """Array of boolean values."""

    SCHEMA_ID = "/elements/bool-array-1/1.0.1/bool-array-1.schema.json"

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    data_type: str = "bool"
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
        if not self.data_type == "bool":
            raise ValidationFailed('self.data_type == "bool" failed')
