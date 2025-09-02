import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.quadrilaterals import Quadrilaterals_V1_0_1, Quadrilaterals_V1_1_0, Quadrilaterals_V1_2_0
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class UnstructuredQuadGrid_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """An unstructured quadrilateral grid."""

    SCHEMA_ID = "/objects/unstructured-quad-grid/1.0.1/unstructured-quad-grid.schema.json"

    quadrilaterals: Quadrilaterals_V1_0_1
    """The quadrilaterals of the unstructured grid."""
    schema: str = "/objects/unstructured-quad-grid/1.0.1/unstructured-quad-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.quadrilaterals, Quadrilaterals_V1_0_1):
            raise ValidationFailed("self.quadrilaterals is not Quadrilaterals_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-quad-grid/1.0.1/unstructured-quad-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-quad-grid/1.0.1/unstructured-quad-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredQuadGrid_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """An unstructured quadrilateral grid."""

    SCHEMA_ID = "/objects/unstructured-quad-grid/1.1.0/unstructured-quad-grid.schema.json"

    quadrilaterals: Quadrilaterals_V1_1_0
    """The quadrilaterals of the unstructured grid."""
    schema: str = "/objects/unstructured-quad-grid/1.1.0/unstructured-quad-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.quadrilaterals, Quadrilaterals_V1_1_0):
            raise ValidationFailed("self.quadrilaterals is not Quadrilaterals_V1_1_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-quad-grid/1.1.0/unstructured-quad-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-quad-grid/1.1.0/unstructured-quad-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredQuadGrid_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """An unstructured quadrilateral grid."""

    SCHEMA_ID = "/objects/unstructured-quad-grid/1.2.0/unstructured-quad-grid.schema.json"

    quadrilaterals: Quadrilaterals_V1_2_0
    """The quadrilaterals of the unstructured grid."""
    schema: str = "/objects/unstructured-quad-grid/1.2.0/unstructured-quad-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.quadrilaterals, Quadrilaterals_V1_2_0):
            raise ValidationFailed("self.quadrilaterals is not Quadrilaterals_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-quad-grid/1.2.0/unstructured-quad-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-quad-grid/1.2.0/unstructured-quad-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredQuadGrid_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """An unstructured quadrilateral grid."""

    SCHEMA_ID = "/objects/unstructured-quad-grid/1.3.0/unstructured-quad-grid.schema.json"

    quadrilaterals: Quadrilaterals_V1_2_0
    """The quadrilaterals of the unstructured grid."""
    schema: str = "/objects/unstructured-quad-grid/1.3.0/unstructured-quad-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.quadrilaterals, Quadrilaterals_V1_2_0):
            raise ValidationFailed("self.quadrilaterals is not Quadrilaterals_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-quad-grid/1.3.0/unstructured-quad-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-quad-grid/1.3.0/unstructured-quad-grid.schema.json" failed'
            )
