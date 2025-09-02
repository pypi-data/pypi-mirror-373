import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.ellipsoid import Ellipsoid_V1_0_1, Ellipsoid_V1_1_0
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_0_1(BaseSpatialDataProperties_V1_0_1, Ellipsoid_V1_0_1):
    """Global ellipsoid."""

    SCHEMA_ID = "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        Ellipsoid_V1_0_1.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_1_0(BaseSpatialDataProperties_V1_0_1, Ellipsoid_V1_1_0):
    """Global ellipsoid."""

    SCHEMA_ID = "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        Ellipsoid_V1_1_0.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_2_0(BaseSpatialDataProperties_V1_1_0, Ellipsoid_V1_1_0):
    """Global ellipsoid."""

    SCHEMA_ID = "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        Ellipsoid_V1_1_0.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json" failed'
            )
