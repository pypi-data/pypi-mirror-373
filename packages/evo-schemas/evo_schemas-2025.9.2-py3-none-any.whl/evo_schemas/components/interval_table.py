import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from .from_to import FromTo_V1_0_1


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_2_0_FromTo(FromTo_V1_0_1, AttributeListProperty_V1_2_0):
    """The from-to of the intervals."""

    def __post_init__(self):
        FromTo_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_2_0(Serialiser):
    """An interval table."""

    SCHEMA_ID = "/components/interval-table/1.2.0/interval-table.schema.json"

    name: str
    """The name of the table."""
    from_to: IntervalTable_V1_2_0_FromTo
    """The from-to of the intervals."""
    collection_type: str = "interval"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.from_to, IntervalTable_V1_2_0_FromTo):
            raise ValidationFailed("self.from_to is not IntervalTable_V1_2_0_FromTo")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "interval":
            raise ValidationFailed('self.collection_type == "interval" failed')


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_0_1_FromTo(FromTo_V1_0_1, AttributeListProperty_V1_0_1):
    """The from-to of the intervals."""

    def __post_init__(self):
        FromTo_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_0_1(Serialiser):
    """An interval table."""

    SCHEMA_ID = "/components/interval-table/1.0.1/interval-table.schema.json"

    name: str
    """The name of the table."""
    from_to: IntervalTable_V1_0_1_FromTo
    """The from-to of the intervals."""
    collection_type: str = "interval"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.from_to, IntervalTable_V1_0_1_FromTo):
            raise ValidationFailed("self.from_to is not IntervalTable_V1_0_1_FromTo")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "interval":
            raise ValidationFailed('self.collection_type == "interval" failed')


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_1_0_FromTo(FromTo_V1_0_1, AttributeListProperty_V1_1_0):
    """The from-to of the intervals."""

    def __post_init__(self):
        FromTo_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class IntervalTable_V1_1_0(Serialiser):
    """An interval table."""

    SCHEMA_ID = "/components/interval-table/1.1.0/interval-table.schema.json"

    name: str
    """The name of the table."""
    from_to: IntervalTable_V1_1_0_FromTo
    """The from-to of the intervals."""
    collection_type: str = "interval"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.from_to, IntervalTable_V1_1_0_FromTo):
            raise ValidationFailed("self.from_to is not IntervalTable_V1_1_0_FromTo")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "interval":
            raise ValidationFailed('self.collection_type == "interval" failed')
