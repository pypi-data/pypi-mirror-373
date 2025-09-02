import dataclasses

from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagneticChannel_V1_0_0_Filter(Serialiser):
    order: float
    """Filter order."""
    frequency: float
    """Filter frequency."""

    def __post_init__(self):
        if not isinstance(self.order, float):
            raise ValidationFailed("self.order is not float")
        if not 0.0 <= self.order:
            raise ValidationFailed("0.0 <= self.order failed")
        if not isinstance(self.frequency, float):
            raise ValidationFailed("self.frequency is not float")
        if not 0.0 <= self.frequency:
            raise ValidationFailed("0.0 <= self.frequency failed")


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagneticChannel_V1_0_0(Serialiser):
    """Time domain electromagnetic channel."""

    SCHEMA_ID = "/components/time-domain-electromagnetic-channel/1.0.0/time-domain-electromagnetic-channel.schema.json"

    index: int
    """Channel number."""
    repetition_frequency: float
    """Repetition frequency (Hz)."""
    zero_time: float
    """Current turn off time (msec) relative to start of cycle."""
    start_time: float
    """Time (msec) delay of first gate relative to turn off time."""
    transmitter_id: int
    """Transmitter Id."""
    receiver_id: int
    """Receiver Id."""
    waveform_id: int
    """Waveform Id."""
    gates_id: int
    """Gates Id."""
    number_of_transmitter_turns: float
    """Number of transmitter loop turns."""
    base_transmitter_frequency: float
    """Base frequency (Hz) at the transmitter."""
    peak_transmitter_frequency: float
    """Peak current (Amp)."""
    inclinometers_transmitter_position: list[Coordinates3D_V1_0_0] | None = None
    """Inclinometers transmitter position."""
    inclinometers_receiver_position: list[Coordinates3D_V1_0_0] | None = None
    """Inclinometers receiver position."""
    gates_factor: float = 1.0
    """Gate factor (calibrations factor)."""
    gates_time_shift: float = 0.0
    """Gate time shift (calibration factor)."""
    uniform_standard_deviation: float = 0.0
    """Uniform data standard deviation."""
    primary_field_damping_factor: float | None = None
    """Primary field damping factor."""
    front_gate_filter: TimeDomainElectromagneticChannel_V1_0_0_Filter | None = None
    """Front gate filter."""
    front_gate_time: float | None = None
    """Front gate time (sec)."""
    front_gate_slope_low_pass_filter: TimeDomainElectromagneticChannel_V1_0_0_Filter | None = None
    """Slope low pass filter before front gate."""

    def __post_init__(self):
        if not isinstance(self.index, int):
            raise ValidationFailed("self.index is not int")
        if not 0 <= self.index:
            raise ValidationFailed("0 <= self.index failed")
        if not isinstance(self.repetition_frequency, float):
            raise ValidationFailed("self.repetition_frequency is not float")
        if not 0 <= self.repetition_frequency:
            raise ValidationFailed("0 <= self.repetition_frequency failed")
        if not isinstance(self.zero_time, float):
            raise ValidationFailed("self.zero_time is not float")
        if not 0.0 <= self.zero_time:
            raise ValidationFailed("0.0 <= self.zero_time failed")
        if not isinstance(self.start_time, float):
            raise ValidationFailed("self.start_time is not float")
        if not 0.0 <= self.start_time:
            raise ValidationFailed("0.0 <= self.start_time failed")
        if not isinstance(self.transmitter_id, int):
            raise ValidationFailed("self.transmitter_id is not int")
        if not 0 <= self.transmitter_id:
            raise ValidationFailed("0 <= self.transmitter_id failed")
        if not isinstance(self.receiver_id, int):
            raise ValidationFailed("self.receiver_id is not int")
        if not 0 <= self.receiver_id:
            raise ValidationFailed("0 <= self.receiver_id failed")
        if not isinstance(self.waveform_id, int):
            raise ValidationFailed("self.waveform_id is not int")
        if not 0 <= self.waveform_id:
            raise ValidationFailed("0 <= self.waveform_id failed")
        if not isinstance(self.gates_id, int):
            raise ValidationFailed("self.gates_id is not int")
        if not 0 <= self.gates_id:
            raise ValidationFailed("0 <= self.gates_id failed")
        if not isinstance(self.number_of_transmitter_turns, float):
            raise ValidationFailed("self.number_of_transmitter_turns is not float")
        if not 0.0 <= self.number_of_transmitter_turns:
            raise ValidationFailed("0.0 <= self.number_of_transmitter_turns failed")
        if not isinstance(self.base_transmitter_frequency, float):
            raise ValidationFailed("self.base_transmitter_frequency is not float")
        if not 0.0 <= self.base_transmitter_frequency:
            raise ValidationFailed("0.0 <= self.base_transmitter_frequency failed")
        if not isinstance(self.peak_transmitter_frequency, float):
            raise ValidationFailed("self.peak_transmitter_frequency is not float")
        if not 0.0 <= self.peak_transmitter_frequency:
            raise ValidationFailed("0.0 <= self.peak_transmitter_frequency failed")
        if self.inclinometers_transmitter_position is not None:
            if not isinstance(self.inclinometers_transmitter_position, list):
                raise ValidationFailed("self.inclinometers_transmitter_position is not a list")
            for v in self.inclinometers_transmitter_position:
                if not isinstance(v, Coordinates3D_V1_0_0):
                    raise ValidationFailed("v is not Coordinates3D_V1_0_0")
            if not 1 <= len(self.inclinometers_transmitter_position) <= 2:
                raise ValidationFailed("1 <= len(self.inclinometers_transmitter_position) <= 2 failed")
        if self.inclinometers_receiver_position is not None:
            if not isinstance(self.inclinometers_receiver_position, list):
                raise ValidationFailed("self.inclinometers_receiver_position is not a list")
            for v in self.inclinometers_receiver_position:
                if not isinstance(v, Coordinates3D_V1_0_0):
                    raise ValidationFailed("v is not Coordinates3D_V1_0_0")
            if not 1 <= len(self.inclinometers_receiver_position) <= 2:
                raise ValidationFailed("1 <= len(self.inclinometers_receiver_position) <= 2 failed")
        if not isinstance(self.gates_factor, float):
            raise ValidationFailed("self.gates_factor is not float")
        if not 0.0 <= self.gates_factor:
            raise ValidationFailed("0.0 <= self.gates_factor failed")
        if not isinstance(self.gates_time_shift, float):
            raise ValidationFailed("self.gates_time_shift is not float")
        if not 0.0 <= self.gates_time_shift:
            raise ValidationFailed("0.0 <= self.gates_time_shift failed")
        if not isinstance(self.uniform_standard_deviation, float):
            raise ValidationFailed("self.uniform_standard_deviation is not float")
        if not 0.0 <= self.uniform_standard_deviation:
            raise ValidationFailed("0.0 <= self.uniform_standard_deviation failed")
        if self.primary_field_damping_factor is not None:
            if not isinstance(self.primary_field_damping_factor, float):
                raise ValidationFailed("self.primary_field_damping_factor is not float")
            if not 0.0 <= self.primary_field_damping_factor:
                raise ValidationFailed("0.0 <= self.primary_field_damping_factor failed")
        if self.front_gate_filter is not None:
            if not isinstance(self.front_gate_filter, TimeDomainElectromagneticChannel_V1_0_0_Filter):
                raise ValidationFailed("self.front_gate_filter is not TimeDomainElectromagneticChannel_V1_0_0_Filter")
        if self.front_gate_time is not None:
            if not isinstance(self.front_gate_time, float):
                raise ValidationFailed("self.front_gate_time is not float")
            if not 0.0 <= self.front_gate_time:
                raise ValidationFailed("0.0 <= self.front_gate_time failed")
        if self.front_gate_slope_low_pass_filter is not None:
            if not isinstance(self.front_gate_slope_low_pass_filter, TimeDomainElectromagneticChannel_V1_0_0_Filter):
                raise ValidationFailed(
                    "self.front_gate_slope_low_pass_filter is not TimeDomainElectromagneticChannel_V1_0_0_Filter"
                )
