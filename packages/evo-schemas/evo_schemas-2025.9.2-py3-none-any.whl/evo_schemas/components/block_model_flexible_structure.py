import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .rotation import Rotation_V1_1_0


@dataclasses.dataclass(kw_only=True)
class BlockModelFlexibleStructure_V1_0_0(Serialiser):
    """The structure of a flexibly-subblocked block model. Subblocking is carried out by dividing each parent block into a fixed grid of subblocks defined by n_subblocks_per_parent, before recombining the subblocks into larger chunks. The resulting subblocks can have different sizes within the same parent block, but must remain cuboid and completely fill the parent block."""

    SCHEMA_ID = "/components/block-model-flexible-structure/1.0.0/block-model-flexible-structure.schema.json"

    n_parent_blocks: list[int]
    """The number of parent blocks in the model. [nx, ny, nz]"""
    parent_block_size: list[float]
    """The size of each parent block in the model. [dx, dy, dz]"""
    n_subblocks_per_parent: list[int]
    """The number of blocks per axis in the underlying subblock grid in each parent block in the model. [nx, ny, nz]"""
    origin: list[float]
    """The coordinates of the model origin. [x, y, z]"""
    model_type: str = "flexible"
    """The model geometry type."""
    rotation: Rotation_V1_1_0 | None = None
    """The orientation of the model."""

    def __post_init__(self):
        if not isinstance(self.n_parent_blocks, list):
            raise ValidationFailed("self.n_parent_blocks is not a list")
        for v in self.n_parent_blocks:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.n_parent_blocks) == 3:
            raise ValidationFailed("len(self.n_parent_blocks) == 3 failed")
        if not isinstance(self.parent_block_size, list):
            raise ValidationFailed("self.parent_block_size is not a list")
        for v in self.parent_block_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.parent_block_size) == 3:
            raise ValidationFailed("len(self.parent_block_size) == 3 failed")
        if not isinstance(self.n_subblocks_per_parent, list):
            raise ValidationFailed("self.n_subblocks_per_parent is not a list")
        for v in self.n_subblocks_per_parent:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v <= 100:
                raise ValidationFailed("1 <= v <= 100 failed")
        if not len(self.n_subblocks_per_parent) == 3:
            raise ValidationFailed("len(self.n_subblocks_per_parent) == 3 failed")
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.model_type, str):
            raise ValidationFailed("self.model_type is not str")
        if not self.model_type == "flexible":
            raise ValidationFailed('self.model_type == "flexible" failed')
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
