import dataclasses

from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Lines3DIndices_V1_0_1(Serialiser):
    """This component describes line endpoints for 3D lines. It has two columns (start,end), which are indices into vertices_3D for the line endpoint. Unlike 2D, curved segments in 3D would use a 2D segment with a transform, or be represented via a BREP"""

    SCHEMA_ID = "/components/lines-3d-indices/1.0.1/lines-3d-indices.schema.json"

    indices: IndexArray2_V1_0_1
    """0-based indices into the vertices. Columns: start, end."""

    def __post_init__(self):
        if not isinstance(self.indices, IndexArray2_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray2_V1_0_1")
