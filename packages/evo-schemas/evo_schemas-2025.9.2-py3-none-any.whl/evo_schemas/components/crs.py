import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Crs_V1_0_1_EpsgCode(Serialiser):
    epsg_code: int
    """EPSG Geodetic Parameter Dataset. EPSG codes are between 1024-32767"""

    def __post_init__(self):
        if not isinstance(self.epsg_code, int):
            raise ValidationFailed("self.epsg_code is not int")
        if not 1024 <= self.epsg_code <= 32767:
            raise ValidationFailed("1024 <= self.epsg_code <= 32767 failed")


@dataclasses.dataclass(kw_only=True)
class Crs_V1_0_1_OgcWkt(Serialiser):
    ogc_wkt: str
    """Well-known text representation of coordinate reference systems."""

    def __post_init__(self):
        if not isinstance(self.ogc_wkt, str):
            raise ValidationFailed("self.ogc_wkt is not str")


Crs_V1_0_1 = Crs_V1_0_1_EpsgCode | Crs_V1_0_1_OgcWkt | str


def is_crs_v1_0_1(value):
    if isinstance(value, Crs_V1_0_1_EpsgCode):
        return True
    if isinstance(value, Crs_V1_0_1_OgcWkt):
        return True
    if isinstance(value, str) and value == "unspecified":
        # Unspecified coordinate reference system.
        return True
    return False
