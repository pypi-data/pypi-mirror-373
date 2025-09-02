import dataclasses

from ..elements.serialiser import ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_attribute import BaseAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class BaseContinuousAttribute_V1_0_0(BaseAttribute_V1_0_0):
    """A base schema for continuous attributes."""

    SCHEMA_ID = "/components/base-continuous-attribute/1.0.0/base-continuous-attribute.schema.json"

    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        BaseAttribute_V1_0_0.__post_init__(self)
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
