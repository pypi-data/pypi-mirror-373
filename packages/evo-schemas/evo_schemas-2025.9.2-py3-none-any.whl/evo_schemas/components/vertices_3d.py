import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Vertices3D_V1_0_1(Serialiser):
    """This component describes 3D vertices."""

    SCHEMA_ID = "/components/vertices-3d/1.0.1/vertices-3d.schema.json"

    vertices: FloatArray3_V1_0_1
    """Vertex coordinate in 3D space. Columns: x, y, z."""

    def __post_init__(self):
        if not isinstance(self.vertices, FloatArray3_V1_0_1):
            raise ValidationFailed("self.vertices is not FloatArray3_V1_0_1")
