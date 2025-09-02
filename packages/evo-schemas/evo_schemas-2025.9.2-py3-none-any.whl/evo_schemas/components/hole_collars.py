import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import ValidationFailed
from .attribute_list_property import AttributeListProperty_V1_2_0
from .hole_chunks import HoleChunks_V1_0_0
from .locations import Locations_V1_0_1


@dataclasses.dataclass(kw_only=True)
class HoleCollars_V1_0_0(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """Hole collars represent the surface locations where drillholes begin. Contains the 3D coordinates (x, y, z), depth information, hole indices, and attributes for the collars of drillholes."""

    SCHEMA_ID = "/components/hole-collars/1.0.0/hole-collars.schema.json"

    distances: FloatArray3_V1_0_1
    """The depth values for each drillhole. Columns: final, target, current."""
    holes: HoleChunks_V1_0_0
    """The data describing the hole paths."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.distances, FloatArray3_V1_0_1):
            raise ValidationFailed("self.distances is not FloatArray3_V1_0_1")
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")
