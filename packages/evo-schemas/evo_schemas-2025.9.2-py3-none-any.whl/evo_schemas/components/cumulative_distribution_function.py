import dataclasses

from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel_PowerModel(Serialiser):
    """Power model"""

    min: float
    """minimum"""
    power: float
    """power"""

    def __post_init__(self):
        if not isinstance(self.min, float):
            raise ValidationFailed("self.min is not float")
        if not isinstance(self.power, float):
            raise ValidationFailed("self.power is not float")
        if not 1.0 <= self.power:
            raise ValidationFailed("1.0 <= self.power failed")


@dataclasses.dataclass(kw_only=True)
class CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel(Serialiser):
    power_model: CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel_PowerModel
    """Power model"""

    def __post_init__(self):
        if not isinstance(
            self.power_model, CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel_PowerModel
        ):
            raise ValidationFailed(
                "self.power_model is not CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel_PowerModel"
            )


CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation = (
    CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel | str
)


def is_cumulative_distribution_function_v1_0_1_lower_tail_extrapolation(value):
    if isinstance(value, CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel):
        return True
    if isinstance(value, str) and value == "no_extrapolation":
        # No extrapolation.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel_PowerModel(Serialiser):
    """Power model"""

    max: float
    """maximum"""
    power: float
    """power"""

    def __post_init__(self):
        if not isinstance(self.max, float):
            raise ValidationFailed("self.max is not float")
        if not isinstance(self.power, float):
            raise ValidationFailed("self.power is not float")
        if not 0.0 < self.power:
            raise ValidationFailed("0.0 < self.power failed")
        if not self.power <= 1.0:
            raise ValidationFailed("self.power <= 1.0 failed")


@dataclasses.dataclass(kw_only=True)
class CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel(Serialiser):
    power_model: CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel_PowerModel
    """Power model"""

    def __post_init__(self):
        if not isinstance(
            self.power_model, CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel_PowerModel
        ):
            raise ValidationFailed(
                "self.power_model is not CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel_PowerModel"
            )


CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation = (
    CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel | str
)


def is_cumulative_distribution_function_v1_0_1_upper_tail_extrapolation(value):
    if isinstance(value, CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel):
        return True
    if isinstance(value, str) and value == "no_extrapolation":
        # No extrapolation.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class CumulativeDistributionFunction_V1_0_1(Serialiser):
    """Cumulative distribution function (CDF)."""

    SCHEMA_ID = "/components/cumulative-distribution-function/1.0.1/cumulative-distribution-function.schema.json"

    values: FloatArray2_V1_0_1
    """Array of values and probabilities. Columns: values, probabilities."""
    lower_tail_extrapolation: CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation
    """Lower tail extrapolation."""
    upper_tail_extrapolation: CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation
    """Upper tail extrapolation."""

    def __post_init__(self):
        if not isinstance(self.values, FloatArray2_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray2_V1_0_1")
        if not is_cumulative_distribution_function_v1_0_1_lower_tail_extrapolation(self.lower_tail_extrapolation):
            raise ValidationFailed(
                "is_cumulative_distribution_function_v1_0_1_lower_tail_extrapolation(self.lower_tail_extrapolation) failed"
            )
        if not is_cumulative_distribution_function_v1_0_1_upper_tail_extrapolation(self.upper_tail_extrapolation):
            raise ValidationFailed(
                "is_cumulative_distribution_function_v1_0_1_upper_tail_extrapolation(self.upper_tail_extrapolation) failed"
            )
