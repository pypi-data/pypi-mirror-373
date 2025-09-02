import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.geometry_part import GeometryPart_V1_0_1
from ..components.lines_2d_indices import Lines2DIndices_V1_0_1
from ..components.lines_3d_indices import Lines3DIndices_V1_0_1
from ..components.material import Material_V1_0_1
from ..components.vertices_2d import Vertices2D_V1_0_1
from ..components.vertices_3d import Vertices3D_V1_0_1
from ..elements.serialiser import ValidationFailed
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories


@dataclasses.dataclass(kw_only=True)
class DesignGeometry_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """2D/3D Geometry"""

    SCHEMA_ID = "/objects/design-geometry/1.0.1/design-geometry.schema.json"

    kind: str
    """The kind of geometry."""
    materials: list[Material_V1_0_1]
    """Materials for this geometry."""
    parts: list[GeometryPart_V1_0_1]
    """List of geometry parts."""
    schema: str = "/objects/design-geometry/1.0.1/design-geometry.schema.json"
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    vertices_2d: Vertices2D_V1_0_1 | None = None
    """Vertex coordinates in 2D space."""
    vertices_3d: Vertices3D_V1_0_1 | None = None
    """Vertex coordinates in 3D space."""
    lines_2d: Lines2DIndices_V1_0_1 | None = None
    """2D line indices."""
    lines_3d: Lines3DIndices_V1_0_1 | None = None
    """3D line indices."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in ("Planar2D", "Domain3D"):
            raise ValidationFailed('self.kind in ("Planar2D", "Domain3D") failed')
        if not isinstance(self.materials, list):
            raise ValidationFailed("self.materials is not a list")
        for v in self.materials:
            if not isinstance(v, Material_V1_0_1):
                raise ValidationFailed("v is not Material_V1_0_1")
        if not isinstance(self.parts, list):
            raise ValidationFailed("self.parts is not a list")
        for v in self.parts:
            if not isinstance(v, GeometryPart_V1_0_1):
                raise ValidationFailed("v is not GeometryPart_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/design-geometry/1.0.1/design-geometry.schema.json":
            raise ValidationFailed('self.schema == "/objects/design-geometry/1.0.1/design-geometry.schema.json" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.vertices_2d is not None:
            if not isinstance(self.vertices_2d, Vertices2D_V1_0_1):
                raise ValidationFailed("self.vertices_2d is not Vertices2D_V1_0_1")
        if self.vertices_3d is not None:
            if not isinstance(self.vertices_3d, Vertices3D_V1_0_1):
                raise ValidationFailed("self.vertices_3d is not Vertices3D_V1_0_1")
        if self.lines_2d is not None:
            if not isinstance(self.lines_2d, Lines2DIndices_V1_0_1):
                raise ValidationFailed("self.lines_2d is not Lines2DIndices_V1_0_1")
        if self.lines_3d is not None:
            if not isinstance(self.lines_3d, Lines3DIndices_V1_0_1):
                raise ValidationFailed("self.lines_3d is not Lines3DIndices_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class DesignGeometry_V1_1_0(BaseSpatialDataProperties_V1_1_0):
    """2D/3D Geometry"""

    SCHEMA_ID = "/objects/design-geometry/1.1.0/design-geometry.schema.json"

    kind: str
    """The kind of geometry."""
    materials: list[Material_V1_0_1]
    """Materials for this geometry."""
    parts: list[GeometryPart_V1_0_1]
    """List of geometry parts."""
    schema: str = "/objects/design-geometry/1.1.0/design-geometry.schema.json"
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    vertices_2d: Vertices2D_V1_0_1 | None = None
    """Vertex coordinates in 2D space."""
    vertices_3d: Vertices3D_V1_0_1 | None = None
    """Vertex coordinates in 3D space."""
    lines_2d: Lines2DIndices_V1_0_1 | None = None
    """2D line indices."""
    lines_3d: Lines3DIndices_V1_0_1 | None = None
    """3D line indices."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in ("Planar2D", "Domain3D"):
            raise ValidationFailed('self.kind in ("Planar2D", "Domain3D") failed')
        if not isinstance(self.materials, list):
            raise ValidationFailed("self.materials is not a list")
        for v in self.materials:
            if not isinstance(v, Material_V1_0_1):
                raise ValidationFailed("v is not Material_V1_0_1")
        if not isinstance(self.parts, list):
            raise ValidationFailed("self.parts is not a list")
        for v in self.parts:
            if not isinstance(v, GeometryPart_V1_0_1):
                raise ValidationFailed("v is not GeometryPart_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/design-geometry/1.1.0/design-geometry.schema.json":
            raise ValidationFailed('self.schema == "/objects/design-geometry/1.1.0/design-geometry.schema.json" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.vertices_2d is not None:
            if not isinstance(self.vertices_2d, Vertices2D_V1_0_1):
                raise ValidationFailed("self.vertices_2d is not Vertices2D_V1_0_1")
        if self.vertices_3d is not None:
            if not isinstance(self.vertices_3d, Vertices3D_V1_0_1):
                raise ValidationFailed("self.vertices_3d is not Vertices3D_V1_0_1")
        if self.lines_2d is not None:
            if not isinstance(self.lines_2d, Lines2DIndices_V1_0_1):
                raise ValidationFailed("self.lines_2d is not Lines2DIndices_V1_0_1")
        if self.lines_3d is not None:
            if not isinstance(self.lines_3d, Lines3DIndices_V1_0_1):
                raise ValidationFailed("self.lines_3d is not Lines3DIndices_V1_0_1")
