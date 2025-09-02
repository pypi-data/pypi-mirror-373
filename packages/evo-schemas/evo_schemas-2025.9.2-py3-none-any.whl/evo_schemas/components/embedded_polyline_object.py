import dataclasses

from ..elements.reversible_index import ReversibleIndex_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class EmbeddedPolylineObject_V1_0_0(Serialiser):
    """A base polyline/polygon object referencing parts in an embedded-line-geometry."""

    SCHEMA_ID = "/components/embedded-polyline-object/1.0.0/embedded-polyline-object.schema.json"

    name: str
    """Name of the object."""
    parts: list[ReversibleIndex_V1_0_0]
    """A list of parts and whether they are reversed."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.parts, list):
            raise ValidationFailed("self.parts is not a list")
        for v in self.parts:
            if not isinstance(v, ReversibleIndex_V1_0_0):
                raise ValidationFailed("v is not ReversibleIndex_V1_0_0")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
