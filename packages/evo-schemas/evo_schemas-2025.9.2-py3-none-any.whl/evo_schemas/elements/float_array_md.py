import dataclasses

from .binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FloatArrayMd_V1_0_1(Serialiser):
    """Multi dimensional array of floats."""

    SCHEMA_ID = "/elements/float-array-md/1.0.1/float-array-md.schema.json"

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int
    """number of columns"""
    data_type: str = "float64"
    """data type"""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "float64":
            raise ValidationFailed('self.data_type == "float64" failed')
