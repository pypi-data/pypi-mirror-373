import dataclasses

from ..elements.color_array import ColorArray_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class ColorAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """An attribute for color values."""

    SCHEMA_ID = "/components/color-attribute/1.1.0/color-attribute.schema.json"

    values: ColorArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "color"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, ColorArray_V1_0_1):
            raise ValidationFailed("self.values is not ColorArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "color":
            raise ValidationFailed('self.attribute_type == "color" failed')


@dataclasses.dataclass(kw_only=True)
class ColorAttribute_V1_0_0(Serialiser):
    """An attribute for color values."""

    SCHEMA_ID = "/components/color-attribute/1.0.0/color-attribute.schema.json"

    name: str
    """The name of the attribute."""
    values: ColorArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "color"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, ColorArray_V1_0_1):
            raise ValidationFailed("self.values is not ColorArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "color":
            raise ValidationFailed('self.attribute_type == "color" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
