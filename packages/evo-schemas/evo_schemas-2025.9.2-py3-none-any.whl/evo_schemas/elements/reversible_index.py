import dataclasses

from .serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ReversibleIndex_V1_0_0(Serialiser):
    """A structure holding an index of a model part, and optionally, a flag speficying whether the part should be reversed."""

    SCHEMA_ID = "/elements/reversible-index/1.0.0/reversible-index.schema.json"

    index: int
    """The index of the part in the geometry parts list."""
    reversed: bool = False
    """Whether the part should be reversed."""

    def __post_init__(self):
        if not isinstance(self.index, int):
            raise ValidationFailed("self.index is not int")
        if not 0 <= self.index:
            raise ValidationFailed("0 <= self.index failed")
        if not isinstance(self.reversed, bool):
            raise ValidationFailed("self.reversed is not bool")
