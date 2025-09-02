import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIpSipSurveyProperties_V1_0_0(Serialiser):
    """Resistivity-IP properties for Spectral Induced Polarization (SIP) surveys."""

    SCHEMA_ID = (
        "/components/resistivity-ip-sip-survey-properties/1.0.0/resistivity-ip-sip-survey-properties.schema.json"
    )

    frequencies: list[float]
    """Frequencies (Hz) used during measurements."""
    type: str = "SIP"
    """Type of survey."""

    def __post_init__(self):
        if not isinstance(self.frequencies, list):
            raise ValidationFailed("self.frequencies is not a list")
        for v in self.frequencies:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
            if not 0.0 <= v:
                raise ValidationFailed("0.0 <= v failed")
        if not 1 <= len(self.frequencies):
            raise ValidationFailed("1 <= len(self.frequencies) failed")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "SIP":
            raise ValidationFailed('self.type == "SIP" failed')
