import dataclasses

from ..elements.bool_array_1 import BoolArray1_V1_0_1
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class PlanarData_V1_0_1(Serialiser):
    """An extension used to associate planar data with locations."""

    SCHEMA_ID = "/components/planar-data/1.0.1/planar-data.schema.json"

    plane_orientations: FloatArray2_V1_0_1
    """Plane orientation. Columns: dip_azimuth, dip."""
    plane_polarity: BoolArray1_V1_0_1 | None = None
    """Plane polarity. Column: has_positive_polarity."""

    def __post_init__(self):
        if not isinstance(self.plane_orientations, FloatArray2_V1_0_1):
            raise ValidationFailed("self.plane_orientations is not FloatArray2_V1_0_1")
        if self.plane_polarity is not None:
            if not isinstance(self.plane_polarity, BoolArray1_V1_0_1):
                raise ValidationFailed("self.plane_polarity is not BoolArray1_V1_0_1")
