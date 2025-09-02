import dataclasses

from ..elements.float_array_1 import FloatArray1_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_2_0_Distance(AttributeListProperty_V1_2_0):
    """The distance down the drillhole."""

    values: FloatArray1_V1_0_1
    """The distance down the drillhole."""
    unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Unit"""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.values, FloatArray1_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray1_V1_0_1")
        if self.unit is not None:
            if not isinstance(self.unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.unit is not UnitLength_V1_0_1_UnitCategories")


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_2_0(Serialiser):
    """A table of lineation data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-lineation-data-table/1.2.0/relative-lineation-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativeLineationDataTable_V1_2_0_Distance
    """The distance down the drillhole."""
    relative_lineation_angles: FloatArray3_V1_0_1
    """Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma"""
    collection_type: str = "lineation"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativeLineationDataTable_V1_2_0_Distance):
            raise ValidationFailed("self.distance is not RelativeLineationDataTable_V1_2_0_Distance")
        if not isinstance(self.relative_lineation_angles, FloatArray3_V1_0_1):
            raise ValidationFailed("self.relative_lineation_angles is not FloatArray3_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "lineation":
            raise ValidationFailed('self.collection_type == "lineation" failed')


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_0_1_Distance(AttributeListProperty_V1_0_1):
    """The distance down the drillhole."""

    values: FloatArray1_V1_0_1
    """The distance down the drillhole."""
    unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Unit"""

    def __post_init__(self):
        AttributeListProperty_V1_0_1.__post_init__(self)
        if not isinstance(self.values, FloatArray1_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray1_V1_0_1")
        if self.unit is not None:
            if not isinstance(self.unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.unit is not UnitLength_V1_0_1_UnitCategories")


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_0_1(Serialiser):
    """A table of lineation data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-lineation-data-table/1.0.1/relative-lineation-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativeLineationDataTable_V1_0_1_Distance
    """The distance down the drillhole."""
    relative_lineation_angles: FloatArray3_V1_0_1
    """Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma"""
    collection_type: str = "lineation"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativeLineationDataTable_V1_0_1_Distance):
            raise ValidationFailed("self.distance is not RelativeLineationDataTable_V1_0_1_Distance")
        if not isinstance(self.relative_lineation_angles, FloatArray3_V1_0_1):
            raise ValidationFailed("self.relative_lineation_angles is not FloatArray3_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "lineation":
            raise ValidationFailed('self.collection_type == "lineation" failed')


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_1_0_Distance(AttributeListProperty_V1_1_0):
    """The distance down the drillhole."""

    values: FloatArray1_V1_0_1
    """The distance down the drillhole."""
    unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Unit"""

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.values, FloatArray1_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray1_V1_0_1")
        if self.unit is not None:
            if not isinstance(self.unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.unit is not UnitLength_V1_0_1_UnitCategories")


@dataclasses.dataclass(kw_only=True)
class RelativeLineationDataTable_V1_1_0(Serialiser):
    """A table of lineation data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-lineation-data-table/1.1.0/relative-lineation-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativeLineationDataTable_V1_1_0_Distance
    """The distance down the drillhole."""
    relative_lineation_angles: FloatArray3_V1_0_1
    """Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma"""
    collection_type: str = "lineation"
    """The type of the collection."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativeLineationDataTable_V1_1_0_Distance):
            raise ValidationFailed("self.distance is not RelativeLineationDataTable_V1_1_0_Distance")
        if not isinstance(self.relative_lineation_angles, FloatArray3_V1_0_1):
            raise ValidationFailed("self.relative_lineation_angles is not FloatArray3_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "lineation":
            raise ValidationFailed('self.collection_type == "lineation" failed')
