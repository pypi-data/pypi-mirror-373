import dataclasses

from ..elements.serialiser import ValidationFailed
from .base_category_attribute import BaseCategoryAttribute_V1_0_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1
from .category_data import CategoryData_V1_0_1
from .nan_categorical import NanCategorical_V1_0_1


@dataclasses.dataclass(kw_only=True)
class CategoryAttribute_V1_0_1(CategoryData_V1_0_1):
    """An attribute that describes a category."""

    SCHEMA_ID = "/components/category-attribute/1.0.1/category-attribute.schema.json"

    name: str
    """The name of the attribute."""
    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    attribute_type: str = "category"
    """Type of the attribute."""
    attribute_description: CategoryAttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        CategoryData_V1_0_1.__post_init__(self)
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "category":
            raise ValidationFailed('self.attribute_type == "category" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, CategoryAttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not CategoryAttributeDescription_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class CategoryAttribute_V1_1_0(BaseCategoryAttribute_V1_0_0, CategoryData_V1_0_1):
    """An attribute that describes a category."""

    SCHEMA_ID = "/components/category-attribute/1.1.0/category-attribute.schema.json"

    nan_description: NanCategorical_V1_0_1
    """Describes the values used to designate not-a-number."""
    attribute_type: str = "category"

    def __post_init__(self):
        BaseCategoryAttribute_V1_0_0.__post_init__(self)
        CategoryData_V1_0_1.__post_init__(self)
        if not isinstance(self.nan_description, NanCategorical_V1_0_1):
            raise ValidationFailed("self.nan_description is not NanCategorical_V1_0_1")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "category":
            raise ValidationFailed('self.attribute_type == "category" failed')
