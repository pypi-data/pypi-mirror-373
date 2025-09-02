import dataclasses

from ..components.attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.locations import Locations_V1_0_1
from ..components.planar_data import PlanarData_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_0_1_Locations(Locations_V1_0_1, PlanarData_V1_0_1, AttributeListProperty_V1_0_1):
    """The structural planar data and attributes."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        PlanarData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A set of structural planar data points and their associated attributes."""

    SCHEMA_ID = "/objects/planar-data-pointset/1.0.1/planar-data-pointset.schema.json"

    locations: PlanarDataPointset_V1_0_1_Locations
    """The structural planar data and attributes."""
    schema: str = "/objects/planar-data-pointset/1.0.1/planar-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, PlanarDataPointset_V1_0_1_Locations):
            raise ValidationFailed("self.locations is not PlanarDataPointset_V1_0_1_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/planar-data-pointset/1.0.1/planar-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/planar-data-pointset/1.0.1/planar-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_1_0_Locations(Locations_V1_0_1, PlanarData_V1_0_1, AttributeListProperty_V1_1_0):
    """The structural planar data and attributes."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        PlanarData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A set of structural planar data points and their associated attributes."""

    SCHEMA_ID = "/objects/planar-data-pointset/1.1.0/planar-data-pointset.schema.json"

    locations: PlanarDataPointset_V1_1_0_Locations
    """The structural planar data and attributes."""
    schema: str = "/objects/planar-data-pointset/1.1.0/planar-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, PlanarDataPointset_V1_1_0_Locations):
            raise ValidationFailed("self.locations is not PlanarDataPointset_V1_1_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/planar-data-pointset/1.1.0/planar-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/planar-data-pointset/1.1.0/planar-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_2_0_Locations(Locations_V1_0_1, PlanarData_V1_0_1, AttributeListProperty_V1_2_0):
    """The structural planar data and attributes."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        PlanarData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """A set of structural planar data points and their associated attributes."""

    SCHEMA_ID = "/objects/planar-data-pointset/1.2.0/planar-data-pointset.schema.json"

    locations: PlanarDataPointset_V1_2_0_Locations
    """The structural planar data and attributes."""
    schema: str = "/objects/planar-data-pointset/1.2.0/planar-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, PlanarDataPointset_V1_2_0_Locations):
            raise ValidationFailed("self.locations is not PlanarDataPointset_V1_2_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/planar-data-pointset/1.2.0/planar-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/planar-data-pointset/1.2.0/planar-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_3_0_Locations(Locations_V1_0_1, PlanarData_V1_0_1, AttributeListProperty_V1_2_0):
    """The structural planar data and attributes."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        PlanarData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class PlanarDataPointset_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """A set of structural planar data points and their associated attributes."""

    SCHEMA_ID = "/objects/planar-data-pointset/1.3.0/planar-data-pointset.schema.json"

    locations: PlanarDataPointset_V1_3_0_Locations
    """The structural planar data and attributes."""
    schema: str = "/objects/planar-data-pointset/1.3.0/planar-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.locations, PlanarDataPointset_V1_3_0_Locations):
            raise ValidationFailed("self.locations is not PlanarDataPointset_V1_3_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/planar-data-pointset/1.3.0/planar-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/planar-data-pointset/1.3.0/planar-data-pointset.schema.json" failed'
            )
