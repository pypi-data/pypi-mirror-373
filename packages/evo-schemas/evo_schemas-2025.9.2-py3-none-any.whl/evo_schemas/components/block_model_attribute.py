import dataclasses
import uuid

from ..elements.serialiser import ValidationFailed
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class BlockModelAttribute_V1_0_0(BaseContinuousAttribute_V1_0_0):
    """A block model attribute."""

    SCHEMA_ID = "/components/block-model-attribute/1.0.0/block-model-attribute.schema.json"

    attribute_type: str
    """The data type of the attribute as stored in the Block Model Service."""
    block_model_column_uuid: uuid.UUID
    """The unique ID of the attribute on the block model."""

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if self.attribute_type not in (
            "Int8",
            "Int16",
            "Int32",
            "Int64",
            "UInt8",
            "UInt16",
            "UInt32",
            "UInt64",
            "Float16",
            "Float32",
            "Float64",
            "Date32",
            "Timestamp",
        ):
            raise ValidationFailed(
                'self.attribute_type in ("Int8", "Int16", "Int32", "Int64", "UInt8", "UInt16", "UInt32", "UInt64", "Float16", "Float32", "Float64", "Date32", "Timestamp") failed'
            )
        if not isinstance(self.block_model_column_uuid, uuid.UUID):
            raise ValidationFailed("self.block_model_column_uuid is not uuid.UUID")
