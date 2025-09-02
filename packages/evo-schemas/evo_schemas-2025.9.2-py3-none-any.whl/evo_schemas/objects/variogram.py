import dataclasses

from ..components.base_object_properties import BaseObjectProperties_V1_0_1, BaseObjectProperties_V1_1_0
from ..components.variogram_cubic_structure import VariogramCubicStructure_V1_0_1, VariogramCubicStructure_V1_1_0
from ..components.variogram_exponential_structure import (
    VariogramExponentialStructure_V1_0_1,
    VariogramExponentialStructure_V1_1_0,
)
from ..components.variogram_gaussian_structure import (
    VariogramGaussianStructure_V1_0_1,
    VariogramGaussianStructure_V1_1_0,
)
from ..components.variogram_generalisedcauchy_structure import (
    VariogramGeneralisedcauchyStructure_V1_0_1,
    VariogramGeneralisedcauchyStructure_V1_1_0,
)
from ..components.variogram_linear_structure import VariogramLinearStructure_V1_0_1, VariogramLinearStructure_V1_1_0
from ..components.variogram_spherical_structure import (
    VariogramSphericalStructure_V1_0_1,
    VariogramSphericalStructure_V1_1_0,
)
from ..components.variogram_spheroidal_structure import (
    VariogramSpheroidalStructure_V1_0_1,
    VariogramSpheroidalStructure_V1_1_0,
)
from ..elements.serialiser import ValidationFailed

Variogram_V1_0_1_Structures = (
    VariogramExponentialStructure_V1_0_1
    | VariogramGaussianStructure_V1_0_1
    | VariogramGeneralisedcauchyStructure_V1_0_1
    | VariogramSphericalStructure_V1_0_1
    | VariogramSpheroidalStructure_V1_0_1
    | VariogramLinearStructure_V1_0_1
    | VariogramCubicStructure_V1_0_1
)


@dataclasses.dataclass(kw_only=True)
class Variogram_V1_0_1(BaseObjectProperties_V1_0_1):
    """Variogram model and associated metadata. The variogram model is defined by the nugget, and multiple structures using the leapfrog-convention rotation. See struture and rotation components for additional details."""

    SCHEMA_ID = "/objects/variogram/1.0.1/variogram.schema.json"

    sill: float
    """The variance of the variogram. This must be within a very small tolerance of the nugget plus the sum of all structure's contributions."""
    is_rotation_fixed: bool
    """Boolean value specifying whether all structure's rotations are the same."""
    structures: list[Variogram_V1_0_1_Structures]
    """A list of at least one mathematical model, which are parameterised to represent the spatial structure of the variogram model."""
    schema: str = "/objects/variogram/1.0.1/variogram.schema.json"
    nugget: float = 0.0
    """The variance between two samples separated by near-zero lag distance, representing the randomness present. When plotted, this value is the y-intercept."""
    data_variance: float | None = None
    """The variance of the data, if different from the sill value, this is used for normalising or rescaling the variogram"""
    modelling_space: str | None = None
    """The modelling space the variogram model was fitted in either data for original units or normalscore for gaussian space."""
    domain: str | None = None
    """The domain the variogram is modelled for"""
    attribute: str | None = None
    """The attribute the variogram is modelled for"""

    def __post_init__(self):
        BaseObjectProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.sill, float):
            raise ValidationFailed("self.sill is not float")
        if not 0.0 <= self.sill:
            raise ValidationFailed("0.0 <= self.sill failed")
        if not isinstance(self.is_rotation_fixed, bool):
            raise ValidationFailed("self.is_rotation_fixed is not bool")
        if not isinstance(self.structures, list):
            raise ValidationFailed("self.structures is not a list")
        for v in self.structures:
            if not isinstance(v, Variogram_V1_0_1_Structures):
                raise ValidationFailed("v is not Variogram_V1_0_1_Structures")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/variogram/1.0.1/variogram.schema.json":
            raise ValidationFailed('self.schema == "/objects/variogram/1.0.1/variogram.schema.json" failed')
        if not isinstance(self.nugget, float):
            raise ValidationFailed("self.nugget is not float")
        if not 0.0 <= self.nugget:
            raise ValidationFailed("0.0 <= self.nugget failed")
        if self.data_variance is not None:
            if not isinstance(self.data_variance, float):
                raise ValidationFailed("self.data_variance is not float")
            if not 0.0 <= self.data_variance:
                raise ValidationFailed("0.0 <= self.data_variance failed")
        if self.modelling_space is not None:
            if not isinstance(self.modelling_space, str):
                raise ValidationFailed("self.modelling_space is not str")
            if self.modelling_space not in ("data", "normalscore"):
                raise ValidationFailed('self.modelling_space in ("data", "normalscore") failed')
        if self.domain is not None:
            if not isinstance(self.domain, str):
                raise ValidationFailed("self.domain is not str")
        if self.attribute is not None:
            if not isinstance(self.attribute, str):
                raise ValidationFailed("self.attribute is not str")


