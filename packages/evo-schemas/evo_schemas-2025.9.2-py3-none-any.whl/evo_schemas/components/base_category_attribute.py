import dataclasses

from ..elements.serialiser import ValidationFailed
from .base_attribute import BaseAttribute_V1_0_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1


@dataclasses.dataclass(kw_only=True)
class BaseCategoryAttribute_V1_0_0(BaseAttribute_V1_0_0):
    """A base schema for categorial attributes."""

    SCHEMA_ID = "/components/base-category-attribute/1.0.0/base-category-attribute.schema.json"

    attribute_description: CategoryAttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        BaseAttribute_V1_0_0.__post_init__(self)
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, CategoryAttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not CategoryAttributeDescription_V1_0_1")
