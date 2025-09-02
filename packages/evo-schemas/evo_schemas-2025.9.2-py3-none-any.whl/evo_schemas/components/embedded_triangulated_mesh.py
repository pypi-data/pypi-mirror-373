import dataclasses

from ..elements.index_array_1 import IndexArray1_V1_0_1
from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import AttributeListProperty_V1_1_0, AttributeListProperty_V1_2_0
from .mesh_quality import MeshQuality_V1_0_1
from .triangles import Triangles_V1_0_1, Triangles_V1_1_0, Triangles_V1_2_0


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V2_1_0_Parts(AttributeListProperty_V1_2_0):
    """A structure defining chunks the mesh is composed of."""

    chunks: IndexArray2_V1_0_1
    """A tuple defining the first index and the length of a chunk.
     
    If triangle_indices is defined, the chunk refers to a segment of the triangle_indices array.
    Otherwise, the chunk refers to a segment of the triangles array.
    Chunks do not have to include all triangles, and chunks can overlap.
    Columns: offset, count
    """
    triangle_indices: IndexArray1_V1_0_1 | None = None
    """An optional index array into the triangle indices set.
     
    This is used to define chunks if the mesh triangle indices do not contain contiguous chunks.
    """

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")
        if self.triangle_indices is not None:
            if not isinstance(self.triangle_indices, IndexArray1_V1_0_1):
                raise ValidationFailed("self.triangle_indices is not IndexArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V2_1_0(Serialiser):
    """A mesh composed of triangles.

    The triangles are defined by triplets of indices into a vertex list.
    Optionally, parts can be defined.
    """

    SCHEMA_ID = "/components/embedded-triangulated-mesh/2.1.0/embedded-triangulated-mesh.schema.json"

    triangles: Triangles_V1_2_0
    """The vertices and triangle indices of the mesh."""
    parts: EmbeddedTriangulatedMesh_V2_1_0_Parts | None = None
    """A structure defining triangle chunks the mesh is composed of."""

    def __post_init__(self):
        if not isinstance(self.triangles, Triangles_V1_2_0):
            raise ValidationFailed("self.triangles is not Triangles_V1_2_0")
        if self.parts is not None:
            if not isinstance(self.parts, EmbeddedTriangulatedMesh_V2_1_0_Parts):
                raise ValidationFailed("self.parts is not EmbeddedTriangulatedMesh_V2_1_0_Parts")


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V2_0_0_Parts(AttributeListProperty_V1_1_0):
    """A structure defining chunks the mesh is composed of."""

    chunks: IndexArray2_V1_0_1
    """A tuple defining the first index and the length of a chunk.
     
    If triangle_indices is defined, the chunk refers to a segment of the triangle_indices array.
    Otherwise, the chunk refers to a segment of the triangles array.
    Chunks do not have to include all triangles, and chunks can overlap.
    Columns: offset, count
    """
    triangle_indices: IndexArray1_V1_0_1 | None = None
    """An optional index array into the triangle indices set.
     
    This is used to define chunks if the mesh triangle indices do not contain contiguous chunks.
    """

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")
        if self.triangle_indices is not None:
            if not isinstance(self.triangle_indices, IndexArray1_V1_0_1):
                raise ValidationFailed("self.triangle_indices is not IndexArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V2_0_0(Serialiser):
    """A mesh composed of triangles.

    The triangles are defined by triplets of indices into a vertex list.
    Optionally, parts can be defined.
    """

    SCHEMA_ID = "/components/embedded-triangulated-mesh/2.0.0/embedded-triangulated-mesh.schema.json"

    triangles: Triangles_V1_1_0
    """The vertices and triangle indices of the mesh."""
    parts: EmbeddedTriangulatedMesh_V2_0_0_Parts | None = None
    """A structure defining triangle chunks the mesh is composed of."""

    def __post_init__(self):
        if not isinstance(self.triangles, Triangles_V1_1_0):
            raise ValidationFailed("self.triangles is not Triangles_V1_1_0")
        if self.parts is not None:
            if not isinstance(self.parts, EmbeddedTriangulatedMesh_V2_0_0_Parts):
                raise ValidationFailed("self.parts is not EmbeddedTriangulatedMesh_V2_0_0_Parts")


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V1_0_1(Triangles_V1_0_1):
    """A mesh made up of triangles, which is part of an object."""

    SCHEMA_ID = "/components/embedded-triangulated-mesh/1.0.1/embedded-triangulated-mesh.schema.json"

    kind: str
    """The kind of mesh."""
    name: str
    """Name of the object."""
    feature: str
    """Kind of feature."""
    quality: MeshQuality_V1_0_1 | None = None
    """Mesh quality."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        Triangles_V1_0_1.__post_init__(self)
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in ("Open", "Closed"):
            raise ValidationFailed('self.kind in ("Open", "Closed") failed')
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Void",
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "OutputVolume",
            "StratigraphicContactSurface",
            "Vein",
            "VeinSystem",
        ):
            raise ValidationFailed(
                'self.feature in ("Void", "Fault", "ContactSurface", "Topography", "BoundarySurface", "OutputVolume", "StratigraphicContactSurface", "Vein", "VeinSystem") failed'
            )
        if self.quality is not None:
            if not isinstance(self.quality, MeshQuality_V1_0_1):
                raise ValidationFailed("self.quality is not MeshQuality_V1_0_1")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class EmbeddedTriangulatedMesh_V1_1_0(Triangles_V1_1_0):
    """A mesh made up of triangles, which is part of an object."""

    SCHEMA_ID = "/components/embedded-triangulated-mesh/1.1.0/embedded-triangulated-mesh.schema.json"

    kind: str
    """The kind of mesh."""
    name: str
    """Name of the object."""
    feature: str
    """Kind of feature."""
    quality: MeshQuality_V1_0_1 | None = None
    """Mesh quality."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        Triangles_V1_1_0.__post_init__(self)
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in ("Open", "Closed"):
            raise ValidationFailed('self.kind in ("Open", "Closed") failed')
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Void",
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "OutputVolume",
            "StratigraphicContactSurface",
            "Vein",
            "VeinSystem",
        ):
            raise ValidationFailed(
                'self.feature in ("Void", "Fault", "ContactSurface", "Topography", "BoundarySurface", "OutputVolume", "StratigraphicContactSurface", "Vein", "VeinSystem") failed'
            )
        if self.quality is not None:
            if not isinstance(self.quality, MeshQuality_V1_0_1):
                raise ValidationFailed("self.quality is not MeshQuality_V1_0_1")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")