Variogram_V1_1_0_Structures = (
    VariogramExponentialStructure_V1_1_0
    | VariogramGaussianStructure_V1_1_0
    | VariogramGeneralisedcauchyStructure_V1_1_0
    | VariogramSphericalStructure_V1_1_0
    | VariogramSpheroidalStructure_V1_1_0
    | VariogramLinearStructure_V1_1_0
    | VariogramCubicStructure_V1_1_0
)


@dataclasses.dataclass(kw_only=True)
class Variogram_V1_1_0(BaseObjectProperties_V1_0_1):
    """Variogram model and associated metadata. The variogram model is defined by the nugget, and multiple structures using the leapfrog-convention rotation. See struture and rotation components for additional details."""

    SCHEMA_ID = "/objects/variogram/1.1.0/variogram.schema.json"

    sill: float
    """The variance of the variogram. This must be within a very small tolerance of the nugget plus the sum of all structure's contributions."""
    is_rotation_fixed: bool
    """Boolean value specifying whether all structure's rotations are the same."""
    structures: list[Variogram_V1_1_0_Structures]
    """A list of at least one mathematical model, which are parameterised to represent the spatial structure of the variogram model."""
    schema: str = "/objects/variogram/1.1.0/variogram.schema.json"
    nugget: float = 0.0
    """The variance between two samples separated by near-zero lag distance, representing the randomness present. When plotted, this value is the y-intercept."""
    data_variance: float | None = None
    """The variance of the data, if different from the sill value, this is used for normalising or rescaling the variogram"""
    modelling_space: str | None = None
    """The modelling space the variogram model was fitted in either data for original units or normalscore for gaussian space."""
    domain: str | None = None
    """The domain the variogram is modelled for"""
    attribute: str | None = None
    """The attribute the variogram is modelled for"""

    def __post_init__(self):
        BaseObjectProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.sill, float):
            raise ValidationFailed("self.sill is not float")
        if not 0.0 <= self.sill:
            raise ValidationFailed("0.0 <= self.sill failed")
        if not isinstance(self.is_rotation_fixed, bool):
            raise ValidationFailed("self.is_rotation_fixed is not bool")
        if not isinstance(self.structures, list):
            raise ValidationFailed("self.structures is not a list")
        for v in self.structures:
            if not isinstance(v, Variogram_V1_1_0_Structures):
                raise ValidationFailed("v is not Variogram_V1_1_0_Structures")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/variogram/1.1.0/variogram.schema.json":
            raise ValidationFailed('self.schema == "/objects/variogram/1.1.0/variogram.schema.json" failed')
        if not isinstance(self.nugget, float):
            raise ValidationFailed("self.nugget is not float")
        if not 0.0 <= self.nugget:
            raise ValidationFailed("0.0 <= self.nugget failed")
        if self.data_variance is not None:
            if not isinstance(self.data_variance, float):
                raise ValidationFailed("self.data_variance is not float")
            if not 0.0 <= self.data_variance:
                raise ValidationFailed("0.0 <= self.data_variance failed")
        if self.modelling_space is not None:
            if not isinstance(self.modelling_space, str):
                raise ValidationFailed("self.modelling_space is not str")
            if self.modelling_space not in ("data", "normalscore"):
                raise ValidationFailed('self.modelling_space in ("data", "normalscore") failed')
        if self.domain is not None:
            if not isinstance(self.domain, str):
                raise ValidationFailed("self.domain is not str")
        if self.attribute is not None:
            if not isinstance(self.attribute, str):
                raise ValidationFailed("self.attribute is not str")


