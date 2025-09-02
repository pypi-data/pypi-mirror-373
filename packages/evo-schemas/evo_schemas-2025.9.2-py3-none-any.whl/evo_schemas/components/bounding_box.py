import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class BoundingBox_V1_0_1(Serialiser):
    """Defines the geographic bounds of the dataset"""

    SCHEMA_ID = "/components/bounding-box/1.0.1/bounding-box.schema.json"

    min_x: float
    """minimum value on the x-axis"""
    max_x: float
    """maximum value on the x-axis"""
    min_y: float
    """minimum value on the y-axis"""
    max_y: float
    """maximum value on the y-axis"""
    min_z: float
    """minimum value on the z-axis"""
    max_z: float
    """maximum value on the z-axis"""

    def __post_init__(self):
        if not isinstance(self.min_x, float):
            raise ValidationFailed("self.min_x is not float")
        if not isinstance(self.max_x, float):
            raise ValidationFailed("self.max_x is not float")
        if not isinstance(self.min_y, float):
            raise ValidationFailed("self.min_y is not float")
        if not isinstance(self.max_y, float):
            raise ValidationFailed("self.max_y is not float")
        if not isinstance(self.min_z, float):
            raise ValidationFailed("self.min_z is not float")
        if not isinstance(self.max_z, float):
            raise ValidationFailed("self.max_z is not float")
