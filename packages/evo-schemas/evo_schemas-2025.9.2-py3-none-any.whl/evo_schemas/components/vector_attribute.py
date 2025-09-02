import dataclasses

from ..elements.float_array_md import FloatArrayMd_V1_0_1
from ..elements.serialiser import ValidationFailed
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0
from .nan_continuous import NanContinuous_V1_0_1


@dataclasses.dataclass(kw_only=True)
class VectorAttribute_V1_0_0(BaseContinuousAttribute_V1_0_0):
    """An attribute containing an N-dimensional vector."""

    SCHEMA_ID = "/components/vector-attribute/1.0.0/vector-attribute.schema.json"

    nan_description: NanContinuous_V1_0_1
    """Describes the values used to designate not-a-number."""
    values: FloatArrayMd_V1_0_1
    """The vector array, where each row is a vector."""
    attribute_type: str = "vector"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.nan_description, NanContinuous_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanContinuous_V1_0_1")
        if not isinstance(self.values, FloatArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not FloatArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "vector":
            raise ValidationFailed('self.attribute_type == "vector" failed')
