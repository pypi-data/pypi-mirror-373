import dataclasses

from ..elements.date_time_array import DateTimeArray_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class TimeStepDateTimeAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """An attribute for a range of timestamps in a time series."""

    SCHEMA_ID = "/components/time-step-date-time-attribute/1.1.0/time-step-date-time-attribute.schema.json"

    values: DateTimeArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "date_time"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, DateTimeArray_V1_0_1):
            raise ValidationFailed("self.values is not DateTimeArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "date_time":
            raise ValidationFailed('self.attribute_type == "date_time" failed')


@dataclasses.dataclass(kw_only=True)
class TimeStepDateTimeAttribute_V1_0_1(Serialiser):
    """An attribute for a range of timestamps in a time series."""

    SCHEMA_ID = "/components/time-step-date-time-attribute/1.0.1/time-step-date-time-attribute.schema.json"

    name: str
    """The name of the attribute."""
    values: DateTimeArray_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "date_time"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, DateTimeArray_V1_0_1):
            raise ValidationFailed("self.values is not DateTimeArray_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "date_time":
            raise ValidationFailed('self.attribute_type == "date_time" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
