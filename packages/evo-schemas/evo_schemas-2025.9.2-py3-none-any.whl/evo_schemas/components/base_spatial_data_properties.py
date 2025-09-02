import dataclasses

from ..elements.serialiser import ValidationFailed
from .base_object_properties import BaseObjectProperties_V1_0_1, BaseObjectProperties_V1_1_0
from .bounding_box import BoundingBox_V1_0_1
from .crs import Crs_V1_0_1, is_crs_v1_0_1


@dataclasses.dataclass(kw_only=True)
class BaseSpatialDataProperties_V1_0_1(BaseObjectProperties_V1_0_1):
    """Properties common to all types of Geoscience spatial data such as name, unique identifier, and bounding box"""

    SCHEMA_ID = "/components/base-spatial-data-properties/1.0.1/base-spatial-data-properties.schema.json"

    bounding_box: BoundingBox_V1_0_1
    """Bounding box of the spatial data."""
    coordinate_reference_system: Crs_V1_0_1
    """Coordinate system of the spatial data"""

    def __post_init__(self):
        BaseObjectProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.bounding_box, BoundingBox_V1_0_1):
            raise ValidationFailed("self.bounding_box is not BoundingBox_V1_0_1")
        if not is_crs_v1_0_1(self.coordinate_reference_system):
            raise ValidationFailed("is_crs_v1_0_1(self.coordinate_reference_system) failed")


@dataclasses.dataclass(kw_only=True)
class BaseSpatialDataProperties_V1_1_0(BaseObjectProperties_V1_1_0):
    """Properties common to all types of Geoscience spatial data such as name, unique identifier, and bounding box"""

    SCHEMA_ID = "/components/base-spatial-data-properties/1.1.0/base-spatial-data-properties.schema.json"

    bounding_box: BoundingBox_V1_0_1
    """Bounding box of the spatial data."""
    coordinate_reference_system: Crs_V1_0_1
    """Coordinate system of the spatial data"""

    def __post_init__(self):
        BaseObjectProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.bounding_box, BoundingBox_V1_0_1):
            raise ValidationFailed("self.bounding_box is not BoundingBox_V1_0_1")
        if not is_crs_v1_0_1(self.coordinate_reference_system):
            raise ValidationFailed("is_crs_v1_0_1(self.coordinate_reference_system) failed")
