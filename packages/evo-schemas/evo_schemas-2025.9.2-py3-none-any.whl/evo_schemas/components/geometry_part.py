import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .bounding_box import BoundingBox_V1_0_1
from .geometry_composite import GeometryComposite_V1_0_1


@dataclasses.dataclass(kw_only=True)
class GeometryPart_V1_0_1_Feature(Serialiser):
    """Geometry part feature."""

    name: str
    """Feature name."""
    kind: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.kind, str):
            raise ValidationFailed("self.kind is not str")
        if self.kind not in (
            "Void",
            "Soil",
            "GMV",
            "Discontinuity",
            "Plate",
            "Geogrid",
            "Beam",
            "EmbeddedBeam",
            "Cable",
            "Anchor",
        ):
            raise ValidationFailed(
                'self.kind in ("Void", "Soil", "GMV", "Discontinuity", "Plate", "Geogrid", "Beam", "EmbeddedBeam", "Cable", "Anchor") failed'
            )
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeometryPart_V1_0_1_Geometry_PartKey(Serialiser):
    """Another part in the geometry"""

    part_key: str
    """Unique identifier of another part in the geometry."""

    def __post_init__(self):
        if not isinstance(self.part_key, str):
            raise ValidationFailed("self.part_key is not str")


GeometryPart_V1_0_1_Geometry = GeometryPart_V1_0_1_Geometry_PartKey | GeometryComposite_V1_0_1


@dataclasses.dataclass(kw_only=True)
class GeometryPart_V1_0_1(Serialiser):
    """This component describes a geometry part."""

    SCHEMA_ID = "/components/geometry-part/1.0.1/geometry-part.schema.json"

    key: str
    """Unique identifier of the geometry part."""
    name: str
    """Name."""
    feature: GeometryPart_V1_0_1_Feature
    """Geometry part feature."""
    bounding_box: BoundingBox_V1_0_1
    """Bounding box of the geometry part."""
    geometry: GeometryPart_V1_0_1_Geometry
    """Another part in the geometry or a geometry composite."""
    data_source: str | None = None
    """Data source."""
    transform: list[float] | None = None
    """4x4 transformation matrix flattened in row-major order."""
    layer: str | None = None
    """Geometry part layer."""
    color: int | None = None
    """Geometry part color."""

    def __post_init__(self):
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.feature, GeometryPart_V1_0_1_Feature):
            raise ValidationFailed("self.feature is not GeometryPart_V1_0_1_Feature")
        if not isinstance(self.bounding_box, BoundingBox_V1_0_1):
            raise ValidationFailed("self.bounding_box is not BoundingBox_V1_0_1")
        if not isinstance(self.geometry, GeometryPart_V1_0_1_Geometry):
            raise ValidationFailed("self.geometry is not GeometryPart_V1_0_1_Geometry")
        if self.data_source is not None:
            if not isinstance(self.data_source, str):
                raise ValidationFailed("self.data_source is not str")
        if self.transform is not None:
            if not isinstance(self.transform, list):
                raise ValidationFailed("self.transform is not a list")
            for v in self.transform:
                if not isinstance(v, float):
                    raise ValidationFailed("v is not float")
            if not len(self.transform) == 16:
                raise ValidationFailed("len(self.transform) == 16 failed")
        if self.layer is not None:
            if not isinstance(self.layer, str):
                raise ValidationFailed("self.layer is not str")
        if self.color is not None:
            if not isinstance(self.color, int):
                raise ValidationFailed("self.color is not int")
