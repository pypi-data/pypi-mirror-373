import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class BaseAttribute_V1_0_0(Serialiser):
    """A base schema for attributes."""

    SCHEMA_ID = "/components/base-attribute/1.0.0/base-attribute.schema.json"

    name: str
    """The name of the attribute"""
    key: str
    """An identifier of the attribute, used to keep track of the attribute when it is renamed.
     
    The identifier must be unique within an attribute list.
    """
    attribute_type: str
    """Type of the attribute."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
