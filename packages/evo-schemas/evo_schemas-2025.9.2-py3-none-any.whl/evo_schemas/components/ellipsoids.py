import dataclasses

from ..elements.float_array_6 import FloatArray6_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Ellipsoids_V1_0_1(Serialiser):
    """Ellipsoids specification"""

    SCHEMA_ID = "/components/ellipsoids/1.0.1/ellipsoids.schema.json"

    values: FloatArray6_V1_0_1
    """Array of ellipsoids. Columns: dip_azimuth, dip, pitch, major, semi_major, minor."""

    def __post_init__(self):
        if not isinstance(self.values, FloatArray6_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray6_V1_0_1")
