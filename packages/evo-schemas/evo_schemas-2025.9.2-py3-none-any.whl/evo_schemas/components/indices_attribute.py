import dataclasses
import re
import uuid

from ..elements.index_array_1 import IndexArray1_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class IndicesAttribute_V1_1_0_RelatedObject(Serialiser):
    """Related Geoscience Object."""

    uuid: uuid.UUID
    """Unique identifier of related Geoscience Object."""
    version: str
    """Geoscience object version."""
    component: str
    """component type."""

    def __post_init__(self):
        if not isinstance(self.uuid, uuid.UUID):
            raise ValidationFailed("self.uuid is not uuid.UUID")
        if not isinstance(self.version, str):
            raise ValidationFailed("self.version is not str")
        if not re.match(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$", self.version):
            raise ValidationFailed('re.match(r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$", self.version) failed')
        if not isinstance(self.component, str):
            raise ValidationFailed("self.component is not str")


@dataclasses.dataclass(kw_only=True)
class IndicesAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """An attribute for a range of indices."""

    SCHEMA_ID = "/components/indices-attribute/1.1.0/indices-attribute.schema.json"

    values: IndexArray1_V1_0_1
    """The values of the attributes."""
    related_object: IndicesAttribute_V1_1_0_RelatedObject
    """Related Geoscience Object."""
    attribute_type: str = "indices"

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, IndexArray1_V1_0_1):
            raise ValidationFailed("self.values is not IndexArray1_V1_0_1")
        if not isinstance(self.related_object, IndicesAttribute_V1_1_0_RelatedObject):
            raise ValidationFailed("self.related_object is not IndicesAttribute_V1_1_0_RelatedObject")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "indices":
            raise ValidationFailed('self.attribute_type == "indices" failed')


@dataclasses.dataclass(kw_only=True)
class IndicesAttribute_V1_0_1_RelatedObject(Serialiser):
    """Related Geoscience Object."""

    uuid: uuid.UUID
    """Unique identifier of related Geoscience Object."""
    version: str
    """Geoscience object version."""
    component: str
    """component type."""

    def __post_init__(self):
        if not isinstance(self.uuid, uuid.UUID):
            raise ValidationFailed("self.uuid is not uuid.UUID")
        if not isinstance(self.version, str):
            raise ValidationFailed("self.version is not str")
        if not re.match(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$", self.version):
            raise ValidationFailed('re.match(r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$", self.version) failed')
        if not isinstance(self.component, str):
            raise ValidationFailed("self.component is not str")


@dataclasses.dataclass(kw_only=True)
class IndicesAttribute_V1_0_1(Serialiser):
    """An attribute for a range of indices."""

    SCHEMA_ID = "/components/indices-attribute/1.0.1/indices-attribute.schema.json"

    name: str
    """The name of the attribute."""
    values: IndexArray1_V1_0_1
    """The values of the attributes."""
    related_object: IndicesAttribute_V1_0_1_RelatedObject
    """Related Geoscience Object."""
    attribute_type: str = "indices"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, IndexArray1_V1_0_1):
            raise ValidationFailed("self.values is not IndexArray1_V1_0_1")
        if not isinstance(self.related_object, IndicesAttribute_V1_0_1_RelatedObject):
            raise ValidationFailed("self.related_object is not IndicesAttribute_V1_0_1_RelatedObject")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "indices":
            raise ValidationFailed('self.attribute_type == "indices" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
