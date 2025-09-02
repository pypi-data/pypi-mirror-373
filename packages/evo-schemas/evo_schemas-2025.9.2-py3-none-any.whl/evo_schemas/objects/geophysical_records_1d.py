import dataclasses

from ..components.attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.category_data import CategoryData_V1_0_1
from ..components.lengths import Lengths_V1_0_1
from ..components.locations import Locations_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1_Locations(Locations_V1_0_1, AttributeListProperty_V1_0_1):
    """Array of locations."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1_Depths(Lengths_V1_0_1, AttributeListProperty_V1_0_1):
    """Array of depths."""

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records."""

    SCHEMA_ID = "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_0_1_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_0_1_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_0_1_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_0_1_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_0_1_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_0_1_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_1_0):
    """Array of locations."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_1_0):
    """Array of depths."""

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records."""

    SCHEMA_ID = "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_1_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_1_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_1_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_1_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_1_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_1_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of locations."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of depths."""

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records."""

    SCHEMA_ID = "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_2_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_2_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_2_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_2_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_2_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_2_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of locations."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of depths."""

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """1D geophysical records."""

    SCHEMA_ID = "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_3_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_3_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_3_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_3_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_3_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_3_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")
