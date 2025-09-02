import dataclasses

from ..elements.bool_array_1 import BoolArray1_V1_0_1
from ..elements.float_array_1 import FloatArray1_V1_0_1
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class RelativePlanarDataTable_V1_2_0_Distance(AttributeListProperty_V1_2_0):
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
class RelativePlanarDataTable_V1_2_0(Serialiser):
    """A table of planar data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-planar-data-table/1.2.0/relative-planar-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativePlanarDataTable_V1_2_0_Distance
    """The distance down the drillhole."""
    relative_plane_angles: FloatArray2_V1_0_1
    """Planar measurements relative to the drillhole. Columns: alpha, beta"""
    collection_type: str = "planar"
    """The type of the collection."""
    plane_polarity: BoolArray1_V1_0_1 | None = None
    """Polarity of the planar measurements. Column: has_positive_polarity"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativePlanarDataTable_V1_2_0_Distance):
            raise ValidationFailed("self.distance is not RelativePlanarDataTable_V1_2_0_Distance")
        if not isinstance(self.relative_plane_angles, FloatArray2_V1_0_1):
            raise ValidationFailed("self.relative_plane_angles is not FloatArray2_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "planar":
            raise ValidationFailed('self.collection_type == "planar" failed')
        if self.plane_polarity is not None:
            if not isinstance(self.plane_polarity, BoolArray1_V1_0_1):
                raise ValidationFailed("self.plane_polarity is not BoolArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class RelativePlanarDataTable_V1_0_1_Distance(AttributeListProperty_V1_0_1):
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
class RelativePlanarDataTable_V1_0_1(Serialiser):
    """A table of planar data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-planar-data-table/1.0.1/relative-planar-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativePlanarDataTable_V1_0_1_Distance
    """The distance down the drillhole."""
    relative_plane_angles: FloatArray2_V1_0_1
    """Planar measurements relative to the drillhole. Columns: alpha, beta"""
    collection_type: str = "planar"
    """The type of the collection."""
    plane_polarity: BoolArray1_V1_0_1 | None = None
    """Polarity of the planar measurements. Column: has_positive_polarity"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativePlanarDataTable_V1_0_1_Distance):
            raise ValidationFailed("self.distance is not RelativePlanarDataTable_V1_0_1_Distance")
        if not isinstance(self.relative_plane_angles, FloatArray2_V1_0_1):
            raise ValidationFailed("self.relative_plane_angles is not FloatArray2_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "planar":
            raise ValidationFailed('self.collection_type == "planar" failed')
        if self.plane_polarity is not None:
            if not isinstance(self.plane_polarity, BoolArray1_V1_0_1):
                raise ValidationFailed("self.plane_polarity is not BoolArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class RelativePlanarDataTable_V1_1_0_Distance(AttributeListProperty_V1_1_0):
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
class RelativePlanarDataTable_V1_1_0(Serialiser):
    """A table of planar data relative to a drillhole"""

    SCHEMA_ID = "/components/relative-planar-data-table/1.1.0/relative-planar-data-table.schema.json"

    name: str
    """The name of the table."""
    distance: RelativePlanarDataTable_V1_1_0_Distance
    """The distance down the drillhole."""
    relative_plane_angles: FloatArray2_V1_0_1
    """Planar measurements relative to the drillhole. Columns: alpha, beta"""
    collection_type: str = "planar"
    """The type of the collection."""
    plane_polarity: BoolArray1_V1_0_1 | None = None
    """Polarity of the planar measurements. Column: has_positive_polarity"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.distance, RelativePlanarDataTable_V1_1_0_Distance):
            raise ValidationFailed("self.distance is not RelativePlanarDataTable_V1_1_0_Distance")
        if not isinstance(self.relative_plane_angles, FloatArray2_V1_0_1):
            raise ValidationFailed("self.relative_plane_angles is not FloatArray2_V1_0_1")
        if not isinstance(self.collection_type, str):
            raise ValidationFailed("self.collection_type is not str")
        if not self.collection_type == "planar":
            raise ValidationFailed('self.collection_type == "planar" failed')
        if self.plane_polarity is not None:
            if not isinstance(self.plane_polarity, BoolArray1_V1_0_1):
                raise ValidationFailed("self.plane_polarity is not BoolArray1_V1_0_1")
