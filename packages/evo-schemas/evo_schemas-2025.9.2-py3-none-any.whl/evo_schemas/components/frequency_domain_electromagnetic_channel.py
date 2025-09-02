import dataclasses

from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagneticChannel_V1_0_0_CoilConfiguration(Serialiser):
    frequency: float
    """Frequency (Hz) used during measurements."""
    geometry: str
    """The configuration consists of 2 coils and their relative orientation(Horizontal or Vertical), direction relative to each other (Coaxial or Coplanar) and separation between the coils."""
    separation: float
    """Separation (m) between centre of coils."""

    def __post_init__(self):
        if not isinstance(self.frequency, float):
            raise ValidationFailed("self.frequency is not float")
        if not isinstance(self.geometry, str):
            raise ValidationFailed("self.geometry is not str")
        if self.geometry not in ("VCA", "VCP", "HCP", "PRP"):
            raise ValidationFailed('self.geometry in ("VCA", "VCP", "HCP", "PRP") failed')
        if not isinstance(self.separation, float):
            raise ValidationFailed("self.separation is not float")
        if not 0.0 <= self.separation:
            raise ValidationFailed("0.0 <= self.separation failed")


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagneticChannel_V1_0_0(Serialiser):
    """Frequency domain electromagnetic channel."""

    SCHEMA_ID = "/components/frequency-domain-electromagnetic-channel/1.0.0/frequency-domain-electromagnetic-channel.schema.json"

    id: int
    """Channel ID number."""
    relative_quadrature_standard_deviation: int
    """Relative (%) qaudrature standard deviation."""
    relative_in_phase_standard_deviation: int
    """Relative (%) in-phase standard deviation."""
    coil_configuration: list[FrequencyDomainElectromagneticChannel_V1_0_0_CoilConfiguration]
    """Coil configuration. Frequency is provided in increasing order."""
    gps: Coordinates3D_V1_0_0
    """Location of GPS relative to point of reference."""

    def __post_init__(self):
        if not isinstance(self.id, int):
            raise ValidationFailed("self.id is not int")
        if not 0 <= self.id:
            raise ValidationFailed("0 <= self.id failed")
        if not isinstance(self.relative_quadrature_standard_deviation, int):
            raise ValidationFailed("self.relative_quadrature_standard_deviation is not int")
        if not 0.0 <= self.relative_quadrature_standard_deviation:
            raise ValidationFailed("0.0 <= self.relative_quadrature_standard_deviation failed")
        if not isinstance(self.relative_in_phase_standard_deviation, int):
            raise ValidationFailed("self.relative_in_phase_standard_deviation is not int")
        if not 0.0 <= self.relative_in_phase_standard_deviation:
            raise ValidationFailed("0.0 <= self.relative_in_phase_standard_deviation failed")
        if not isinstance(self.coil_configuration, list):
            raise ValidationFailed("self.coil_configuration is not a list")
        for v in self.coil_configuration:
            if not isinstance(v, FrequencyDomainElectromagneticChannel_V1_0_0_CoilConfiguration):
                raise ValidationFailed("v is not FrequencyDomainElectromagneticChannel_V1_0_0_CoilConfiguration")
        if not 1 <= len(self.coil_configuration):
            raise ValidationFailed("1 <= len(self.coil_configuration) failed")
        if not isinstance(self.gps, Coordinates3D_V1_0_0):
            raise ValidationFailed("self.gps is not Coordinates3D_V1_0_0")
