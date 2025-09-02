import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_0_1_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_0_1_Indices(IndexArray2_V1_0_1, AttributeListProperty_V1_0_1):
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        IndexArray2_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_0_1(Serialiser):
    """Segments are are made up of vertices and indices."""

    SCHEMA_ID = "/components/segments/1.0.1/segments.schema.json"

    vertices: Segments_V1_0_1_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Segments_V1_0_1_Indices
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        if not isinstance(self.vertices, Segments_V1_0_1_Vertices):
            raise ValidationFailed("self.vertices is not Segments_V1_0_1_Vertices")
        if not isinstance(self.indices, Segments_V1_0_1_Indices):
            raise ValidationFailed("self.indices is not Segments_V1_0_1_Indices")


@dataclasses.dataclass(kw_only=True)
class Segments_V1_2_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_2_0_Indices(IndexArray2_V1_0_1, AttributeListProperty_V1_2_0):
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        IndexArray2_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_2_0(Serialiser):
    """Segments are defined by pairs of indices into the vertices list."""

    SCHEMA_ID = "/components/segments/1.2.0/segments.schema.json"

    vertices: Segments_V1_2_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Segments_V1_2_0_Indices
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        if not isinstance(self.vertices, Segments_V1_2_0_Vertices):
            raise ValidationFailed("self.vertices is not Segments_V1_2_0_Vertices")
        if not isinstance(self.indices, Segments_V1_2_0_Indices):
            raise ValidationFailed("self.indices is not Segments_V1_2_0_Indices")


@dataclasses.dataclass(kw_only=True)
class Segments_V1_1_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_1_0_Indices(IndexArray2_V1_0_1, AttributeListProperty_V1_1_0):
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        IndexArray2_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Segments_V1_1_0(Serialiser):
    """Segments are defined by pairs of indices into the vertices list."""

    SCHEMA_ID = "/components/segments/1.1.0/segments.schema.json"

    vertices: Segments_V1_1_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Segments_V1_1_0_Indices
    """0-based indices into the vertices. Each pair is a segment. Columns: n0, n1."""

    def __post_init__(self):
        if not isinstance(self.vertices, Segments_V1_1_0_Vertices):
            raise ValidationFailed("self.vertices is not Segments_V1_1_0_Vertices")
        if not isinstance(self.indices, Segments_V1_1_0_Indices):
            raise ValidationFailed("self.indices is not Segments_V1_1_0_Indices")
