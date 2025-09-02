import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .channel_attribute import ChannelAttribute_V1_1_0


@dataclasses.dataclass(kw_only=True)
class ResistivityIpLine_V1_1_0(Serialiser):
    """Resistivity IP Line."""

    SCHEMA_ID = "/components/resistivity-ip-line/1.1.0/resistivity-ip-line.schema.json"

    group_number: str
    """Group number."""
    date: str
    """Date."""
    station: str
    """Station identifier."""
    number_of_electrodes: int
    """Number of electrodes."""
    channel_attributes: list[ChannelAttribute_V1_1_0]
    """List of channel attributes."""

    def __post_init__(self):
        if not isinstance(self.group_number, str):
            raise ValidationFailed("self.group_number is not str")
        if not isinstance(self.date, str):
            raise ValidationFailed("self.date is not str")
        if not Serialiser.is_date_time(self.date):
            raise ValidationFailed("Serialiser.is_date_time(self.date) failed")
        if not isinstance(self.station, str):
            raise ValidationFailed("self.station is not str")
        if not isinstance(self.number_of_electrodes, int):
            raise ValidationFailed("self.number_of_electrodes is not int")
        if not 1 <= self.number_of_electrodes <= 6:
            raise ValidationFailed("1 <= self.number_of_electrodes <= 6 failed")
        if not isinstance(self.channel_attributes, list):
            raise ValidationFailed("self.channel_attributes is not a list")
        for v in self.channel_attributes:
            if not isinstance(v, ChannelAttribute_V1_1_0):
                raise ValidationFailed("v is not ChannelAttribute_V1_1_0")
