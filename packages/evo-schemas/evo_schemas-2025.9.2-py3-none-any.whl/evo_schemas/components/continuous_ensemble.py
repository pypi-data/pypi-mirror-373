import dataclasses

from ..elements.float_array_md import FloatArrayMd_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0
from .nan_continuous import NanContinuous_V1_0_1


@dataclasses.dataclass(kw_only=True)
class ContinuousEnsemble_V1_0_1(Serialiser):
    """Continuous ensemble."""

    SCHEMA_ID = "/components/continuous-ensemble/1.0.1/continuous-ensemble.schema.json"

    name: str
    """The name of the attribute."""
    nan_description: NanContinuous_V1_0_1
    """Describes the values used to designate not-a-number."""
    values: FloatArrayMd_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "ensemble_continuous"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.nan_description, NanContinuous_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanContinuous_V1_0_1")
        if not isinstance(self.values, FloatArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not FloatArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "ensemble_continuous":
            raise ValidationFailed('self.attribute_type == "ensemble_continuous" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class ContinuousEnsemble_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """Continuous ensemble."""

    SCHEMA_ID = "/components/continuous-ensemble/1.1.0/continuous-ensemble.schema.json"

    nan_description: NanContinuous_V1_0_1
    """Describes the values used to designate not-a-number."""
    values: FloatArrayMd_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "ensemble_continuous"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.nan_description, NanContinuous_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanContinuous_V1_0_1")
        if not isinstance(self.values, FloatArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not FloatArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "ensemble_continuous":
            raise ValidationFailed('self.attribute_type == "ensemble_continuous" failed')
