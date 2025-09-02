import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class HoleChunks_V1_0_0(Serialiser):
    """Used to indicate which rows of the segment and attribute tables are associated with a specific drillhole. The indices, counts, and offsets into locations and attribute tables of each hole. Columns: hole_index, offset, count."""

    SCHEMA_ID = "/components/hole-chunks/1.0.0/hole-chunks.schema.json"

    data: BinaryBlob_V1_0_1
    """The binary data for the holes. Columns: hole_index, offset, count."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/uint64"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/uint64":
            raise ValidationFailed('self.data_type == "int32/uint64/uint64" failed')
