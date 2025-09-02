import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.survey_line import SurveyLine_V1_0_1, SurveyLine_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_0_1_Survey(Serialiser):
    """Survey information."""

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR"):
            raise ValidationFailed('self.type in ("GROUND", "AIR") failed')


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """Radiometric survey data."""

    SCHEMA_ID = "/objects/radiometric/1.0.1/radiometric.schema.json"

    survey: Radiometric_V1_0_1_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_0_1]
    """Line list."""
    schema: str = "/objects/radiometric/1.0.1/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_0_1_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_0_1_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.0.1/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.0.1/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_1_0_Survey(Serialiser):
    """Survey information."""

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR"):
            raise ValidationFailed('self.type in ("GROUND", "AIR") failed')


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """Radiometric survey data."""

    SCHEMA_ID = "/objects/radiometric/1.1.0/radiometric.schema.json"

    survey: Radiometric_V1_1_0_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/radiometric/1.1.0/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_1_0_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_1_0_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.1.0/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.1.0/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_2_0_Survey(Serialiser):
    """Survey information."""

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR"):
            raise ValidationFailed('self.type in ("GROUND", "AIR") failed')


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_2_0(BaseSpatialDataProperties_V1_1_0):
    """Radiometric survey data."""

    SCHEMA_ID = "/objects/radiometric/1.2.0/radiometric.schema.json"

    survey: Radiometric_V1_2_0_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/radiometric/1.2.0/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_2_0_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_2_0_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.2.0/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.2.0/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")
