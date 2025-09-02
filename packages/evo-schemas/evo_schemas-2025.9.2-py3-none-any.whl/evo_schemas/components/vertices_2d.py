import dataclasses

from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Vertices2D_V1_0_1(Serialiser):
    """This component describes 2D vertices."""

    SCHEMA_ID = "/components/vertices-2d/1.0.1/vertices-2d.schema.json"

    vertices: FloatArray2_V1_0_1
    """Vertex coordinate in 2D space. Columns: x, y."""

    def __post_init__(self):
        if not isinstance(self.vertices, FloatArray2_V1_0_1):
            raise ValidationFailed("self.vertices is not FloatArray2_V1_0_1")
