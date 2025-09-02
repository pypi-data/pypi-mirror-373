import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .one_of_attribute import (
    OneOfAttribute_V1_0_1,
    OneOfAttribute_V1_0_1_Item,
    OneOfAttribute_V1_1_0,
    OneOfAttribute_V1_1_0_Item,
    OneOfAttribute_V1_2_0,
    OneOfAttribute_V1_2_0_Item,
)


@dataclasses.dataclass(kw_only=True)
class AttributeListProperty_V1_2_0(Serialiser):
    """A component describing the list of attributes that can be used."""

    SCHEMA_ID = "/components/attribute-list-property/1.2.0/attribute-list-property.schema.json"

    attributes: OneOfAttribute_V1_2_0 | None = None
    """Attribute data."""

    def __post_init__(self):
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class AttributeListProperty_V1_0_1(Serialiser):
    """A component describing the list of attributes that can be used."""

    SCHEMA_ID = "/components/attribute-list-property/1.0.1/attribute-list-property.schema.json"

    attributes: OneOfAttribute_V1_0_1 | None = None
    """Attribute data."""

    def __post_init__(self):
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_0_1_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_0_1_Item")


@dataclasses.dataclass(kw_only=True)
class AttributeListProperty_V1_1_0(Serialiser):
    """A component describing the list of attributes that can be used."""

    SCHEMA_ID = "/components/attribute-list-property/1.1.0/attribute-list-property.schema.json"

    attributes: OneOfAttribute_V1_1_0 | None = None
    """Attribute data."""

    def __post_init__(self):
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_1_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_1_0_Item")
