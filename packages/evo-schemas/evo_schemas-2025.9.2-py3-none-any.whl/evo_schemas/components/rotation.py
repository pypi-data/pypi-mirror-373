import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Rotation_V1_1_0(Serialiser):
    """Rotation in 3D space described by 3 angles, all rotating clockwise about the Z, then X, and finally Z axes. All angles must be positive values, specified in degrees, within the bounds defined for each rotation. 0 degrees in the xy plane (dip azimuth) is 90 degrees East of North."""

    SCHEMA_ID = "/components/rotation/1.1.0/rotation.schema.json"

    dip_azimuth: float = 0.0
    """first rotation, about the z-axis"""
    dip: float = 0.0
    """second rotation, about the x-axis"""
    pitch: float = 0.0
    """third rotation, about the z-axis"""

    def __post_init__(self):
        if not isinstance(self.dip_azimuth, float):
            raise ValidationFailed("self.dip_azimuth is not float")
        if not 0.0 <= self.dip_azimuth <= 360.0:
            raise ValidationFailed("0.0 <= self.dip_azimuth <= 360.0 failed")
        if not isinstance(self.dip, float):
            raise ValidationFailed("self.dip is not float")
        if not 0.0 <= self.dip <= 180.0:
            raise ValidationFailed("0.0 <= self.dip <= 180.0 failed")
        if not isinstance(self.pitch, float):
            raise ValidationFailed("self.pitch is not float")
        if not 0.0 <= self.pitch <= 360.0:
            raise ValidationFailed("0.0 <= self.pitch <= 360.0 failed")


@dataclasses.dataclass(kw_only=True)
class Rotation_V1_0_1(Serialiser):
    """Rotation in 3D space described by 3 angles, all rotating clockwise about the Z, then X, and finally Z axes. All angles must be positive values, specified in degrees, within the bounds defined for each rotation. 0 degrees in the xy plane (dip azimuth) is 90 degrees East of North."""

    SCHEMA_ID = "/components/rotation/1.0.1/rotation.schema.json"

    dip_azimuth: float = 0.0
    """first rotation, about the z-axis"""
    dip: float = 0.0
    """second rotation, about the x-axis"""
    pitch: float = 0.0
    """third rotation, about the z-axis"""

    def __post_init__(self):
        if not isinstance(self.dip_azimuth, float):
            raise ValidationFailed("self.dip_azimuth is not float")
        if not 0.0 <= self.dip_azimuth <= 360.0:
            raise ValidationFailed("0.0 <= self.dip_azimuth <= 360.0 failed")
        if not isinstance(self.dip, float):
            raise ValidationFailed("self.dip is not float")
        if not 0.0 <= self.dip <= 90.0:
            raise ValidationFailed("0.0 <= self.dip <= 90.0 failed")
        if not isinstance(self.pitch, float):
            raise ValidationFailed("self.pitch is not float")
        if not 0.0 <= self.pitch <= 180.0:
            raise ValidationFailed("0.0 <= self.pitch <= 180.0 failed")
