import dataclasses

from ..elements.date_time_array import DateTimeArray_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0
from .nan_categorical import NanCategorical_V1_0_1


@dataclasses.dataclass(kw_only=True)
class DateTimeAttribute_V1_0_1(Serialiser):
    """An attribute for a range of timestamps."""

    SCHEMA_ID = "/components/date-time-attribute/1.0.1/date-time-attribute.schema.json"

    name: str
    """The name of the attribute."""
    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    values: DateTimeArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "date_time"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.values, DateTimeArray_V1_0_1):
            raise ValidationFailed("self.values is not DateTimeArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "date_time":
            raise ValidationFailed('self.attribute_type == "date_time" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class DateTimeAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """An attribute for a range of timestamps."""

    SCHEMA_ID = "/components/date-time-attribute/1.1.0/date-time-attribute.schema.json"

    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    values: DateTimeArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "date_time"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.values, DateTimeArray_V1_0_1):
            raise ValidationFailed("self.values is not DateTimeArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "date_time":
            raise ValidationFailed('self.attribute_type == "date_time" failed')
