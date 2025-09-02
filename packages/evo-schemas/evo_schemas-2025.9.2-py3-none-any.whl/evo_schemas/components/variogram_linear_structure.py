import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .ellipsoid import Ellipsoid_V1_0_1, Ellipsoid_V1_1_0


@dataclasses.dataclass(kw_only=True)
class VariogramLinearStructure_V1_0_1(Serialiser):
    """Linear variogram structure."""

    SCHEMA_ID = "/components/variogram-linear-structure/1.0.1/variogram-linear-structure.schema.json"

    contribution: float
    """The scaling of the structure and contribution to the total sill of the variogram model."""
    anisotropy: Ellipsoid_V1_0_1
    """The spatial extent and orientation of the variogram structure."""
    variogram_type: str = "linear"
    """type of structure - linear"""

    def __post_init__(self):
        if not isinstance(self.contribution, float):
            raise ValidationFailed("self.contribution is not float")
        if not 0 < self.contribution:
            raise ValidationFailed("0 < self.contribution failed")
        if not isinstance(self.anisotropy, Ellipsoid_V1_0_1):
            raise ValidationFailed("self.anisotropy is not Ellipsoid_V1_0_1")
        if not isinstance(self.variogram_type, str):
            raise ValidationFailed("self.variogram_type is not str")
        if not self.variogram_type == "linear":
            raise ValidationFailed('self.variogram_type == "linear" failed')


@dataclasses.dataclass(kw_only=True)
class VariogramLinearStructure_V1_1_0(Serialiser):
    """Linear variogram structure."""

    SCHEMA_ID = "/components/variogram-linear-structure/1.1.0/variogram-linear-structure.schema.json"

    contribution: float
    """The scaling of the structure and contribution to the total sill of the variogram model."""
    anisotropy: Ellipsoid_V1_1_0
    """The spatial extent and orientation of the variogram structure."""
    variogram_type: str = "linear"
    """type of structure - linear"""

    def __post_init__(self):
        if not isinstance(self.contribution, float):
            raise ValidationFailed("self.contribution is not float")
        if not 0 < self.contribution:
            raise ValidationFailed("0 < self.contribution failed")
        if not isinstance(self.anisotropy, Ellipsoid_V1_1_0):
            raise ValidationFailed("self.anisotropy is not Ellipsoid_V1_1_0")
        if not isinstance(self.variogram_type, str):
            raise ValidationFailed("self.variogram_type is not str")
        if not self.variogram_type == "linear":
            raise ValidationFailed('self.variogram_type == "linear" failed')
