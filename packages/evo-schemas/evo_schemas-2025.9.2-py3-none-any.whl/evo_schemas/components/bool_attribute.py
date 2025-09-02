import dataclasses

from ..elements.bool_array_1 import BoolArray1_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .base_category_attribute import BaseCategoryAttribute_V1_0_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1


@dataclasses.dataclass(kw_only=True)
class BoolAttribute_V1_0_1(Serialiser):
    """An attribute for boolean values."""

    SCHEMA_ID = "/components/bool-attribute/1.0.1/bool-attribute.schema.json"

    name: str
    """The name of the attribute"""
    values: BoolArray1_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "bool"
    """Type of the attribute."""
    attribute_description: CategoryAttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, BoolArray1_V1_0_1):
            raise ValidationFailed("self.values is not BoolArray1_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "bool":
            raise ValidationFailed('self.attribute_type == "bool" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, CategoryAttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not CategoryAttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class BoolAttribute_V1_1_0(BaseCategoryAttribute_V1_0_0):
    """An attribute for boolean values."""

    SCHEMA_ID = "/components/bool-attribute/1.1.0/bool-attribute.schema.json"

    values: BoolArray1_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "bool"

    def __post_init__(self):
        BaseCategoryAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, BoolArray1_V1_0_1):
            raise ValidationFailed("self.values is not BoolArray1_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "bool":
            raise ValidationFailed('self.attribute_type == "bool" failed')
