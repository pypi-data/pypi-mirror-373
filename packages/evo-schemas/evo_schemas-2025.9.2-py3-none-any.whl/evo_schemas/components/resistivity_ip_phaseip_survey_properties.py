import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIpPhaseipSurveyProperties_V1_0_0(Serialiser):
    """Resistivity-IP properties for Phased Induced Polarization (PHASEIP) surveys."""

    SCHEMA_ID = "/components/resistivity-ip-phaseip-survey-properties/1.0.0/resistivity-ip-phaseip-survey-properties.schema.json"

    frequency: float
    """Frequency (Hz) used during measurements."""
    type: str = "PHASEIP"
    """Type of survey."""

    def __post_init__(self):
        if not isinstance(self.frequency, float):
            raise ValidationFailed("self.frequency is not float")
        if not 0.0 <= self.frequency:
            raise ValidationFailed("0.0 <= self.frequency failed")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "PHASEIP":
            raise ValidationFailed('self.type == "PHASEIP" failed')
