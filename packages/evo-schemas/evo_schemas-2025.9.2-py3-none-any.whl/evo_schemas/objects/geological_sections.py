from __future__ import annotations

import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.embedded_line_geometry import EmbeddedLineGeometry_V1_0_0
from ..components.embedded_polyline_object import EmbeddedPolylineObject_V1_0_0
from ..components.material import Material_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_2_0, OneOfAttribute_V1_2_0_Item
from ..components.rotation import Rotation_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_Folder_Items_SectionIndex(Serialiser):
    section_index: int
    """The index of the section in the sections list."""

    def __post_init__(self):
        if not isinstance(self.section_index, int):
            raise ValidationFailed("self.section_index is not int")
        if not 0 <= self.section_index:
            raise ValidationFailed("0 <= self.section_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_Folder(Serialiser):
    name: str
    """Name of the folder."""
    items: list[GeologicalSections_V1_1_0_Folder_Items]
    """A list of folders containing cross-sections."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalSections_V1_1_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalSections_V1_1_0_Folder_Items")


GeologicalSections_V1_1_0_Folder_Items = (
    GeologicalSections_V1_1_0_Folder | GeologicalSections_V1_1_0_Folder_Items_SectionIndex
)


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_Section_IndicesRange(Serialiser):
    offset: int
    """The first index"""
    count: int
    """The number of objects referenced."""

    def __post_init__(self):
        if not isinstance(self.offset, int):
            raise ValidationFailed("self.offset is not int")
        if not 0 <= self.offset:
            raise ValidationFailed("0 <= self.offset failed")
        if not isinstance(self.count, int):
            raise ValidationFailed("self.count is not int")
        if not 1 <= self.count:
            raise ValidationFailed("1 <= self.count failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_Section(Serialiser):
    name: str
    """Name of the section."""
    origin: list[float]
    """The coordinates of the section origin. [x, y, z]"""
    rotation: Rotation_V1_1_0
    """The orientation of the section."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    volumes: GeologicalSections_V1_1_0_Section_IndicesRange | None = None
    """The consecutive group of volumes in the volumes list."""
    surfaces: GeologicalSections_V1_1_0_Section_IndicesRange | None = None
    """The consecutive group of surfaces in the surface list."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.rotation, Rotation_V1_1_0):
            raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.volumes is not None:
            if not isinstance(self.volumes, GeologicalSections_V1_1_0_Section_IndicesRange):
                raise ValidationFailed("self.volumes is not GeologicalSections_V1_1_0_Section_IndicesRange")
        if self.surfaces is not None:
            if not isinstance(self.surfaces, GeologicalSections_V1_1_0_Section_IndicesRange):
                raise ValidationFailed("self.surfaces is not GeologicalSections_V1_1_0_Section_IndicesRange")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_GmEmbeddedPolygonVolume(EmbeddedPolylineObject_V1_0_0):
    """A closed polyline defining the external ring of the polygon."""

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""
    layer: str | None = None
    """Optional identifier for the layer containing the polygon. Polygons in the same layer should not overlap. Polygons in different layers can overlap. Layer precidence may matters s follow a layer precidence where defined"""
    internal_rings: list[EmbeddedPolylineObject_V1_0_0] | None = None
    """Optional field representing internal rings (holes) inside the volume. When multiple inner_ring's exist they can touch but should not overlap. There may or may not be another volume whose external ring overlaps an inner ring"""

    def __post_init__(self):
        EmbeddedPolylineObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in ("Void", "OutputVolume", "Vein", "VeinSystem"):
            raise ValidationFailed('self.feature in ("Void", "OutputVolume", "Vein", "VeinSystem") failed')
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")
        if self.layer is not None:
            if not isinstance(self.layer, str):
                raise ValidationFailed("self.layer is not str")
        if self.internal_rings is not None:
            if not isinstance(self.internal_rings, list):
                raise ValidationFailed("self.internal_rings is not a list")
            for v in self.internal_rings:
                if not isinstance(v, EmbeddedPolylineObject_V1_0_0):
                    raise ValidationFailed("v is not EmbeddedPolylineObject_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0_GmEmbeddedPolylineSurface(EmbeddedPolylineObject_V1_0_0):
    feature: str
    """Kind of feature."""
    layer: str | None = None
    """Identifier for the layer containing the polyline. Polylines in the same layer should not overlap. Polylines in different layers can overlap."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedPolylineObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "StratigraphicContactSurface",
        ):
            raise ValidationFailed(
                'self.feature in ("Fault", "ContactSurface", "Topography", "BoundarySurface", "StratigraphicContactSurface") failed'
            )
        if self.layer is not None:
            if not isinstance(self.layer, str):
                raise ValidationFailed("self.layer is not str")
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_1_0(BaseSpatialDataProperties_V1_1_0):
    """A collection of cross-sections made up from multiple polygons/polylines."""

    SCHEMA_ID = "/objects/geological-sections/1.1.0/geological-sections.schema.json"

    folders: list[GeologicalSections_V1_1_0_Folder]
    """A recursive list of folders containing indices into the sections list."""
    line_geometry: EmbeddedLineGeometry_V1_0_0
    """The embedded line geometry, defining vertices, segments and parts."""
    sections: list[GeologicalSections_V1_1_0_Section]
    """A list of cross-sections."""
    volumes: list[GeologicalSections_V1_1_0_GmEmbeddedPolygonVolume]
    """A list of embedded polygon volumes. Each volume consists of a number of parts."""
    surfaces: list[GeologicalSections_V1_1_0_GmEmbeddedPolylineSurface]
    """A list of embedded polyline surfaces. Each surface consists of a number of parts."""
    schema: str = "/objects/geological-sections/1.1.0/geological-sections.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this planar geology collection."""
    section_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each section. The attribute tables have one row per section."""
    volume_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each polygon volume. The attribute tables have one row per volume."""
    surface_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each polyline surface. The attribute tables have one row per surface."""
    layer_order: list[str] | None = None
    """An optional list of layers used when stacking volumes on top of each other. The first entry represents the topmost layer, while the last entry represents the bottommost. Layers are occluded sequentially from top to bottom."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalSections_V1_1_0_Folder):
                raise ValidationFailed("v is not GeologicalSections_V1_1_0_Folder")
        if not isinstance(self.line_geometry, EmbeddedLineGeometry_V1_0_0):
            raise ValidationFailed("self.line_geometry is not EmbeddedLineGeometry_V1_0_0")
        if not isinstance(self.sections, list):
            raise ValidationFailed("self.sections is not a list")
        for v in self.sections:
            if not isinstance(v, GeologicalSections_V1_1_0_Section):
                raise ValidationFailed("v is not GeologicalSections_V1_1_0_Section")
        if not isinstance(self.volumes, list):
            raise ValidationFailed("self.volumes is not a list")
        for v in self.volumes:
            if not isinstance(v, GeologicalSections_V1_1_0_GmEmbeddedPolygonVolume):
                raise ValidationFailed("v is not GeologicalSections_V1_1_0_GmEmbeddedPolygonVolume")
        if not isinstance(self.surfaces, list):
            raise ValidationFailed("self.surfaces is not a list")
        for v in self.surfaces:
            if not isinstance(v, GeologicalSections_V1_1_0_GmEmbeddedPolylineSurface):
                raise ValidationFailed("v is not GeologicalSections_V1_1_0_GmEmbeddedPolylineSurface")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-sections/1.1.0/geological-sections.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-sections/1.1.0/geological-sections.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
        if self.section_attributes is not None:
            if not isinstance(self.section_attributes, list):
                raise ValidationFailed("self.section_attributes is not a list")
            for v in self.section_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.volume_attributes is not None:
            if not isinstance(self.volume_attributes, list):
                raise ValidationFailed("self.volume_attributes is not a list")
            for v in self.volume_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.surface_attributes is not None:
            if not isinstance(self.surface_attributes, list):
                raise ValidationFailed("self.surface_attributes is not a list")
            for v in self.surface_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.layer_order is not None:
            if not isinstance(self.layer_order, list):
                raise ValidationFailed("self.layer_order is not a list")
            for v in self.layer_order:
                if not isinstance(v, str):
                    raise ValidationFailed("v is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_Folder_Items_SectionIndex(Serialiser):
    section_index: int
    """The index of the section in the sections list."""

    def __post_init__(self):
        if not isinstance(self.section_index, int):
            raise ValidationFailed("self.section_index is not int")
        if not 0 <= self.section_index:
            raise ValidationFailed("0 <= self.section_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_Folder(Serialiser):
    name: str
    """Name of the folder."""
    items: list[GeologicalSections_V1_0_0_Folder_Items]
    """A list of folders containing cross-sections."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalSections_V1_0_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalSections_V1_0_0_Folder_Items")


GeologicalSections_V1_0_0_Folder_Items = (
    GeologicalSections_V1_0_0_Folder | GeologicalSections_V1_0_0_Folder_Items_SectionIndex
)


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_Section_IndicesRange(Serialiser):
    offset: int
    """The first index"""
    count: int
    """The number of objects referenced."""

    def __post_init__(self):
        if not isinstance(self.offset, int):
            raise ValidationFailed("self.offset is not int")
        if not 0 <= self.offset:
            raise ValidationFailed("0 <= self.offset failed")
        if not isinstance(self.count, int):
            raise ValidationFailed("self.count is not int")
        if not 1 <= self.count:
            raise ValidationFailed("1 <= self.count failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_Section(Serialiser):
    name: str
    """Name of the section."""
    origin: list[float]
    """The coordinates of the section origin. [x, y, z]"""
    rotation: Rotation_V1_1_0
    """The orientation of the section."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    volumes: GeologicalSections_V1_0_0_Section_IndicesRange | None = None
    """The consecutive group of volumes in the volumes list."""
    surfaces: GeologicalSections_V1_0_0_Section_IndicesRange | None = None
    """The consecutive group of surfaces in the surface list."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.rotation, Rotation_V1_1_0):
            raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.volumes is not None:
            if not isinstance(self.volumes, GeologicalSections_V1_0_0_Section_IndicesRange):
                raise ValidationFailed("self.volumes is not GeologicalSections_V1_0_0_Section_IndicesRange")
        if self.surfaces is not None:
            if not isinstance(self.surfaces, GeologicalSections_V1_0_0_Section_IndicesRange):
                raise ValidationFailed("self.surfaces is not GeologicalSections_V1_0_0_Section_IndicesRange")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_GmEmbeddedPolygonVolume(EmbeddedPolylineObject_V1_0_0):
    layer: str
    """Identifier for the layer containing the polygon. Polygons in the same layer should not overlap. Polygons in different layers can overlap."""
    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedPolylineObject_V1_0_0.__post_init__(self)
        if not isinstance(self.layer, str):
            raise ValidationFailed("self.layer is not str")
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in ("Void", "OutputVolume", "Vein", "VeinSystem"):
            raise ValidationFailed('self.feature in ("Void", "OutputVolume", "Vein", "VeinSystem") failed')
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0_GmEmbeddedPolylineSurface(EmbeddedPolylineObject_V1_0_0):
    layer: str
    """Identifier for the layer containing the polyline. Polylines in the same layer should not overlap. Polylines in different layers can overlap."""
    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedPolylineObject_V1_0_0.__post_init__(self)
        if not isinstance(self.layer, str):
            raise ValidationFailed("self.layer is not str")
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "StratigraphicContactSurface",
        ):
            raise ValidationFailed(
                'self.feature in ("Fault", "ContactSurface", "Topography", "BoundarySurface", "StratigraphicContactSurface") failed'
            )
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalSections_V1_0_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of cross-sections made up from multiple polygons/polylines."""

    SCHEMA_ID = "/objects/geological-sections/1.0.0/geological-sections.schema.json"

    folders: list[GeologicalSections_V1_0_0_Folder]
    """A recursive list of folders containing indices into the sections list."""
    line_geometry: EmbeddedLineGeometry_V1_0_0
    """The embedded line geometry, defining vertices, segments and parts."""
    sections: list[GeologicalSections_V1_0_0_Section]
    """A list of cross-sections."""
    volumes: list[GeologicalSections_V1_0_0_GmEmbeddedPolygonVolume]
    """A list of embedded polygon volumes. Each volume consists of a number of parts."""
    surfaces: list[GeologicalSections_V1_0_0_GmEmbeddedPolylineSurface]
    """A list of embedded polyline surfaces. Each surface consists of a number of parts."""
    schema: str = "/objects/geological-sections/1.0.0/geological-sections.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this planar geology collection."""
    section_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each section. The attribute tables have one row per section."""
    volume_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each polygon volume. The attribute tables have one row per volume."""
    surface_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each polyline surface. The attribute tables have one row per surface."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalSections_V1_0_0_Folder):
                raise ValidationFailed("v is not GeologicalSections_V1_0_0_Folder")
        if not isinstance(self.line_geometry, EmbeddedLineGeometry_V1_0_0):
            raise ValidationFailed("self.line_geometry is not EmbeddedLineGeometry_V1_0_0")
        if not isinstance(self.sections, list):
            raise ValidationFailed("self.sections is not a list")
        for v in self.sections:
            if not isinstance(v, GeologicalSections_V1_0_0_Section):
                raise ValidationFailed("v is not GeologicalSections_V1_0_0_Section")
        if not isinstance(self.volumes, list):
            raise ValidationFailed("self.volumes is not a list")
        for v in self.volumes:
            if not isinstance(v, GeologicalSections_V1_0_0_GmEmbeddedPolygonVolume):
                raise ValidationFailed("v is not GeologicalSections_V1_0_0_GmEmbeddedPolygonVolume")
        if not isinstance(self.surfaces, list):
            raise ValidationFailed("self.surfaces is not a list")
        for v in self.surfaces:
            if not isinstance(v, GeologicalSections_V1_0_0_GmEmbeddedPolylineSurface):
                raise ValidationFailed("v is not GeologicalSections_V1_0_0_GmEmbeddedPolylineSurface")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-sections/1.0.0/geological-sections.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-sections/1.0.0/geological-sections.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
        if self.section_attributes is not None:
            if not isinstance(self.section_attributes, list):
                raise ValidationFailed("self.section_attributes is not a list")
            for v in self.section_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.volume_attributes is not None:
            if not isinstance(self.volume_attributes, list):
                raise ValidationFailed("self.volume_attributes is not a list")
            for v in self.volume_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.surface_attributes is not None:
            if not isinstance(self.surface_attributes, list):
                raise ValidationFailed("self.surface_attributes is not a list")
            for v in self.surface_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
