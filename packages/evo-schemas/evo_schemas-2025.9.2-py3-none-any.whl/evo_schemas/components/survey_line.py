import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .channel_attribute import ChannelAttribute_V1_0_1, ChannelAttribute_V1_1_0


@dataclasses.dataclass(kw_only=True)
class SurveyLine_V1_0_1_LocationChannels(Serialiser):
    """Survey location coordinate channels."""

    x: str
    """Channel name indicating which of the channel attributes corresponds to the X channel."""
    y: str
    """Channel name indicating which of the channel attributes corresponds to the Y channel."""
    z: str | None = None
    """Channel name indicating which of the channel attributes corresponds to the Z channel."""

    def __post_init__(self):
        if not isinstance(self.x, str):
            raise ValidationFailed("self.x is not str")
        if not isinstance(self.y, str):
            raise ValidationFailed("self.y is not str")
        if self.z is not None:
            if not isinstance(self.z, str):
                raise ValidationFailed("self.z is not str")


@dataclasses.dataclass(kw_only=True)
class SurveyLine_V1_0_1(Serialiser):
    """A survey line."""

    SCHEMA_ID = "/components/survey-line/1.0.1/survey-line.schema.json"

    line_number: str
    """The number of the line, can be alphanumeric."""
    date: str
    """Date."""
    version: int = 0
    """Version."""
    group: int = 0
    """Represents the group when the data is collected."""
    type: str = "Line"
    """Survey line type."""
    location_channels: SurveyLine_V1_0_1_LocationChannels
    """Survey location coordinate channels."""
    channel_attributes: list[ChannelAttribute_V1_0_1]
    """List of channel attributes."""

    def __post_init__(self):
        if not isinstance(self.line_number, str):
            raise ValidationFailed("self.line_number is not str")
        if not isinstance(self.date, str):
            raise ValidationFailed("self.date is not str")
        if not Serialiser.is_date_time(self.date):
            raise ValidationFailed("Serialiser.is_date_time(self.date) failed")
        if not isinstance(self.version, int):
            raise ValidationFailed("self.version is not int")
        if not 0 <= self.version:
            raise ValidationFailed("0 <= self.version failed")
        if not isinstance(self.group, int):
            raise ValidationFailed("self.group is not int")
        if not 0 <= self.group:
            raise ValidationFailed("0 <= self.group failed")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test"):
            raise ValidationFailed('self.type in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test") failed')
        if not isinstance(self.location_channels, SurveyLine_V1_0_1_LocationChannels):
            raise ValidationFailed("self.location_channels is not SurveyLine_V1_0_1_LocationChannels")
        if not isinstance(self.channel_attributes, list):
            raise ValidationFailed("self.channel_attributes is not a list")
        for v in self.channel_attributes:
            if not isinstance(v, ChannelAttribute_V1_0_1):
                raise ValidationFailed("v is not ChannelAttribute_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class SurveyLine_V1_1_0_LocationChannels(Serialiser):
    """Survey location coordinate channels."""

    x: str
    """Channel name indicating which of the channel attributes corresponds to the X channel."""
    y: str
    """Channel name indicating which of the channel attributes corresponds to the Y channel."""
    z: str | None = None
    """Channel name indicating which of the channel attributes corresponds to the Z channel."""

    def __post_init__(self):
        if not isinstance(self.x, str):
            raise ValidationFailed("self.x is not str")
        if not isinstance(self.y, str):
            raise ValidationFailed("self.y is not str")
        if self.z is not None:
            if not isinstance(self.z, str):
                raise ValidationFailed("self.z is not str")


@dataclasses.dataclass(kw_only=True)
class SurveyLine_V1_1_0(Serialiser):
    """A survey line."""

    SCHEMA_ID = "/components/survey-line/1.1.0/survey-line.schema.json"

    line_number: str
    """The number of the line, can be alphanumeric."""
    date: str
    """Date."""
    version: int = 0
    """Version."""
    group: int = 0
    """Represents the group when the data is collected."""
    type: str = "Line"
    """Survey line type."""
    location_channels: SurveyLine_V1_1_0_LocationChannels
    """Survey location coordinate channels."""
    channel_attributes: list[ChannelAttribute_V1_1_0]
    """List of channel attributes."""

    def __post_init__(self):
        if not isinstance(self.line_number, str):
            raise ValidationFailed("self.line_number is not str")
        if not isinstance(self.date, str):
            raise ValidationFailed("self.date is not str")
        if not Serialiser.is_date_time(self.date):
            raise ValidationFailed("Serialiser.is_date_time(self.date) failed")
        if not isinstance(self.version, int):
            raise ValidationFailed("self.version is not int")
        if not 0 <= self.version:
            raise ValidationFailed("0 <= self.version failed")
        if not isinstance(self.group, int):
            raise ValidationFailed("self.group is not int")
        if not 0 <= self.group:
            raise ValidationFailed("0 <= self.group failed")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test"):
            raise ValidationFailed('self.type in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test") failed')
        if not isinstance(self.location_channels, SurveyLine_V1_1_0_LocationChannels):
            raise ValidationFailed("self.location_channels is not SurveyLine_V1_1_0_LocationChannels")
        if not isinstance(self.channel_attributes, list):
            raise ValidationFailed("self.channel_attributes is not a list")
        for v in self.channel_attributes:
            if not isinstance(v, ChannelAttribute_V1_1_0):
                raise ValidationFailed("v is not ChannelAttribute_V1_1_0")
