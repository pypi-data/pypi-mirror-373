import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.string_array import StringArray_V1_0_1
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class StringAttribute_V1_0_1(Serialiser):
    """List of attributes that are just strings."""

    SCHEMA_ID = "/components/string-attribute/1.0.1/string-attribute.schema.json"

    name: str
    """The name of the attribute."""
    values: StringArray_V1_0_1
    """List of strings. One per item."""
    attribute_type: str = "string"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, StringArray_V1_0_1):
            raise ValidationFailed("self.values is not StringArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "string":
            raise ValidationFailed('self.attribute_type == "string" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class StringAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """List of attributes that are just strings."""

    SCHEMA_ID = "/components/string-attribute/1.1.0/string-attribute.schema.json"

    values: StringArray_V1_0_1
    """List of strings. One per item."""
    attribute_type: str = "string"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, StringArray_V1_0_1):
            raise ValidationFailed("self.values is not StringArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "string":
            raise ValidationFailed('self.attribute_type == "string" failed')
