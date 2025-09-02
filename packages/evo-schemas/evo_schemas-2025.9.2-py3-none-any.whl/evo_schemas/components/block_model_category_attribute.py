import dataclasses
import uuid

from ..elements.serialiser import ValidationFailed
from .base_category_attribute import BaseCategoryAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class BlockModelCategoryAttribute_V1_0_0(BaseCategoryAttribute_V1_0_0):
    """A block model category/string attribute stored by the Block Model Service."""

    SCHEMA_ID = "/components/block-model-category-attribute/1.0.0/block-model-category-attribute.schema.json"

    attribute_type: str
    """The data type of the attribute as stored in the Block Model Service."""
    block_model_column_uuid: uuid.UUID
    """The unique ID of the attribute on the block model."""

    def __post_init__(self):
        BaseCategoryAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if self.attribute_type not in ("Boolean", "Utf8"):
            raise ValidationFailed('self.attribute_type in ("Boolean", "Utf8") failed')
        if not isinstance(self.block_model_column_uuid, uuid.UUID):
            raise ValidationFailed("self.block_model_column_uuid is not uuid.UUID")
