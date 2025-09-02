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
class DataTable_V1_2_0(Serialiser):
    """A table storing extra data."""

    SCHEMA_ID = "/components/data-table/1.2.0/data-table.schema.json"

    name: str
    """The name of the table."""
    collection_type: str = "data"
    """The type of the collection."""
    attributes: OneOfAttribute_V1_2_0 | None = None
    """Attribute data."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "data":
            raise ValidationFailed('self.collection_type == "data" failed')
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class DataTable_V1_0_1(Serialiser):
    """A table storing extra data."""

    SCHEMA_ID = "/components/data-table/1.0.1/data-table.schema.json"

    name: str
    """The name of the table."""
    collection_type: str = "data"
    """The type of the collection."""
    attributes: OneOfAttribute_V1_0_1 | None = None
    """Attribute data."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "data":
            raise ValidationFailed('self.collection_type == "data" failed')
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_0_1_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_0_1_Item")


@dataclasses.dataclass(kw_only=True)
class DataTable_V1_1_0(Serialiser):
    """A table storing extra data."""

    SCHEMA_ID = "/components/data-table/1.1.0/data-table.schema.json"

    name: str
    """The name of the table."""
    collection_type: str = "data"
    """The type of the collection."""
    attributes: OneOfAttribute_V1_1_0 | None = None
    """Attribute data."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "data":
            raise ValidationFailed('self.collection_type == "data" failed')
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, OneOfAttribute_V1_1_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_1_0_Item")
