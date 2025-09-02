import dataclasses

from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIpPldpConfigurationProperties_V1_0_0(Serialiser):
    """Resistivity-IP properties for pole-dipole or offset pole-dipole configurations."""

    SCHEMA_ID = "/components/resistivity-ip-pldp-configuration-properties/1.0.0/resistivity-ip-pldp-configuration-properties.schema.json"

    type: str
    """Type of configuration."""
    transmitter_remote: Coordinates3D_V1_0_0 | None = None
    """Location of transmitter remote."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("PLDP", "OPLDP"):
            raise ValidationFailed('self.type in ("PLDP", "OPLDP") failed')
        if self.transmitter_remote is not None:
            if not isinstance(self.transmitter_remote, Coordinates3D_V1_0_0):
                raise ValidationFailed("self.transmitter_remote is not Coordinates3D_V1_0_0")
