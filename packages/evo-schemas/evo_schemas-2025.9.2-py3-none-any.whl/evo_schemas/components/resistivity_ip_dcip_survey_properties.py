import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIpDcipSurveyProperties_V1_0_0(Serialiser):
    """Resistivity-IP properties for Direct Current Induced Polarization (DCIP) surveys."""

    SCHEMA_ID = (
        "/components/resistivity-ip-dcip-survey-properties/1.0.0/resistivity-ip-dcip-survey-properties.schema.json"
    )

    delay_time: float
    """Delay time (sec). Integration start time since current shut off."""
    number_of_time_gates: int
    """Number of time gates."""
    gate_times: float
    """Width of each IP time (sec) gate."""
    type: str = "DCIP"
    """Type of survey."""
    duty_cycle: float | None = None
    """Time (sec) cycle."""
    wave_type: int | None = None
    """Wave type. 50% or 100% duty cycle."""
    pulses: int = 4
    """Number of pulses."""

    def __post_init__(self):
        if not isinstance(self.delay_time, float):
            raise ValidationFailed("self.delay_time is not float")
        if not 0.0 <= self.delay_time:
            raise ValidationFailed("0.0 <= self.delay_time failed")
        if not isinstance(self.number_of_time_gates, int):
            raise ValidationFailed("self.number_of_time_gates is not int")
        if not 0 <= self.number_of_time_gates:
            raise ValidationFailed("0 <= self.number_of_time_gates failed")
        if not isinstance(self.gate_times, float):
            raise ValidationFailed("self.gate_times is not float")
        if not 0.0 <= self.gate_times:
            raise ValidationFailed("0.0 <= self.gate_times failed")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "DCIP":
            raise ValidationFailed('self.type == "DCIP" failed')
        if self.duty_cycle is not None:
            if not isinstance(self.duty_cycle, float):
                raise ValidationFailed("self.duty_cycle is not float")
            if not 0.0 <= self.duty_cycle:
                raise ValidationFailed("0.0 <= self.duty_cycle failed")
        if self.wave_type is not None:
            if not isinstance(self.wave_type, int):
                raise ValidationFailed("self.wave_type is not int")
            if self.wave_type not in (50, 100):
                raise ValidationFailed("self.wave_type in (50, 100) failed")
        if not isinstance(self.pulses, int):
            raise ValidationFailed("self.pulses is not int")
        if not 0 <= self.pulses:
            raise ValidationFailed("0 <= self.pulses failed")
