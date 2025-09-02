import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Locations_V1_0_1(Serialiser):
    """Locations are coordinates in 3D space."""

    SCHEMA_ID = "/components/locations/1.0.1/locations.schema.json"

    coordinates: FloatArray3_V1_0_1
    """Coordinates. Columns: x, y, z."""

    def __post_init__(self):
        if not isinstance(self.coordinates, FloatArray3_V1_0_1):
            raise ValidationFailed("self.coordinates is not FloatArray3_V1_0_1")
