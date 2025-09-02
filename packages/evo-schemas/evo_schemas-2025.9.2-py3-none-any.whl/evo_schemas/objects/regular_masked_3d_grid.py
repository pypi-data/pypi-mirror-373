import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bool_attribute import BoolAttribute_V1_0_1, BoolAttribute_V1_1_0
from ..components.one_of_attribute import (
    OneOfAttribute_V1_0_1,
    OneOfAttribute_V1_0_1_Item,
    OneOfAttribute_V1_1_0,
    OneOfAttribute_V1_1_0_Item,
    OneOfAttribute_V1_2_0,
    OneOfAttribute_V1_2_0_Item,
)
from ..components.rotation import Rotation_V1_0_1, Rotation_V1_1_0
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class RegularMasked3DGrid_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A 3D regular masked grid (all cells are equal size). The mask attribute will indicate which cells have values."""

    SCHEMA_ID = "/objects/regular-masked-3d-grid/1.0.1/regular-masked-3d-grid.schema.json"

    origin: list[float]
    """The coordinates of the origin [x,y,z]"""
    size: list[int]
    """Number of cells in each direction. [grid_size_x, grid_size_y, grid_size_z]"""
    cell_size: list[float]
    """The size of each cell in the grid. [cell_size_x, cell_size_y, cell_size_z]"""
    mask: BoolAttribute_V1_0_1
    """Attribute that indicates which cells have values."""
    number_of_active_cells: int
    """Number of active cells."""
    schema: str = "/objects/regular-masked-3d-grid/1.0.1/regular-masked-3d-grid.schema.json"
    rotation: Rotation_V1_0_1 | None = None
    """Orientation of the grid."""
    cell_attributes: OneOfAttribute_V1_0_1 | None = None
    """Attributes associated with the cells."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.size, list):
            raise ValidationFailed("self.size is not a list")
        for v in self.size:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.size) == 3:
            raise ValidationFailed("len(self.size) == 3 failed")
        if not isinstance(self.cell_size, list):
            raise ValidationFailed("self.cell_size is not a list")
        for v in self.cell_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.cell_size) == 3:
            raise ValidationFailed("len(self.cell_size) == 3 failed")
        if not isinstance(self.mask, BoolAttribute_V1_0_1):
            raise ValidationFailed("self.mask is not BoolAttribute_V1_0_1")
        if not isinstance(self.number_of_active_cells, int):
            raise ValidationFailed("self.number_of_active_cells is not int")
        if not 0 < self.number_of_active_cells:
            raise ValidationFailed("0 < self.number_of_active_cells failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/regular-masked-3d-grid/1.0.1/regular-masked-3d-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/regular-masked-3d-grid/1.0.1/regular-masked-3d-grid.schema.json" failed'
            )
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_0_1):
                raise ValidationFailed("self.rotation is not Rotation_V1_0_1")
        if self.cell_attributes is not None:
            if not isinstance(self.cell_attributes, list):
                raise ValidationFailed("self.cell_attributes is not a list")
            for v in self.cell_attributes:
                if not isinstance(v, OneOfAttribute_V1_0_1_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_0_1_Item")


@dataclasses.dataclass(kw_only=True)
class RegularMasked3DGrid_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A 3D regular masked grid (all cells are equal size). The mask attribute will indicate which cells have values."""

    SCHEMA_ID = "/objects/regular-masked-3d-grid/1.1.0/regular-masked-3d-grid.schema.json"

    origin: list[float]
    """The coordinates of the origin [x,y,z]"""
    size: list[int]
    """Number of cells in each direction. [grid_size_x, grid_size_y, grid_size_z]"""
    cell_size: list[float]
    """The size of each cell in the grid. [cell_size_x, cell_size_y, cell_size_z]"""
    mask: BoolAttribute_V1_0_1
    """Attribute that indicates which cells have values."""
    number_of_active_cells: int
    """Number of active cells."""
    schema: str = "/objects/regular-masked-3d-grid/1.1.0/regular-masked-3d-grid.schema.json"
    rotation: Rotation_V1_0_1 | None = None
    """Orientation of the grid."""
    cell_attributes: OneOfAttribute_V1_1_0 | None = None
    """Attributes associated with the cells."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.size, list):
            raise ValidationFailed("self.size is not a list")
        for v in self.size:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.size) == 3:
            raise ValidationFailed("len(self.size) == 3 failed")
        if not isinstance(self.cell_size, list):
            raise ValidationFailed("self.cell_size is not a list")
        for v in self.cell_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.cell_size) == 3:
            raise ValidationFailed("len(self.cell_size) == 3 failed")
        if not isinstance(self.mask, BoolAttribute_V1_0_1):
            raise ValidationFailed("self.mask is not BoolAttribute_V1_0_1")
        if not isinstance(self.number_of_active_cells, int):
            raise ValidationFailed("self.number_of_active_cells is not int")
        if not 0 < self.number_of_active_cells:
            raise ValidationFailed("0 < self.number_of_active_cells failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/regular-masked-3d-grid/1.1.0/regular-masked-3d-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/regular-masked-3d-grid/1.1.0/regular-masked-3d-grid.schema.json" failed'
            )
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_0_1):
                raise ValidationFailed("self.rotation is not Rotation_V1_0_1")
        if self.cell_attributes is not None:
            if not isinstance(self.cell_attributes, list):
                raise ValidationFailed("self.cell_attributes is not a list")
            for v in self.cell_attributes:
                if not isinstance(v, OneOfAttribute_V1_1_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_1_0_Item")


@dataclasses.dataclass(kw_only=True)
class RegularMasked3DGrid_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """A 3D regular masked grid (all cells are equal size). The mask attribute will indicate which cells have values."""

    SCHEMA_ID = "/objects/regular-masked-3d-grid/1.2.0/regular-masked-3d-grid.schema.json"

    origin: list[float]
    """The coordinates of the origin [x,y,z]"""
    size: list[int]
    """Number of cells in each direction. [grid_size_x, grid_size_y, grid_size_z]"""
    cell_size: list[float]
    """The size of each cell in the grid. [cell_size_x, cell_size_y, cell_size_z]"""
    mask: BoolAttribute_V1_1_0
    """Attribute that indicates which cells have values."""
    number_of_active_cells: int
    """Number of active cells."""
    schema: str = "/objects/regular-masked-3d-grid/1.2.0/regular-masked-3d-grid.schema.json"
    rotation: Rotation_V1_1_0 | None = None
    """Orientation of the grid."""
    cell_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with the cells."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.size, list):
            raise ValidationFailed("self.size is not a list")
        for v in self.size:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.size) == 3:
            raise ValidationFailed("len(self.size) == 3 failed")
        if not isinstance(self.cell_size, list):
            raise ValidationFailed("self.cell_size is not a list")
        for v in self.cell_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.cell_size) == 3:
            raise ValidationFailed("len(self.cell_size) == 3 failed")
        if not isinstance(self.mask, BoolAttribute_V1_1_0):
            raise ValidationFailed("self.mask is not BoolAttribute_V1_1_0")
        if not isinstance(self.number_of_active_cells, int):
            raise ValidationFailed("self.number_of_active_cells is not int")
        if not 0 < self.number_of_active_cells:
            raise ValidationFailed("0 < self.number_of_active_cells failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/regular-masked-3d-grid/1.2.0/regular-masked-3d-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/regular-masked-3d-grid/1.2.0/regular-masked-3d-grid.schema.json" failed'
            )
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
        if self.cell_attributes is not None:
            if not isinstance(self.cell_attributes, list):
                raise ValidationFailed("self.cell_attributes is not a list")
            for v in self.cell_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class RegularMasked3DGrid_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """A 3D regular masked grid (all cells are equal size). The mask attribute will indicate which cells have values."""

    SCHEMA_ID = "/objects/regular-masked-3d-grid/1.3.0/regular-masked-3d-grid.schema.json"

    origin: list[float]
    """The coordinates of the origin [x,y,z]"""
    size: list[int]
    """Number of cells in each direction. [grid_size_x, grid_size_y, grid_size_z]"""
    cell_size: list[float]
    """The size of each cell in the grid. [cell_size_x, cell_size_y, cell_size_z]"""
    mask: BoolAttribute_V1_1_0
    """Attribute that indicates which cells have values."""
    number_of_active_cells: int
    """Number of active cells."""
    schema: str = "/objects/regular-masked-3d-grid/1.3.0/regular-masked-3d-grid.schema.json"
    rotation: Rotation_V1_1_0 | None = None
    """Orientation of the grid."""
    cell_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with the cells."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.size, list):
            raise ValidationFailed("self.size is not a list")
        for v in self.size:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.size) == 3:
            raise ValidationFailed("len(self.size) == 3 failed")
        if not isinstance(self.cell_size, list):
            raise ValidationFailed("self.cell_size is not a list")
        for v in self.cell_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.cell_size) == 3:
            raise ValidationFailed("len(self.cell_size) == 3 failed")
        if not isinstance(self.mask, BoolAttribute_V1_1_0):
            raise ValidationFailed("self.mask is not BoolAttribute_V1_1_0")
        if not isinstance(self.number_of_active_cells, int):
            raise ValidationFailed("self.number_of_active_cells is not int")
        if not 0 < self.number_of_active_cells:
            raise ValidationFailed("0 < self.number_of_active_cells failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/regular-masked-3d-grid/1.3.0/regular-masked-3d-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/regular-masked-3d-grid/1.3.0/regular-masked-3d-grid.schema.json" failed'
            )
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
        if self.cell_attributes is not None:
            if not isinstance(self.cell_attributes, list):
                raise ValidationFailed("self.cell_attributes is not a list")
            for v in self.cell_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
