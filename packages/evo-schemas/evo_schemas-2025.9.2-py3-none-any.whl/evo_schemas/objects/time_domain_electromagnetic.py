import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.survey_line import SurveyLine_V1_1_0
from ..components.time_domain_electromagnetic_channel import TimeDomainElectromagneticChannel_V1_0_0
from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagnetic_V1_1_0_Survey(Serialiser):
    """Survey information."""

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MOVING_GROUND", "DAGCAP"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MOVING_GROUND", "DAGCAP") failed')


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagnetic_V1_1_0(BaseSpatialDataProperties_V1_1_0):
    """Time Domain Electromagnetic data."""

    SCHEMA_ID = "/objects/time-domain-electromagnetic/1.1.0/time-domain-electromagnetic.schema.json"

    survey: TimeDomainElectromagnetic_V1_1_0_Survey
    """Survey information."""
    geometry_category: str
    """Geometry category."""
    gps: Coordinates3D_V1_0_0
    """Location of GPS relative to point of reference."""
    channels: list[TimeDomainElectromagneticChannel_V1_0_0]
    """Channel information."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/time-domain-electromagnetic/1.1.0/time-domain-electromagnetic.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.survey, TimeDomainElectromagnetic_V1_1_0_Survey):
            raise ValidationFailed("self.survey is not TimeDomainElectromagnetic_V1_1_0_Survey")
        if not isinstance(self.geometry_category, str):
            raise ValidationFailed("self.geometry_category is not str")
        if self.geometry_category not in ("STXMRX", "FGTXRX", "MTXMRX", "STXSRX"):
            raise ValidationFailed('self.geometry_category in ("STXMRX", "FGTXRX", "MTXMRX", "STXSRX") failed')
        if not isinstance(self.gps, Coordinates3D_V1_0_0):
            raise ValidationFailed("self.gps is not Coordinates3D_V1_0_0")
        if not isinstance(self.channels, list):
            raise ValidationFailed("self.channels is not a list")
        for v in self.channels:
            if not isinstance(v, TimeDomainElectromagneticChannel_V1_0_0):
                raise ValidationFailed("v is not TimeDomainElectromagneticChannel_V1_0_0")
        if not 1 <= len(self.channels):
            raise ValidationFailed("1 <= len(self.channels) failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/time-domain-electromagnetic/1.1.0/time-domain-electromagnetic.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/time-domain-electromagnetic/1.1.0/time-domain-electromagnetic.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagnetic_V1_0_0_Survey(Serialiser):
    """Survey information."""

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MOVING_GROUND", "DAGCAP"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MOVING_GROUND", "DAGCAP") failed')


@dataclasses.dataclass(kw_only=True)
class TimeDomainElectromagnetic_V1_0_0(BaseSpatialDataProperties_V1_0_1):
    """Time Domain Electromagnetic data."""

    SCHEMA_ID = "/objects/time-domain-electromagnetic/1.0.0/time-domain-electromagnetic.schema.json"

    survey: TimeDomainElectromagnetic_V1_0_0_Survey
    """Survey information."""
    geometry_category: str
    """Geometry category."""
    gps: Coordinates3D_V1_0_0
    """Location of GPS relative to point of reference."""
    channels: list[TimeDomainElectromagneticChannel_V1_0_0]
    """Channel information."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/time-domain-electromagnetic/1.0.0/time-domain-electromagnetic.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, TimeDomainElectromagnetic_V1_0_0_Survey):
            raise ValidationFailed("self.survey is not TimeDomainElectromagnetic_V1_0_0_Survey")
        if not isinstance(self.geometry_category, str):
            raise ValidationFailed("self.geometry_category is not str")
        if self.geometry_category not in ("STXMRX", "FGTXRX", "MTXMRX", "STXSRX"):
            raise ValidationFailed('self.geometry_category in ("STXMRX", "FGTXRX", "MTXMRX", "STXSRX") failed')
        if not isinstance(self.gps, Coordinates3D_V1_0_0):
            raise ValidationFailed("self.gps is not Coordinates3D_V1_0_0")
        if not isinstance(self.channels, list):
            raise ValidationFailed("self.channels is not a list")
        for v in self.channels:
            if not isinstance(v, TimeDomainElectromagneticChannel_V1_0_0):
                raise ValidationFailed("v is not TimeDomainElectromagneticChannel_V1_0_0")
        if not 1 <= len(self.channels):
            raise ValidationFailed("1 <= len(self.channels) failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/time-domain-electromagnetic/1.0.0/time-domain-electromagnetic.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/time-domain-electromagnetic/1.0.0/time-domain-electromagnetic.schema.json" failed'
            )
