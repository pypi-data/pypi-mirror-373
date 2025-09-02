import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .rotation import Rotation_V1_1_0


@dataclasses.dataclass(kw_only=True)
class BlockModelRegularStructure_V1_0_0(Serialiser):
    """The structure of a regular, non-subblocked block model."""

    SCHEMA_ID = "/components/block-model-regular-structure/1.0.0/block-model-regular-structure.schema.json"

    n_blocks: list[int]
    """The number of blocks in the model. [nx, ny, nz]"""
    block_size: list[float]
    """The size of each block in the model. [dx, dy, dz]"""
    origin: list[float]
    """The coordinates of the model origin. [x, y, z]"""
    model_type: str = "regular"
    """The model geometry type."""
    rotation: Rotation_V1_1_0 | None = None
    """The orientation of the model."""

    def __post_init__(self):
        if not isinstance(self.n_blocks, list):
            raise ValidationFailed("self.n_blocks is not a list")
        for v in self.n_blocks:
            if not isinstance(v, int):
                raise ValidationFailed("v is not int")
            if not 1 <= v:
                raise ValidationFailed("1 <= v failed")
        if not len(self.n_blocks) == 3:
            raise ValidationFailed("len(self.n_blocks) == 3 failed")
        if not isinstance(self.block_size, list):
            raise ValidationFailed("self.block_size is not a list")
        for v in self.block_size:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0 < v:
                raise ValidationFailed("0 < v failed")
        if not len(self.block_size) == 3:
            raise ValidationFailed("len(self.block_size) == 3 failed")
        if not isinstance(self.origin, list):
            raise ValidationFailed("self.origin is not a list")
        for v in self.origin:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.origin) == 3:
            raise ValidationFailed("len(self.origin) == 3 failed")
        if not isinstance(self.model_type, str):
            raise ValidationFailed("self.model_type is not str")
        if not self.model_type == "regular":
            raise ValidationFailed('self.model_type == "regular" failed')
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
