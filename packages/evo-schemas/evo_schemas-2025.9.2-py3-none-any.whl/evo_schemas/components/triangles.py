import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.index_array_3 import IndexArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_0_1_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_0_1_Indices(IndexArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        IndexArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_0_1(Serialiser):
    """Triangles are made up of vertices and indices."""

    SCHEMA_ID = "/components/triangles/1.0.1/triangles.schema.json"

    vertices: Triangles_V1_0_1_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Triangles_V1_0_1_Indices
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        if not isinstance(self.vertices, Triangles_V1_0_1_Vertices):
            raise ValidationFailed("self.vertices is not Triangles_V1_0_1_Vertices")
        if not isinstance(self.indices, Triangles_V1_0_1_Indices):
            raise ValidationFailed("self.indices is not Triangles_V1_0_1_Indices")


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_2_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_2_0_Indices(IndexArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        IndexArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_2_0(Serialiser):
    """Triangles are made up of vertices and indices."""

    SCHEMA_ID = "/components/triangles/1.2.0/triangles.schema.json"

    vertices: Triangles_V1_2_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Triangles_V1_2_0_Indices
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        if not isinstance(self.vertices, Triangles_V1_2_0_Vertices):
            raise ValidationFailed("self.vertices is not Triangles_V1_2_0_Vertices")
        if not isinstance(self.indices, Triangles_V1_2_0_Indices):
            raise ValidationFailed("self.indices is not Triangles_V1_2_0_Indices")


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_1_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_1_0_Indices(IndexArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        IndexArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Triangles_V1_1_0(Serialiser):
    """Triangles are made up of vertices and indices."""

    SCHEMA_ID = "/components/triangles/1.1.0/triangles.schema.json"

    vertices: Triangles_V1_1_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Triangles_V1_1_0_Indices
    """0-based indices into the vertices. Each triple is a triangle. Columns: n0, n1, n2."""

    def __post_init__(self):
        if not isinstance(self.vertices, Triangles_V1_1_0_Vertices):
            raise ValidationFailed("self.vertices is not Triangles_V1_1_0_Vertices")
        if not isinstance(self.indices, Triangles_V1_1_0_Indices):
            raise ValidationFailed("self.indices is not Triangles_V1_1_0_Indices")
