import dataclasses

from ..elements.index_array_3 import IndexArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .mesh_quality import MeshQuality_V1_0_1


@dataclasses.dataclass(kw_only=True)
class SurfaceMesh_V1_0_1(Serialiser):
    """This component describes a surface mesh."""

    SCHEMA_ID = "/components/surface-mesh/1.0.1/surface-mesh.schema.json"

    kind: str
    """The kind of surface mesh."""
    triangles: IndexArray3_V1_0_1
    """0-based indices. Each triple is a triangle. Columns: i, j, k."""
    quality: MeshQuality_V1_0_1 | None = None
    """Mesh quality."""

    def __post_init__(self):
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in ("Open", "Closed"):
            raise ValidationFailed('self.kind in ("Open", "Closed") failed')
        if not isinstance(self.triangles, IndexArray3_V1_0_1):
            raise ValidationFailed("self.triangles is not IndexArray3_V1_0_1")
        if self.quality is not None:
            if not isinstance(self.quality, MeshQuality_V1_0_1):
                raise ValidationFailed("self.quality is not MeshQuality_V1_0_1")
