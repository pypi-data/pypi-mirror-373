import dataclasses

from ..elements.integer_array_md import IntegerArrayMd_V1_0_1
from ..elements.lookup_table import LookupTable_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .base_category_attribute import BaseCategoryAttribute_V1_0_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1
from .nan_categorical import NanCategorical_V1_0_1


@dataclasses.dataclass(kw_only=True)
class CategoryEnsemble_V1_0_1(Serialiser):
    """Category ensemble."""

    SCHEMA_ID = "/components/category-ensemble/1.0.1/category-ensemble.schema.json"

    name: str
    """The name of the attribute."""
    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    table: LookupTable_V1_0_1
    """Lookup table associated with the attributes."""
    values: IntegerArrayMd_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "ensemble_category"
    """Type of the attribute."""
    attribute_description: CategoryAttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.table, LookupTable_V1_0_1):
            raise ValidationFailed("self.table is not LookupTable_V1_0_1")
        if not isinstance(self.values, IntegerArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not IntegerArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "ensemble_category":
            raise ValidationFailed('self.attribute_type == "ensemble_category" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, CategoryAttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not CategoryAttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class CategoryEnsemble_V1_1_0(BaseCategoryAttribute_V1_0_0):
    """Category ensemble."""

    SCHEMA_ID = "/components/category-ensemble/1.1.0/category-ensemble.schema.json"

    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    table: LookupTable_V1_0_1
    """Lookup table associated with the attributes."""
    values: IntegerArrayMd_V1_0_1
    """The values of the attributes."""
    attribute_type: str = "ensemble_category"

    def __post_init__(self):
        BaseCategoryAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.table, LookupTable_V1_0_1):
            raise ValidationFailed("self.table is not LookupTable_V1_0_1")
        if not isinstance(self.values, IntegerArrayMd_V1_0_1):
            raise ValidationFailed("self.values is not IntegerArrayMd_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "ensemble_category":
            raise ValidationFailed('self.attribute_type == "ensemble_category" failed')
