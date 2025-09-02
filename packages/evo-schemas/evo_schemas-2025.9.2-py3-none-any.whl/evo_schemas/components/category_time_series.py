import dataclasses

from ..elements.integer_array_md import IntegerArrayMd_V1_0_1
from ..elements.lookup_table import LookupTable_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .base_category_attribute import BaseCategoryAttribute_V1_0_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1
from .nan_categorical import NanCategorical_V1_0_1
from .time_step_attribute import TimeStepAttribute_V1_0_1, TimeStepAttribute_V1_1_0


@dataclasses.dataclass(kw_only=True)
class CategoryTimeSeries_V1_1_0(BaseCategoryAttribute_V1_0_0):
    """An attribute that describes a category time series."""

    SCHEMA_ID = "/components/category-time-series/1.1.0/category-time-series.schema.json"

    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    num_time_steps: int
    """Number of time steps."""
    time_step: TimeStepAttribute_V1_1_0
    """Time step attribute component."""
    values: IntegerArrayMd_V1_0_1
    """The values of the series where 'num_time_steps' is the width of the array."""
    table: LookupTable_V1_0_1
    """Lookup table associated with the attributes."""
    attribute_type: str = "categoral_time_series"

    def __post_init__(self):
        BaseCategoryAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.num_time_steps, int):
            raise ValidationFailed("self.num_time_steps is not int")
        if not 0 <= self.num_time_steps:
            raise ValidationFailed("0 <= self.num_time_steps failed")
        if not isinstance(self.time_step, TimeStepAttribute_V1_1_0):
            raise ValidationFailed("self.time_step is not TimeStepAttribute_V1_1_0")
        if not isinstance(self.values, IntegerArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not IntegerArrayMd_V1_0_1")
        if not isinstance(self.table, LookupTable_V1_0_1):
            raise ValidationFailed("self.table is not LookupTable_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "categoral_time_series":
            raise ValidationFailed('self.attribute_type == "categoral_time_series" failed')


@dataclasses.dataclass(kw_only=True)
class CategoryTimeSeries_V1_0_1(Serialiser):
    """An attribute that describes a category time series."""

    SCHEMA_ID = "/components/category-time-series/1.0.1/category-time-series.schema.json"

    key: str
    """The key"""
    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    num_time_steps: int
    """Number of time steps."""
    time_step: TimeStepAttribute_V1_0_1
    """Time step attribute component."""
    values: IntegerArrayMd_V1_0_1
    """The values of the series where 'num_time_steps' is the width of the array."""
    table: LookupTable_V1_0_1
    """Lookup table associated with the attributes."""
    attribute_type: str = "categoral_time_series"
    """Type of the attribute."""
    attribute_description: CategoryAttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.num_time_steps, int):
            raise ValidationFailed("self.num_time_steps is not int")
        if not 0 <= self.num_time_steps:
            raise ValidationFailed("0 <= self.num_time_steps failed")
        if not isinstance(self.time_step, TimeStepAttribute_V1_0_1):
            raise ValidationFailed("self.time_step is not TimeStepAttribute_V1_0_1")
        if not isinstance(self.values, IntegerArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not IntegerArrayMd_V1_0_1")
        if not isinstance(self.table, LookupTable_V1_0_1):
            raise ValidationFailed("self.table is not LookupTable_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "categoral_time_series":
            raise ValidationFailed('self.attribute_type == "categoral_time_series" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, CategoryAttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not CategoryAttributeDescription_V1_0_1")
