import dataclasses

from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Coordinates3D_V1_0_0(Serialiser):
    """3D Coordinates"""

    SCHEMA_ID = "/elements/coordinates-3d/1.0.0/coordinates-3d.schema.json"

    x: float
    """x-coordinate position."""
    y: float
    """y-coordinate position."""
    z: float
    """z-coordinate position."""

    def __post_init__(self):
        if not isinstance(self.x, float):
            raise ValidationFailed("self.x is not float")
        if not isinstance(self.y, float):
            raise ValidationFailed("self.y is not float")
        if not isinstance(self.z, float):
            raise ValidationFailed("self.z is not float")
