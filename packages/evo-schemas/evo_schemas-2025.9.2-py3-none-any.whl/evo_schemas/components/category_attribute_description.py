import dataclasses
import typing

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class CategoryAttributeDescription_V1_0_1(Serialiser):
    """General information for a categorical attribute."""

    SCHEMA_ID = "/components/category-attribute-description/1.0.1/category-attribute-description.schema.json"

    discipline: str
    """Discipline"""
    type: str
    """Type"""
    extensions: dict[str, typing.Any] | None = None
    """Extended properties that may be associated to the attribute, but not specified in the schema"""
    tags: dict[str, str] | None = None
    """Key-value pairs of user-defined metadata"""

    def __post_init__(self):
        if not isinstance(self.discipline, str):
            raise ValidationFailed("self.discipline is not str")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.extensions is not None:
            if not isinstance(self.extensions, dict):
                raise ValidationFailed("self.extensions is not a dict")
            for k in self.extensions:
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
        if self.tags is not None:
            if not isinstance(self.tags, dict):
                raise ValidationFailed("self.tags is not a dict")
            for k, v in self.tags.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, str):
                    raise ValidationFailed("v is not str")