Variogram_V1_2_0_Structures = (
    VariogramExponentialStructure_V1_1_0
    | VariogramGaussianStructure_V1_1_0
    | VariogramGeneralisedcauchyStructure_V1_1_0
    | VariogramSphericalStructure_V1_1_0
    | VariogramSpheroidalStructure_V1_1_0
    | VariogramLinearStructure_V1_1_0
    | VariogramCubicStructure_V1_1_0
)


@dataclasses.dataclass(kw_only=True)
class Variogram_V1_2_0(BaseObjectProperties_V1_1_0):
    """Variogram model and associated metadata. The variogram model is defined by the nugget, and multiple structures using the leapfrog-convention rotation. See struture and rotation components for additional details."""

    SCHEMA_ID = "/objects/variogram/1.2.0/variogram.schema.json"

    sill: float
    """The variance of the variogram. This must be within a very small tolerance of the nugget plus the sum of all structure's contributions."""
    is_rotation_fixed: bool
    """Boolean value specifying whether all structure's rotations are the same."""
    structures: list[Variogram_V1_2_0_Structures]
    """A list of at least one mathematical model, which are parameterised to represent the spatial structure of the variogram model."""
    schema: str = "/objects/variogram/1.2.0/variogram.schema.json"
    nugget: float = 0.0
    """The variance between two samples separated by near-zero lag distance, representing the randomness present. When plotted, this value is the y-intercept."""
    data_variance: float | None = None
    """The variance of the data, if different from the sill value, this is used for normalising or rescaling the variogram"""
    modelling_space: str | None = None
    """The modelling space the variogram model was fitted in either data for original units or normalscore for gaussian space."""
    domain: str | None = None
    """The domain the variogram is modelled for"""
    attribute: str | None = None
    """The attribute the variogram is modelled for"""

    def __post_init__(self):
        BaseObjectProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.sill, float):
            raise ValidationFailed("self.sill is not float")
        if not 0.0 <= self.sill:
            raise ValidationFailed("0.0 <= self.sill failed")
        if not isinstance(self.is_rotation_fixed, bool):
            raise ValidationFailed("self.is_rotation_fixed is not bool")
        if not isinstance(self.structures, list):
            raise ValidationFailed("self.structures is not a list")
        for v in self.structures:
            if not isinstance(v, Variogram_V1_2_0_Structures):
                raise ValidationFailed("v is not Variogram_V1_2_0_Structures")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/variogram/1.2.0/variogram.schema.json":
            raise ValidationFailed('self.schema == "/objects/variogram/1.2.0/variogram.schema.json" failed')
        if not isinstance(self.nugget, float):
            raise ValidationFailed("self.nugget is not float")
        if not 0.0 <= self.nugget:
            raise ValidationFailed("0.0 <= self.nugget failed")
        if self.data_variance is not None:
            if not isinstance(self.data_variance, float):
                raise ValidationFailed("self.data_variance is not float")
            if not 0.0 <= self.data_variance:
                raise ValidationFailed("0.0 <= self.data_variance failed")
        if self.modelling_space is not None:
            if not isinstance(self.modelling_space, str):
                raise ValidationFailed("self.modelling_space is not str")
            if self.modelling_space not in ("data", "normalscore"):
                raise ValidationFailed('self.modelling_space in ("data", "normalscore") failed')
        if self.domain is not None:
            if not isinstance(self.domain, str):
                raise ValidationFailed("self.domain is not str")
        if self.attribute is not None:
            if not isinstance(self.attribute, str):
                raise ValidationFailed("self.attribute is not str")
