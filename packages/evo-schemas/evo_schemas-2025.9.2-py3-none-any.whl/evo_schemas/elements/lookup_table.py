import dataclasses

from .binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class LookupTable_V1_0_1(Serialiser):
    """Key-value pairs where keys are integers and values are strings."""

    SCHEMA_ID = "/elements/lookup-table/1.0.1/lookup-table.schema.json"

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob. Columns: key, value."""
    length: int = 0
    """Number of key-value pairs."""
    keys_data_type: str
    """Data type for the keys."""
    values_data_type: str = "string"
    """Data type for the values."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.keys_data_type, str):
            raise ValidationFailed("self.keys_data_type is not str")
        if self.keys_data_type not in ("int32", "int64"):
            raise ValidationFailed('self.keys_data_type in ("int32", "int64") failed')
        if not isinstance(self.values_data_type, str):
            raise ValidationFailed("self.values_data_type is not str")
        if not self.values_data_type == "string":
            raise ValidationFailed('self.values_data_type == "string" failed')
