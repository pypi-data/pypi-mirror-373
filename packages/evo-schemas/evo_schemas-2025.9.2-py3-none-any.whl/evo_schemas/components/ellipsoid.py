import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from .rotation import Rotation_V1_0_1, Rotation_V1_1_0


@dataclasses.dataclass(kw_only=True)
class Ellipsoid_V1_0_1_EllipsoidRanges(Serialiser):
    """An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation."""

    major: float
    """The major axis length of the ellipsoid"""
    semi_major: float
    """The semi-major axis length of the ellipsoid"""
    minor: float
    """The minor axis length of the ellipsoid"""

    def __post_init__(self):
        if not isinstance(self.major, float):
            raise ValidationFailed("self.major is not float")
        if not 0 < self.major:
            raise ValidationFailed("0 < self.major failed")
        if not isinstance(self.semi_major, float):
            raise ValidationFailed("self.semi_major is not float")
        if not 0 < self.semi_major:
            raise ValidationFailed("0 < self.semi_major failed")
        if not isinstance(self.minor, float):
            raise ValidationFailed("self.minor is not float")
        if not 0 < self.minor:
            raise ValidationFailed("0 < self.minor failed")


@dataclasses.dataclass(kw_only=True)
class Ellipsoid_V1_0_1(Serialiser):
    """Ellipsoid specification"""

    SCHEMA_ID = "/components/ellipsoid/1.0.1/ellipsoid.schema.json"

    ellipsoid_ranges: Ellipsoid_V1_0_1_EllipsoidRanges
    """An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation."""
    rotation: Rotation_V1_0_1
    """Rotation of the ellipsoid"""

    def __post_init__(self):
        if not isinstance(self.ellipsoid_ranges, Ellipsoid_V1_0_1_EllipsoidRanges):
            raise ValidationFailed("self.ellipsoid_ranges is not Ellipsoid_V1_0_1_EllipsoidRanges")
        if not isinstance(self.rotation, Rotation_V1_0_1):
            raise ValidationFailed("self.rotation is not Rotation_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class Ellipsoid_V1_1_0_EllipsoidRanges(Serialiser):
    """An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation."""

    major: float
    """The major axis length of the ellipsoid"""
    semi_major: float
    """The semi-major axis length of the ellipsoid"""
    minor: float
    """The minor axis length of the ellipsoid"""

    def __post_init__(self):
        if not isinstance(self.major, float):
            raise ValidationFailed("self.major is not float")
        if not 0 < self.major:
            raise ValidationFailed("0 < self.major failed")
        if not isinstance(self.semi_major, float):
            raise ValidationFailed("self.semi_major is not float")
        if not 0 < self.semi_major:
            raise ValidationFailed("0 < self.semi_major failed")
        if not isinstance(self.minor, float):
            raise ValidationFailed("self.minor is not float")
        if not 0 < self.minor:
            raise ValidationFailed("0 < self.minor failed")


@dataclasses.dataclass(kw_only=True)
class Ellipsoid_V1_1_0(Serialiser):
    """Ellipsoid specification"""

    SCHEMA_ID = "/components/ellipsoid/1.1.0/ellipsoid.schema.json"

    ellipsoid_ranges: Ellipsoid_V1_1_0_EllipsoidRanges
    """An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation."""
    rotation: Rotation_V1_1_0
    """Rotation of the ellipsoid"""

    def __post_init__(self):
        if not isinstance(self.ellipsoid_ranges, Ellipsoid_V1_1_0_EllipsoidRanges):
            raise ValidationFailed("self.ellipsoid_ranges is not Ellipsoid_V1_1_0_EllipsoidRanges")
        if not isinstance(self.rotation, Rotation_V1_1_0):
            raise ValidationFailed("self.rotation is not Rotation_V1_1_0")
