import dataclasses

from ..components.attribute_description import AttributeDescription_V1_0_1
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.cumulative_distribution_function import CumulativeDistributionFunction_V1_0_1
from ..components.rotation import Rotation_V1_0_1, Rotation_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block_Block(Serialiser):
    """Block option."""

    size_x: float
    """Size in x direction"""
    size_y: float
    """Size in y direction"""
    size_z: float
    """Size in x direction"""
    rotation: Rotation_V1_0_1 | None = None
    """Rotation."""

    def __post_init__(self):
        if not isinstance(self.size_x, float):
            raise ValidationFailed("self.size_x is not float")
        if not isinstance(self.size_y, float):
            raise ValidationFailed("self.size_y is not float")
        if not isinstance(self.size_z, float):
            raise ValidationFailed("self.size_z is not float")
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_0_1):
                raise ValidationFailed("self.rotation is not Rotation_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block(Serialiser):
    block: NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block_Block
    """Block option."""

    def __post_init__(self):
        if not isinstance(self.block, NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block_Block):
            raise ValidationFailed(
                "self.block is not NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block_Block"
            )


NonParametricContinuousCumulativeDistribution_V1_0_1_Support = (
    str | NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block
)


def is_non_parametric_continuous_cumulative_distribution_v1_0_1_support(value):
    if isinstance(value, NonParametricContinuousCumulativeDistribution_V1_0_1_Support_Block):
        return True
    if isinstance(value, str) and value == "point":
        # Point option.
        return True
    if isinstance(value, str) and value == "other":
        # Other option.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A description of a non parametric continuous cumulative distribution."""

    SCHEMA_ID = "/objects/non-parametric-continuous-cumulative-distribution/1.0.1/non-parametric-continuous-cumulative-distribution.schema.json"

    cdf: CumulativeDistributionFunction_V1_0_1
    """Cumulative distribution function."""
    is_declustered: bool
    """Is declustered."""
    support: NonParametricContinuousCumulativeDistribution_V1_0_1_Support
    """Support options."""
    schema: str = (
        "/objects/non-parametric-continuous-cumulative-distribution/1.0.1/non-parametric-continuous-cumulative-distribution.schema.json"
    )
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.cdf, CumulativeDistributionFunction_V1_0_1):
            raise ValidationFailed("self.cdf is not CumulativeDistributionFunction_V1_0_1")
        if not isinstance(self.is_declustered, bool):
            raise ValidationFailed("self.is_declustered is not bool")
        if not is_non_parametric_continuous_cumulative_distribution_v1_0_1_support(self.support):
            raise ValidationFailed(
                "is_non_parametric_continuous_cumulative_distribution_v1_0_1_support(self.support) failed"
            )
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if (
            not self.schema
            == "/objects/non-parametric-continuous-cumulative-distribution/1.0.1/non-parametric-continuous-cumulative-distribution.schema.json"
        ):
            raise ValidationFailed(
                'self.schema == "/objects/non-parametric-continuous-cumulative-distribution/1.0.1/non-parametric-continuous-cumulative-distribution.schema.json" failed'
            )
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block_Block(Serialiser):
    """Block option."""

    size_x: float
    """Size in x direction"""
    size_y: float
    """Size in y direction"""
    size_z: float
    """Size in x direction"""
    rotation: Rotation_V1_1_0 | None = None
    """Rotation."""

    def __post_init__(self):
        if not isinstance(self.size_x, float):
            raise ValidationFailed("self.size_x is not float")
        if not isinstance(self.size_y, float):
            raise ValidationFailed("self.size_y is not float")
        if not isinstance(self.size_z, float):
            raise ValidationFailed("self.size_z is not float")
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block(Serialiser):
    block: NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block_Block
    """Block option."""

    def __post_init__(self):
        if not isinstance(self.block, NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block_Block):
            raise ValidationFailed(
                "self.block is not NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block_Block"
            )


NonParametricContinuousCumulativeDistribution_V1_1_0_Support = (
    str | NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block
)


