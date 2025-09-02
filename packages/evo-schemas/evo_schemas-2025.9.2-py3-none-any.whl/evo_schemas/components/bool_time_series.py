import dataclasses

from ..elements.bool_array_md import BoolArrayMd_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0
from .time_step_attribute import TimeStepAttribute_V1_0_1, TimeStepAttribute_V1_1_0


@dataclasses.dataclass(kw_only=True)
class BoolTimeSeries_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """An attribute that describes a bool time series."""

    SCHEMA_ID = "/components/bool-time-series/1.1.0/bool-time-series.schema.json"

    num_time_steps: int
    """Number of time steps."""
    time_step: TimeStepAttribute_V1_1_0
    """Time step attribute component."""
    values: BoolArrayMd_V1_0_1
    """The values of the series where 'num_time_steps' is the width of the array."""
    attribute_type: str = "bool_time_series"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.num_time_steps, int):
            raise ValidationFailed("self.num_time_steps is not int")
        if not 0 <= self.num_time_steps:
            raise ValidationFailed("0 <= self.num_time_steps failed")
        if not isinstance(self.time_step, TimeStepAttribute_V1_1_0):
            raise ValidationFailed("self.time_step is not TimeStepAttribute_V1_1_0")
        if not isinstance(self.values, BoolArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not BoolArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "bool_time_series":
            raise ValidationFailed('self.attribute_type == "bool_time_series" failed')


@dataclasses.dataclass(kw_only=True)
class BoolTimeSeries_V1_0_1(Serialiser):
    """An attribute that describes a bool time series."""

    SCHEMA_ID = "/components/bool-time-series/1.0.1/bool-time-series.schema.json"

    key: str
    """The key"""
    num_time_steps: int
    """Number of time steps."""
    time_step: TimeStepAttribute_V1_0_1
    """Time step attribute component."""
    values: BoolArrayMd_V1_0_1
    """The values of the series where 'num_time_steps' is the width of the array."""
    attribute_type: str = "bool_time_series"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.num_time_steps, int):
            raise ValidationFailed("self.num_time_steps is not int")
        if not 0 <= self.num_time_steps:
            raise ValidationFailed("0 <= self.num_time_steps failed")
        if not isinstance(self.time_step, TimeStepAttribute_V1_0_1):
            raise ValidationFailed("self.time_step is not TimeStepAttribute_V1_0_1")
        if not isinstance(self.values, BoolArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not BoolArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "bool_time_series":
            raise ValidationFailed('self.attribute_type == "bool_time_series" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
