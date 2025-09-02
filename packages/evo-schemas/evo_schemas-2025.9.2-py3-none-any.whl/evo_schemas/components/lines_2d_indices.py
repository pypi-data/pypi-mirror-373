import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Lines2DIndices_V1_0_1_Indices(Serialiser):
    """Array of lines. Columns: start, end, arcCenter. Start/End are 0-based indices into the vertices"""

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "uint64/uint64/float64"
    """Data type for the columns. 1st column is of type uint64, 2nd is uint64 and 3rd is float64."""

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
        if not self.data_type == "uint64/uint64/float64":
            raise ValidationFailed('self.data_type == "uint64/uint64/float64" failed')


@dataclasses.dataclass(kw_only=True)
class Lines2DIndices_V1_0_1(Serialiser):
    """This component describes line endpoints for 2D lines. It has three columns (start, end, arcCenter). Start/end are indices into vertices_2D for the line endpoint. ArcCenter is the counter-clockwise signed distance from the line center to the arc edge."""

    SCHEMA_ID = "/components/lines-2d-indices/1.0.1/lines-2d-indices.schema.json"

    indices: Lines2DIndices_V1_0_1_Indices
    """Array of lines. Columns: start, end, arcCenter. Start/End are 0-based indices into the vertices"""

    def __post_init__(self):
        if not isinstance(self.indices, Lines2DIndices_V1_0_1_Indices):
            raise ValidationFailed("self.indices is not Lines2DIndices_V1_0_1_Indices")
