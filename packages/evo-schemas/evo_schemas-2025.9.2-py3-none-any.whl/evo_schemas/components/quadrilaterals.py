import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.index_array_4 import IndexArray4_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_0_1_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_0_1_Indices(IndexArray4_V1_0_1, AttributeListProperty_V1_0_1):
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        IndexArray4_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_0_1(Serialiser):
    """This component describes a set of quadrilaterals."""

    SCHEMA_ID = "/components/quadrilaterals/1.0.1/quadrilaterals.schema.json"

    vertices: Quadrilaterals_V1_0_1_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Quadrilaterals_V1_0_1_Indices
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        if not isinstance(self.vertices, Quadrilaterals_V1_0_1_Vertices):
            raise ValidationFailed("self.vertices is not Quadrilaterals_V1_0_1_Vertices")
        if not isinstance(self.indices, Quadrilaterals_V1_0_1_Indices):
            raise ValidationFailed("self.indices is not Quadrilaterals_V1_0_1_Indices")


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_1_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_1_0_Indices(IndexArray4_V1_0_1, AttributeListProperty_V1_1_0):
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        IndexArray4_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_1_0(Serialiser):
    """This component describes a set of quadrilaterals."""

    SCHEMA_ID = "/components/quadrilaterals/1.1.0/quadrilaterals.schema.json"

    vertices: Quadrilaterals_V1_1_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Quadrilaterals_V1_1_0_Indices
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        if not isinstance(self.vertices, Quadrilaterals_V1_1_0_Vertices):
            raise ValidationFailed("self.vertices is not Quadrilaterals_V1_1_0_Vertices")
        if not isinstance(self.indices, Quadrilaterals_V1_1_0_Indices):
            raise ValidationFailed("self.indices is not Quadrilaterals_V1_1_0_Indices")


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_2_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_2_0_Indices(IndexArray4_V1_0_1, AttributeListProperty_V1_2_0):
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        IndexArray4_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class Quadrilaterals_V1_2_0(Serialiser):
    """This component describes a set of quadrilaterals."""

    SCHEMA_ID = "/components/quadrilaterals/1.2.0/quadrilaterals.schema.json"

    vertices: Quadrilaterals_V1_2_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    indices: Quadrilaterals_V1_2_0_Indices
    """0-based indices into the vertices. Each row is a quadrilateral. Columns: n0, n1, n2, n3."""

    def __post_init__(self):
        if not isinstance(self.vertices, Quadrilaterals_V1_2_0_Vertices):
            raise ValidationFailed("self.vertices is not Quadrilaterals_V1_2_0_Vertices")
        if not isinstance(self.indices, Quadrilaterals_V1_2_0_Indices):
            raise ValidationFailed("self.indices is not Quadrilaterals_V1_2_0_Indices")
