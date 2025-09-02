import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.survey_line import SurveyLine_V1_0_1, SurveyLine_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_0_1_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    gravity_line_list: list[SurveyLine_V1_0_1]
    """Base station gravity line list."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.location, list):
            raise ValidationFailed("self.location is not a list")
        for v in self.location:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.location) == 3:
            raise ValidationFailed("len(self.location) == 3 failed")
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """Gravity survey data."""

    SCHEMA_ID = "/objects/gravity/1.0.1/gravity.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    gravity_line_list: list[SurveyLine_V1_0_1]
    """Gravity line list."""
    schema: str = "/objects/gravity/1.0.1/gravity.schema.json"
    base_stations: list[Gravity_V1_0_1_BaseStations] | None = None
    """Base stations."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("GRAV", "FTG", "AGG"):
            raise ValidationFailed('self.survey_type in ("GRAV", "FTG", "AGG") failed')
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/gravity/1.0.1/gravity.schema.json":
            raise ValidationFailed('self.schema == "/objects/gravity/1.0.1/gravity.schema.json" failed')
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Gravity_V1_0_1_BaseStations):
                    raise ValidationFailed("v is not Gravity_V1_0_1_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_1_0_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    gravity_line_list: list[SurveyLine_V1_1_0]
    """Base station gravity line list."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.location, list):
            raise ValidationFailed("self.location is not a list")
        for v in self.location:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.location) == 3:
            raise ValidationFailed("len(self.location) == 3 failed")
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """Gravity survey data."""

    SCHEMA_ID = "/objects/gravity/1.1.0/gravity.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    gravity_line_list: list[SurveyLine_V1_1_0]
    """Gravity line list."""
    schema: str = "/objects/gravity/1.1.0/gravity.schema.json"
    base_stations: list[Gravity_V1_1_0_BaseStations] | None = None
    """Base stations."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("GRAV", "FTG", "AGG"):
            raise ValidationFailed('self.survey_type in ("GRAV", "FTG", "AGG") failed')
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/gravity/1.1.0/gravity.schema.json":
            raise ValidationFailed('self.schema == "/objects/gravity/1.1.0/gravity.schema.json" failed')
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Gravity_V1_1_0_BaseStations):
                    raise ValidationFailed("v is not Gravity_V1_1_0_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_2_0_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    gravity_line_list: list[SurveyLine_V1_1_0]
    """Base station gravity line list."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.location, list):
            raise ValidationFailed("self.location is not a list")
        for v in self.location:
            if not isinstance(v, float):
                raise ValidationFailed("v is not float")
        if not len(self.location) == 3:
            raise ValidationFailed("len(self.location) == 3 failed")
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Gravity_V1_2_0(BaseSpatialDataProperties_V1_1_0):
    """Gravity survey data."""

    SCHEMA_ID = "/objects/gravity/1.2.0/gravity.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    gravity_line_list: list[SurveyLine_V1_1_0]
    """Gravity line list."""
    schema: str = "/objects/gravity/1.2.0/gravity.schema.json"
    base_stations: list[Gravity_V1_2_0_BaseStations] | None = None
    """Base stations."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("GRAV", "FTG", "AGG"):
            raise ValidationFailed('self.survey_type in ("GRAV", "FTG", "AGG") failed')
        if not isinstance(self.gravity_line_list, list):
            raise ValidationFailed("self.gravity_line_list is not a list")
        for v in self.gravity_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.gravity_line_list):
            raise ValidationFailed("1 <= len(self.gravity_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/gravity/1.2.0/gravity.schema.json":
            raise ValidationFailed('self.schema == "/objects/gravity/1.2.0/gravity.schema.json" failed')
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Gravity_V1_2_0_BaseStations):
                    raise ValidationFailed("v is not Gravity_V1_2_0_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")
