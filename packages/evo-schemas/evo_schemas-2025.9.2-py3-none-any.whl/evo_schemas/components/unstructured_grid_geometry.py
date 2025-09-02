import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.index_array_1 import IndexArray1_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_0_1_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_0_1_Cells(AttributeListProperty_V1_0_1):
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/int32"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is int32."""

    def __post_init__(self):
        AttributeListProperty_V1_0_1.__post_init__(self)
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/int32":
            raise ValidationFailed('self.data_type == "int32/uint64/int32" failed')


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_0_1(Serialiser):
    """This component describes a set of vertices, indices and cell information."""

    SCHEMA_ID = "/components/unstructured-grid-geometry/1.0.1/unstructured-grid-geometry.schema.json"

    vertices: UnstructuredGridGeometry_V1_0_1_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    cells: UnstructuredGridGeometry_V1_0_1_Cells
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""
    indices: IndexArray1_V1_0_1
    """0-based indices into the vertices."""

    def __post_init__(self):
        if not isinstance(self.vertices, UnstructuredGridGeometry_V1_0_1_Vertices):
            raise ValidationFailed("self.vertices is not UnstructuredGridGeometry_V1_0_1_Vertices")
        if not isinstance(self.cells, UnstructuredGridGeometry_V1_0_1_Cells):
            raise ValidationFailed("self.cells is not UnstructuredGridGeometry_V1_0_1_Cells")
        if not isinstance(self.indices, IndexArray1_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_1_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_1_0_Cells(AttributeListProperty_V1_1_0):
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/int32"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is int32."""

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/int32":
            raise ValidationFailed('self.data_type == "int32/uint64/int32" failed')


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_1_0(Serialiser):
    """This component describes a set of vertices, indices and cell information."""

    SCHEMA_ID = "/components/unstructured-grid-geometry/1.1.0/unstructured-grid-geometry.schema.json"

    vertices: UnstructuredGridGeometry_V1_1_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    cells: UnstructuredGridGeometry_V1_1_0_Cells
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""
    indices: IndexArray1_V1_0_1
    """0-based indices into the vertices."""

    def __post_init__(self):
        if not isinstance(self.vertices, UnstructuredGridGeometry_V1_1_0_Vertices):
            raise ValidationFailed("self.vertices is not UnstructuredGridGeometry_V1_1_0_Vertices")
        if not isinstance(self.cells, UnstructuredGridGeometry_V1_1_0_Cells):
            raise ValidationFailed("self.cells is not UnstructuredGridGeometry_V1_1_0_Cells")
        if not isinstance(self.indices, IndexArray1_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray1_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_2_0_Vertices(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Vertex coordinates. Columns: x, y, z."""

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_2_0_Cells(AttributeListProperty_V1_2_0):
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/int32"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is int32."""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/int32":
            raise ValidationFailed('self.data_type == "int32/uint64/int32" failed')


@dataclasses.dataclass(kw_only=True)
class UnstructuredGridGeometry_V1_2_0(Serialiser):
    """This component describes a set of vertices, indices and cell information."""

    SCHEMA_ID = "/components/unstructured-grid-geometry/1.2.0/unstructured-grid-geometry.schema.json"

    vertices: UnstructuredGridGeometry_V1_2_0_Vertices
    """Vertex coordinates. Columns: x, y, z."""
    cells: UnstructuredGridGeometry_V1_2_0_Cells
    """Cell descriptions which consists of an array of triples. The first item in the triple represents the shape, second item is an offset to the indices array and the third item is the number of vertices for the shape. Columns: shape, offset, num_vertices."""
    indices: IndexArray1_V1_0_1
    """0-based indices into the vertices."""

    def __post_init__(self):
        if not isinstance(self.vertices, UnstructuredGridGeometry_V1_2_0_Vertices):
            raise ValidationFailed("self.vertices is not UnstructuredGridGeometry_V1_2_0_Vertices")
        if not isinstance(self.cells, UnstructuredGridGeometry_V1_2_0_Cells):
            raise ValidationFailed("self.cells is not UnstructuredGridGeometry_V1_2_0_Cells")
        if not isinstance(self.indices, IndexArray1_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray1_V1_0_1")
