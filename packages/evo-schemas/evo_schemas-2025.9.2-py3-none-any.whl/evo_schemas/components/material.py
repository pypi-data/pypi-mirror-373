import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Material_V1_0_1(Serialiser):
    """This component describes a material."""

    SCHEMA_ID = "/components/material/1.0.1/material.schema.json"

    key: str
    """Unique identifier of the material."""
    name: str
    """Name."""
    color: int
    """Color."""
    data_source: str | None = None
    """Optional data source that contains a link to an existing Geoscience object."""

    def __post_init__(self):
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.color, int):
            raise ValidationFailed("self.color is not int")
        if self.data_source is not None:
            if not isinstance(self.data_source, str):
                raise ValidationFailed("self.data_source is not str")
