import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .brep_container import BrepContainer_V1_0_1
from .polyline_2d import Polyline2D_V1_0_1
from .polyline_3d import Polyline3D_V1_0_1
from .surface_mesh import SurfaceMesh_V1_0_1


@dataclasses.dataclass(kw_only=True)
class GeometryComposite_V1_0_1(Serialiser):
    """This component describes a geometry composite."""

    SCHEMA_ID = "/components/geometry-composite/1.0.1/geometry-composite.schema.json"

    brep_container: BrepContainer_V1_0_1 | None = None
    """BRep container."""
    mesh: SurfaceMesh_V1_0_1 | None = None
    """Surface mesh."""
    points_2d: list[int] | None = None
    """Indices to 2D vertices."""
    polylines_2d: list[Polyline2D_V1_0_1] | None = None
    """List of 2D lines."""
    points_3d: list[int] | None = None
    """Indices to 3D vertices."""
    polylines_3d: list[Polyline3D_V1_0_1] | None = None
    """List of 3D lines."""

    def __post_init__(self):
        if self.brep_container is not None:
            if not isinstance(self.brep_container, BrepContainer_V1_0_1):
                raise ValidationFailed("self.brep_container is not BrepContainer_V1_0_1")
        if self.mesh is not None:
            if not isinstance(self.mesh, SurfaceMesh_V1_0_1):
                raise ValidationFailed("self.mesh is not SurfaceMesh_V1_0_1")
        if self.points_2d is not None:
            if not isinstance(self.points_2d, list):
                raise ValidationFailed("self.points_2d is not a list")
            for v in self.points_2d:
                if not isinstance(v, int):
                    raise ValidationFailed("v is not int")
                if not 0 <= v:
                    raise ValidationFailed("0 <= v failed")
        if self.polylines_2d is not None:
            if not isinstance(self.polylines_2d, list):
                raise ValidationFailed("self.polylines_2d is not a list")
            for v in self.polylines_2d:
                if not isinstance(v, Polyline2D_V1_0_1):
                    raise ValidationFailed("v is not Polyline2D_V1_0_1")
        if self.points_3d is not None:
            if not isinstance(self.points_3d, list):
                raise ValidationFailed("self.points_3d is not a list")
            for v in self.points_3d:
                if not isinstance(v, int):
                    raise ValidationFailed("v is not int")
                if not 0 <= v:
                    raise ValidationFailed("0 <= v failed")
        if self.polylines_3d is not None:
            if not isinstance(self.polylines_3d, list):
                raise ValidationFailed("self.polylines_3d is not a list")
            for v in self.polylines_3d:
                if not isinstance(v, Polyline3D_V1_0_1):
                    raise ValidationFailed("v is not Polyline3D_V1_0_1")
