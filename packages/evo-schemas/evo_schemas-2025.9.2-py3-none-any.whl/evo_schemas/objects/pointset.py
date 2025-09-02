import dataclasses

from ..components.attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.locations import Locations_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_0_1_Locations(Locations_V1_0_1, AttributeListProperty_V1_0_1):
    """The points in the pointset."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A set of points in space and their associated attributes."""

    SCHEMA_ID = "/objects/pointset/1.0.1/pointset.schema.json"

    locations: Pointset_V1_0_1_Locations
    """The points in the pointset."""
    schema: str = "/objects/pointset/1.0.1/pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, Pointset_V1_0_1_Locations):
            raise ValidationFailed("self.locations is not Pointset_V1_0_1_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/pointset/1.0.1/pointset.schema.json":
            raise ValidationFailed('self.schema == "/objects/pointset/1.0.1/pointset.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_1_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_1_0):
    """The points in the pointset."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A set of points in space and their associated attributes."""

    SCHEMA_ID = "/objects/pointset/1.1.0/pointset.schema.json"

    locations: Pointset_V1_1_0_Locations
    """The points in the pointset."""
    schema: str = "/objects/pointset/1.1.0/pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, Pointset_V1_1_0_Locations):
            raise ValidationFailed("self.locations is not Pointset_V1_1_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/pointset/1.1.0/pointset.schema.json":
            raise ValidationFailed('self.schema == "/objects/pointset/1.1.0/pointset.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_2_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """The points in the pointset."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """A set of points in space and their associated attributes."""

    SCHEMA_ID = "/objects/pointset/1.2.0/pointset.schema.json"

    locations: Pointset_V1_2_0_Locations
    """The points in the pointset."""
    schema: str = "/objects/pointset/1.2.0/pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, Pointset_V1_2_0_Locations):
            raise ValidationFailed("self.locations is not Pointset_V1_2_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/pointset/1.2.0/pointset.schema.json":
            raise ValidationFailed('self.schema == "/objects/pointset/1.2.0/pointset.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_3_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """The points in the pointset."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Pointset_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """A set of points in space and their associated attributes."""

    SCHEMA_ID = "/objects/pointset/1.3.0/pointset.schema.json"

    locations: Pointset_V1_3_0_Locations
    """The points in the pointset."""
    schema: str = "/objects/pointset/1.3.0/pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.locations, Pointset_V1_3_0_Locations):
            raise ValidationFailed("self.locations is not Pointset_V1_3_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/pointset/1.3.0/pointset.schema.json":
            raise ValidationFailed('self.schema == "/objects/pointset/1.3.0/pointset.schema.json" failed')
