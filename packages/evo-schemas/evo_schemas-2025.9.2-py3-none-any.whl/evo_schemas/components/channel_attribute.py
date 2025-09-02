import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .bool_attribute import BoolAttribute_V1_0_1, BoolAttribute_V1_1_0
from .category_attribute import CategoryAttribute_V1_0_1, CategoryAttribute_V1_1_0
from .category_ensemble import CategoryEnsemble_V1_0_1, CategoryEnsemble_V1_1_0
from .continuous_attribute import ContinuousAttribute_V1_0_1, ContinuousAttribute_V1_1_0
from .continuous_ensemble import ContinuousEnsemble_V1_0_1, ContinuousEnsemble_V1_1_0
from .date_time_attribute import DateTimeAttribute_V1_0_1, DateTimeAttribute_V1_1_0
from .string_attribute import StringAttribute_V1_0_1, StringAttribute_V1_1_0

ChannelAttribute_V1_0_1_Attribute = (
    ContinuousAttribute_V1_0_1
    | ContinuousEnsemble_V1_0_1
    | CategoryAttribute_V1_0_1
    | CategoryEnsemble_V1_0_1
    | DateTimeAttribute_V1_0_1
    | BoolAttribute_V1_0_1
    | StringAttribute_V1_0_1
)


@dataclasses.dataclass(kw_only=True)
class ChannelAttribute_V1_0_1(Serialiser):
    """An attribute for a channel."""

    SCHEMA_ID = "/components/channel-attribute/1.0.1/channel-attribute.schema.json"

    name: str
    """The name of the channel."""
    attribute: ChannelAttribute_V1_0_1_Attribute
    """Attribute associated with the channel."""
    start_fiducial: float | None = None
    """Starting fiducial number."""
    fiducial_increment: float | None = None
    """Fiducial increment amount."""
    significant_digits: int | None = None
    """Significant digits."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.attribute, ChannelAttribute_V1_0_1_Attribute):
            raise ValidationFailed("self.attribute is not ChannelAttribute_V1_0_1_Attribute")
        if self.start_fiducial is not None:
            if not isinstance(self.start_fiducial, float):
                raise ValidationFailed("self.start_fiducial is not float")
        if self.fiducial_increment is not None:
            if not isinstance(self.fiducial_increment, float):
                raise ValidationFailed("self.fiducial_increment is not float")
            if not 0.0 < self.fiducial_increment:
                raise ValidationFailed("0.0 < self.fiducial_increment failed")
        if self.significant_digits is not None:
            if not isinstance(self.significant_digits, int):
                raise ValidationFailed("self.significant_digits is not int")
            if not 0 <= self.significant_digits:
                raise ValidationFailed("0 <= self.significant_digits failed")


ChannelAttribute_V1_1_0_Attribute = (
    BoolAttribute_V1_1_0
    | ContinuousAttribute_V1_1_0
    | ContinuousEnsemble_V1_1_0
    | CategoryAttribute_V1_1_0
    | CategoryEnsemble_V1_1_0
    | DateTimeAttribute_V1_1_0
    | StringAttribute_V1_1_0
)


@dataclasses.dataclass(kw_only=True)
class ChannelAttribute_V1_1_0(Serialiser):
    """An attribute for a channel."""

    SCHEMA_ID = "/components/channel-attribute/1.1.0/channel-attribute.schema.json"

    name: str
    """The name of the channel."""
    attribute: ChannelAttribute_V1_1_0_Attribute
    """Attribute associated with the channel."""
    start_fiducial: float | None = None
    """Starting fiducial number."""
    fiducial_increment: float | None = None
    """Fiducial increment amount."""
    significant_digits: int | None = None
    """Significant digits."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.attribute, ChannelAttribute_V1_1_0_Attribute):
            raise ValidationFailed("self.attribute is not ChannelAttribute_V1_1_0_Attribute")
        if self.start_fiducial is not None:
            if not isinstance(self.start_fiducial, float):
                raise ValidationFailed("self.start_fiducial is not float")
        if self.fiducial_increment is not None:
            if not isinstance(self.fiducial_increment, float):
                raise ValidationFailed("self.fiducial_increment is not float")
            if not 0.0 < self.fiducial_increment:
                raise ValidationFailed("0.0 < self.fiducial_increment failed")
        if self.significant_digits is not None:
            if not isinstance(self.significant_digits, int):
                raise ValidationFailed("self.significant_digits is not int")
            if not 0 <= self.significant_digits:
                raise ValidationFailed("0 <= self.significant_digits failed")
