import dataclasses
import typing

from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit import Unit_V1_0_1, is_unit_v1_0_1


@dataclasses.dataclass(kw_only=True)
class AttributeDescription_V1_0_1(Serialiser):
    """General information for an attribute."""

    SCHEMA_ID = "/components/attribute-description/1.0.1/attribute-description.schema.json"

    discipline: str
    """Discipline attribute comes from, e.g. Geochemistry, Geophysics, Geotechnical, Geology, Structural. None if not known"""
    type: str
    """Type of the attribute, e.g. Gold, Azimuth, Resistivity"""
    unit: Unit_V1_0_1 | None = None
    """Unit"""
    scale: str | None = None
    """Scale of the attribute e.g. log10, log2, exp, lin"""
    extensions: dict[str, typing.Any] | None = None
    """Extended properties that may be associated to the attribute, but not specified in the schema"""
    tags: dict[str, str] | None = None
    """Key-value pairs of user-defined metadata"""

    def __post_init__(self):
        if not isinstance(self.discipline, str):
            raise ValidationFailed("self.discipline is not str")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.unit is not None:
            if not is_unit_v1_0_1(self.unit):
                raise ValidationFailed("is_unit_v1_0_1(self.unit) failed")
        if self.scale is not None:
            if not isinstance(self.scale, str):
                raise ValidationFailed("self.scale is not str")
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
