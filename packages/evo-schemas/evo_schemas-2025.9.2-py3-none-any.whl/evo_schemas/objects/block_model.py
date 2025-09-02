import dataclasses
import uuid

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_1_0
from ..components.block_model_attribute import BlockModelAttribute_V1_0_0
from ..components.block_model_category_attribute import BlockModelCategoryAttribute_V1_0_0
from ..components.block_model_flexible_structure import BlockModelFlexibleStructure_V1_0_0
from ..components.block_model_fully_subblocked_structure import BlockModelFullySubblockedStructure_V1_0_0
from ..components.block_model_regular_structure import BlockModelRegularStructure_V1_0_0
from ..components.block_model_variable_octree_structure import BlockModelVariableOctreeStructure_V1_0_0
from ..elements.serialiser import ValidationFailed

BlockModel_V1_0_0_Geometry = (
    BlockModelFlexibleStructure_V1_0_0
    | BlockModelFullySubblockedStructure_V1_0_0
    | BlockModelRegularStructure_V1_0_0
    | BlockModelVariableOctreeStructure_V1_0_0
)
BlockModel_V1_0_0_Attributes = BlockModelAttribute_V1_0_0 | BlockModelCategoryAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class BlockModel_V1_0_0(BaseSpatialDataProperties_V1_1_0):
    """A reference to a block model stored in the Block Model Service."""

    SCHEMA_ID = "/objects/block-model/1.0.0/block-model.schema.json"

    block_model_uuid: uuid.UUID
    """The unique ID of the block model in the Block Model Service."""
    geometry: BlockModel_V1_0_0_Geometry
    """The geometry (including subblocking parameters, if applicable) of the block model."""
    schema: str = "/objects/block-model/1.0.0/block-model.schema.json"
    block_model_version_uuid: uuid.UUID | None = None
    """The unique ID of this version of the block model in the Block Model Service."""
    attributes: list[BlockModel_V1_0_0_Attributes] | None = None
    """The attributes found on this version of the block model."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.block_model_uuid, uuid.UUID):
            raise ValidationFailed("self.block_model_uuid is not uuid.UUID")
        if not isinstance(self.geometry, BlockModel_V1_0_0_Geometry):
            raise ValidationFailed("self.geometry is not BlockModel_V1_0_0_Geometry")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/block-model/1.0.0/block-model.schema.json":
            raise ValidationFailed('self.schema == "/objects/block-model/1.0.0/block-model.schema.json" failed')
        if self.block_model_version_uuid is not None:
            if not isinstance(self.block_model_version_uuid, uuid.UUID):
                raise ValidationFailed("self.block_model_version_uuid is not uuid.UUID")
        if self.attributes is not None:
            if not isinstance(self.attributes, list):
                raise ValidationFailed("self.attributes is not a list")
            for v in self.attributes:
                if not isinstance(v, BlockModel_V1_0_0_Attributes):
                    raise ValidationFailed("v is not BlockModel_V1_0_0_Attributes")
