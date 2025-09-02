import dataclasses

from ..components.attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.category_data import CategoryData_V1_0_1
from ..components.from_to import FromTo_V1_0_1
from ..components.locations import Locations_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class DownholeIntervals_V1_0_1(BaseSpatialDataProperties_V1_0_1, AttributeListProperty_V1_0_1):
    """A description for downhole intervals."""

    SCHEMA_ID = "/objects/downhole-intervals/1.0.1/downhole-intervals.schema.json"

    is_composited: bool
    """Is composited?"""
    start: Locations_V1_0_1
    """Start locations."""
    end: Locations_V1_0_1
    """End locations."""
    mid_points: Locations_V1_0_1
    """Mid-point locations."""
    from_to: FromTo_V1_0_1
    """From-to description."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    schema: str = "/objects/downhole-intervals/1.0.1/downhole-intervals.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)
        if not isinstance(self.is_composited, bool):
            raise ValidationFailed("self.is_composited is not bool")
        if not isinstance(self.start, Locations_V1_0_1):
            raise ValidationFailed("self.start is not Locations_V1_0_1")
        if not isinstance(self.end, Locations_V1_0_1):
            raise ValidationFailed("self.end is not Locations_V1_0_1")
        if not isinstance(self.mid_points, Locations_V1_0_1):
            raise ValidationFailed("self.mid_points is not Locations_V1_0_1")
        if not isinstance(self.from_to, FromTo_V1_0_1):
            raise ValidationFailed("self.from_to is not FromTo_V1_0_1")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-intervals/1.0.1/downhole-intervals.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-intervals/1.0.1/downhole-intervals.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class DownholeIntervals_V1_1_0(BaseSpatialDataProperties_V1_0_1, AttributeListProperty_V1_1_0):
    """A description for downhole intervals."""

    SCHEMA_ID = "/objects/downhole-intervals/1.1.0/downhole-intervals.schema.json"

    is_composited: bool
    """Is composited?"""
    start: Locations_V1_0_1
    """Start locations."""
    end: Locations_V1_0_1
    """End locations."""
    mid_points: Locations_V1_0_1
    """Mid-point locations."""
    from_to: FromTo_V1_0_1
    """From-to description."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    schema: str = "/objects/downhole-intervals/1.1.0/downhole-intervals.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.is_composited, bool):
            raise ValidationFailed("self.is_composited is not bool")
        if not isinstance(self.start, Locations_V1_0_1):
            raise ValidationFailed("self.start is not Locations_V1_0_1")
        if not isinstance(self.end, Locations_V1_0_1):
            raise ValidationFailed("self.end is not Locations_V1_0_1")
        if not isinstance(self.mid_points, Locations_V1_0_1):
            raise ValidationFailed("self.mid_points is not Locations_V1_0_1")
        if not isinstance(self.from_to, FromTo_V1_0_1):
            raise ValidationFailed("self.from_to is not FromTo_V1_0_1")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-intervals/1.1.0/downhole-intervals.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-intervals/1.1.0/downhole-intervals.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class DownholeIntervals_V1_2_0(BaseSpatialDataProperties_V1_0_1, AttributeListProperty_V1_2_0):
    """A description for downhole intervals."""

    SCHEMA_ID = "/objects/downhole-intervals/1.2.0/downhole-intervals.schema.json"

    is_composited: bool
    """Is composited?"""
    start: Locations_V1_0_1
    """Start locations."""
    end: Locations_V1_0_1
    """End locations."""
    mid_points: Locations_V1_0_1
    """Mid-point locations."""
    from_to: FromTo_V1_0_1
    """From-to description."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    schema: str = "/objects/downhole-intervals/1.2.0/downhole-intervals.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.is_composited, bool):
            raise ValidationFailed("self.is_composited is not bool")
        if not isinstance(self.start, Locations_V1_0_1):
            raise ValidationFailed("self.start is not Locations_V1_0_1")
        if not isinstance(self.end, Locations_V1_0_1):
            raise ValidationFailed("self.end is not Locations_V1_0_1")
        if not isinstance(self.mid_points, Locations_V1_0_1):
            raise ValidationFailed("self.mid_points is not Locations_V1_0_1")
        if not isinstance(self.from_to, FromTo_V1_0_1):
            raise ValidationFailed("self.from_to is not FromTo_V1_0_1")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-intervals/1.2.0/downhole-intervals.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-intervals/1.2.0/downhole-intervals.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class DownholeIntervals_V1_3_0(BaseSpatialDataProperties_V1_1_0, AttributeListProperty_V1_2_0):
    """A description for downhole intervals."""

    SCHEMA_ID = "/objects/downhole-intervals/1.3.0/downhole-intervals.schema.json"

    is_composited: bool
    """Is composited?"""
    start: Locations_V1_0_1
    """Start locations."""
    end: Locations_V1_0_1
    """End locations."""
    mid_points: Locations_V1_0_1
    """Mid-point locations."""
    from_to: FromTo_V1_0_1
    """From-to description."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    schema: str = "/objects/downhole-intervals/1.3.0/downhole-intervals.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.is_composited, bool):
            raise ValidationFailed("self.is_composited is not bool")
        if not isinstance(self.start, Locations_V1_0_1):
            raise ValidationFailed("self.start is not Locations_V1_0_1")
        if not isinstance(self.end, Locations_V1_0_1):
            raise ValidationFailed("self.end is not Locations_V1_0_1")
        if not isinstance(self.mid_points, Locations_V1_0_1):
            raise ValidationFailed("self.mid_points is not Locations_V1_0_1")
        if not isinstance(self.from_to, FromTo_V1_0_1):
            raise ValidationFailed("self.from_to is not FromTo_V1_0_1")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-intervals/1.3.0/downhole-intervals.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-intervals/1.3.0/downhole-intervals.schema.json" failed'
            )
