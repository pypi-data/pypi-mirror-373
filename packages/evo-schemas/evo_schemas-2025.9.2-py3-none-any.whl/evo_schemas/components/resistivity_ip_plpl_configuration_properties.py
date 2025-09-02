import dataclasses

from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIpPlplConfigurationProperties_V1_0_0(Serialiser):
    """Resistivity-IP properties for pole-pole configurations."""

    SCHEMA_ID = "/components/resistivity-ip-plpl-configuration-properties/1.0.0/resistivity-ip-plpl-configuration-properties.schema.json"

    type: str = "PLPL"
    """Type of configuration."""
    receiver_remote: Coordinates3D_V1_0_0 | None = None
    """Location of receiver remote."""
    transmitter_remote: Coordinates3D_V1_0_0 | None = None
    """Location of transmitter remote."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "PLPL":
            raise ValidationFailed('self.type == "PLPL" failed')
        if self.receiver_remote is not None:
            if not isinstance(self.receiver_remote, Coordinates3D_V1_0_0):
                raise ValidationFailed("self.receiver_remote is not Coordinates3D_V1_0_0")
        if self.transmitter_remote is not None:
            if not isinstance(self.transmitter_remote, Coordinates3D_V1_0_0):
                raise ValidationFailed("self.transmitter_remote is not Coordinates3D_V1_0_0")