def is_non_parametric_continuous_cumulative_distribution_v1_1_0_support(value):
    if isinstance(value, NonParametricContinuousCumulativeDistribution_V1_1_0_Support_Block):
        return True
    if isinstance(value, str) and value == "point":
        # Point option.
        return True
    if isinstance(value, str) and value == "other":
        # Other option.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A description of a non parametric continuous cumulative distribution."""

    SCHEMA_ID = "/objects/non-parametric-continuous-cumulative-distribution/1.1.0/non-parametric-continuous-cumulative-distribution.schema.json"

    cdf: CumulativeDistributionFunction_V1_0_1
    """Cumulative distribution function."""
    is_declustered: bool
    """Is declustered."""
    support: NonParametricContinuousCumulativeDistribution_V1_1_0_Support
    """Support options."""
    schema: str = (
        "/objects/non-parametric-continuous-cumulative-distribution/1.1.0/non-parametric-continuous-cumulative-distribution.schema.json"
    )
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.cdf, CumulativeDistributionFunction_V1_0_1):
            raise ValidationFailed("self.cdf is not CumulativeDistributionFunction_V1_0_1")
        if not isinstance(self.is_declustered, bool):
            raise ValidationFailed("self.is_declustered is not bool")
        if not is_non_parametric_continuous_cumulative_distribution_v1_1_0_support(self.support):
            raise ValidationFailed(
                "is_non_parametric_continuous_cumulative_distribution_v1_1_0_support(self.support) failed"
            )
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if (
            not self.schema
            == "/objects/non-parametric-continuous-cumulative-distribution/1.1.0/non-parametric-continuous-cumulative-distribution.schema.json"
        ):
            raise ValidationFailed(
                'self.schema == "/objects/non-parametric-continuous-cumulative-distribution/1.1.0/non-parametric-continuous-cumulative-distribution.schema.json" failed'
            )
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block_Block(Serialiser):
    """Block option."""

    size_x: float
    """Size in x direction"""
    size_y: float
    """Size in y direction"""
    size_z: float
    """Size in x direction"""
    rotation: Rotation_V1_1_0 | None = None
    """Rotation."""

    def __post_init__(self):
        if not isinstance(self.size_x, float):
            raise ValidationFailed("self.size_x is not float")
        if not isinstance(self.size_y, float):
            raise ValidationFailed("self.size_y is not float")
        if not isinstance(self.size_z, float):
            raise ValidationFailed("self.size_z is not float")
        if self.rotation is not None:
            if not isinstance(self.rotation, Rotation_V1_1_0):
                raise ValidationFailed("self.rotation is not Rotation_V1_1_0")


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block(Serialiser):
    block: NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block_Block
    """Block option."""

    def __post_init__(self):
        if not isinstance(self.block, NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block_Block):
            raise ValidationFailed(
                "self.block is not NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block_Block"
            )


NonParametricContinuousCumulativeDistribution_V1_2_0_Support = (
    str | NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block
)


def is_non_parametric_continuous_cumulative_distribution_v1_2_0_support(value):
    if isinstance(value, NonParametricContinuousCumulativeDistribution_V1_2_0_Support_Block):
        return True
    if isinstance(value, str) and value == "point":
        # Point option.
        return True
    if isinstance(value, str) and value == "other":
        # Other option.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class NonParametricContinuousCumulativeDistribution_V1_2_0(BaseSpatialDataProperties_V1_1_0):
    """A description of a non parametric continuous cumulative distribution."""

    SCHEMA_ID = "/objects/non-parametric-continuous-cumulative-distribution/1.2.0/non-parametric-continuous-cumulative-distribution.schema.json"

    cdf: CumulativeDistributionFunction_V1_0_1
    """Cumulative distribution function."""
    is_declustered: bool
    """Is declustered."""
    support: NonParametricContinuousCumulativeDistribution_V1_2_0_Support
    """Support options."""
    schema: str = (
        "/objects/non-parametric-continuous-cumulative-distribution/1.2.0/non-parametric-continuous-cumulative-distribution.schema.json"
    )
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.cdf, CumulativeDistributionFunction_V1_0_1):
            raise ValidationFailed("self.cdf is not CumulativeDistributionFunction_V1_0_1")
        if not isinstance(self.is_declustered, bool):
            raise ValidationFailed("self.is_declustered is not bool")
        if not is_non_parametric_continuous_cumulative_distribution_v1_2_0_support(self.support):
            raise ValidationFailed(
                "is_non_parametric_continuous_cumulative_distribution_v1_2_0_support(self.support) failed"
            )
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if (
            not self.schema
            == "/objects/non-parametric-continuous-cumulative-distribution/1.2.0/non-parametric-continuous-cumulative-distribution.schema.json"
        ):
            raise ValidationFailed(
                'self.schema == "/objects/non-parametric-continuous-cumulative-distribution/1.2.0/non-parametric-continuous-cumulative-distribution.schema.json" failed'
            )
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
