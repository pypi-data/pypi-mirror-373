import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.survey_line import SurveyLine_V1_0_1, SurveyLine_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_0_1_GradientMagnetic(Serialiser):
    """Gradient magnetic details."""

    number_of_sensors: int = 1
    """Number of sensors."""
    sensor_offsets: list[list[float]]
    """Sensor offsets."""

    def __post_init__(self):
        if not isinstance(self.number_of_sensors, int):
            raise ValidationFailed("self.number_of_sensors is not int")
        if not 1 <= self.number_of_sensors:
            raise ValidationFailed("1 <= self.number_of_sensors failed")
        if not isinstance(self.sensor_offsets, list):
            raise ValidationFailed("self.sensor_offsets is not a list")
        for v in self.sensor_offsets:
            if not isinstance(v, list):
                raise ValidationFailed("v is not a list")
            for w in v:
                if not isinstance(w, float):
                    raise ValidationFailed("w is not float")
            if not len(v) == 3:
                raise ValidationFailed("len(v) == 3 failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_0_1_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_0_1]
    """Base station magnetic line list."""

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
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """Magnetics survey data."""

    SCHEMA_ID = "/objects/magnetics/1.0.1/magnetics.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_0_1]
    """Magnetic line list."""
    schema: str = "/objects/magnetics/1.0.1/magnetics.schema.json"
    gradient_magnetic: Magnetics_V1_0_1_GradientMagnetic | None = None
    """Gradient magnetic details."""
    base_stations: list[Magnetics_V1_0_1_BaseStations] | None = None
    """Base stations."""
    qaqc_magnetic_azimuth_test_list: list[SurveyLine_V1_0_1] | None = None
    """QA/QC Magnetic azimuth test list."""
    qaqc_noise_test_list: list[SurveyLine_V1_0_1] | None = None
    """QA/QC Magnetic noise test list."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG", "MGRM"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG", "MGRM") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/magnetics/1.0.1/magnetics.schema.json":
            raise ValidationFailed('self.schema == "/objects/magnetics/1.0.1/magnetics.schema.json" failed')
        if self.gradient_magnetic is not None:
            if not isinstance(self.gradient_magnetic, Magnetics_V1_0_1_GradientMagnetic):
                raise ValidationFailed("self.gradient_magnetic is not Magnetics_V1_0_1_GradientMagnetic")
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Magnetics_V1_0_1_BaseStations):
                    raise ValidationFailed("v is not Magnetics_V1_0_1_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")
        if self.qaqc_magnetic_azimuth_test_list is not None:
            if not isinstance(self.qaqc_magnetic_azimuth_test_list, list):
                raise ValidationFailed("self.qaqc_magnetic_azimuth_test_list is not a list")
            for v in self.qaqc_magnetic_azimuth_test_list:
                if not isinstance(v, SurveyLine_V1_0_1):
                    raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if self.qaqc_noise_test_list is not None:
            if not isinstance(self.qaqc_noise_test_list, list):
                raise ValidationFailed("self.qaqc_noise_test_list is not a list")
            for v in self.qaqc_noise_test_list:
                if not isinstance(v, SurveyLine_V1_0_1):
                    raise ValidationFailed("v is not SurveyLine_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_1_0_GradientMagnetic(Serialiser):
    """Gradient magnetic details."""

    number_of_sensors: int = 1
    """Number of sensors."""
    sensor_offsets: list[list[float]]
    """Sensor offsets."""

    def __post_init__(self):
        if not isinstance(self.number_of_sensors, int):
            raise ValidationFailed("self.number_of_sensors is not int")
        if not 1 <= self.number_of_sensors:
            raise ValidationFailed("1 <= self.number_of_sensors failed")
        if not isinstance(self.sensor_offsets, list):
            raise ValidationFailed("self.sensor_offsets is not a list")
        for v in self.sensor_offsets:
            if not isinstance(v, list):
                raise ValidationFailed("v is not a list")
            for w in v:
                if not isinstance(w, float):
                    raise ValidationFailed("w is not float")
            if not len(v) == 3:
                raise ValidationFailed("len(v) == 3 failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_1_0_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_1_0]
    """Base station magnetic line list."""

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
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """Magnetics survey data."""

    SCHEMA_ID = "/objects/magnetics/1.1.0/magnetics.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_1_0]
    """Magnetic line list."""
    schema: str = "/objects/magnetics/1.1.0/magnetics.schema.json"
    gradient_magnetic: Magnetics_V1_1_0_GradientMagnetic | None = None
    """Gradient magnetic details."""
    base_stations: list[Magnetics_V1_1_0_BaseStations] | None = None
    """Base stations."""
    qaqc_magnetic_azimuth_test_list: list[SurveyLine_V1_1_0] | None = None
    """QA/QC Magnetic azimuth test list."""
    qaqc_noise_test_list: list[SurveyLine_V1_1_0] | None = None
    """QA/QC Magnetic noise test list."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG", "MGRM"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG", "MGRM") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/magnetics/1.1.0/magnetics.schema.json":
            raise ValidationFailed('self.schema == "/objects/magnetics/1.1.0/magnetics.schema.json" failed')
        if self.gradient_magnetic is not None:
            if not isinstance(self.gradient_magnetic, Magnetics_V1_1_0_GradientMagnetic):
                raise ValidationFailed("self.gradient_magnetic is not Magnetics_V1_1_0_GradientMagnetic")
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Magnetics_V1_1_0_BaseStations):
                    raise ValidationFailed("v is not Magnetics_V1_1_0_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")
        if self.qaqc_magnetic_azimuth_test_list is not None:
            if not isinstance(self.qaqc_magnetic_azimuth_test_list, list):
                raise ValidationFailed("self.qaqc_magnetic_azimuth_test_list is not a list")
            for v in self.qaqc_magnetic_azimuth_test_list:
                if not isinstance(v, SurveyLine_V1_1_0):
                    raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if self.qaqc_noise_test_list is not None:
            if not isinstance(self.qaqc_noise_test_list, list):
                raise ValidationFailed("self.qaqc_noise_test_list is not a list")
            for v in self.qaqc_noise_test_list:
                if not isinstance(v, SurveyLine_V1_1_0):
                    raise ValidationFailed("v is not SurveyLine_V1_1_0")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_2_0_GradientMagnetic(Serialiser):
    """Gradient magnetic details."""

    number_of_sensors: int = 1
    """Number of sensors."""
    sensor_offsets: list[list[float]]
    """Sensor offsets."""

    def __post_init__(self):
        if not isinstance(self.number_of_sensors, int):
            raise ValidationFailed("self.number_of_sensors is not int")
        if not 1 <= self.number_of_sensors:
            raise ValidationFailed("1 <= self.number_of_sensors failed")
        if not isinstance(self.sensor_offsets, list):
            raise ValidationFailed("self.sensor_offsets is not a list")
        for v in self.sensor_offsets:
            if not isinstance(v, list):
                raise ValidationFailed("v is not a list")
            for w in v:
                if not isinstance(w, float):
                    raise ValidationFailed("w is not float")
            if not len(v) == 3:
                raise ValidationFailed("len(v) == 3 failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_2_0_BaseStations(Serialiser):
    """Base station."""

    name: str
    """Base station name."""
    location: list[float]
    """Base station location, (x, y, z)-triple."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_1_0]
    """Base station magnetic line list."""

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
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")


@dataclasses.dataclass(kw_only=True)
class Magnetics_V1_2_0(BaseSpatialDataProperties_V1_1_0):
    """Magnetics survey data."""

    SCHEMA_ID = "/objects/magnetics/1.2.0/magnetics.schema.json"

    type: str
    """Survey mode."""
    survey_type: str
    """Type of survey."""
    magnetic_line_list: list[SurveyLine_V1_1_0]
    """Magnetic line list."""
    schema: str = "/objects/magnetics/1.2.0/magnetics.schema.json"
    gradient_magnetic: Magnetics_V1_2_0_GradientMagnetic | None = None
    """Gradient magnetic details."""
    base_stations: list[Magnetics_V1_2_0_BaseStations] | None = None
    """Base stations."""
    qaqc_magnetic_azimuth_test_list: list[SurveyLine_V1_1_0] | None = None
    """QA/QC Magnetic azimuth test list."""
    qaqc_noise_test_list: list[SurveyLine_V1_1_0] | None = None
    """QA/QC Magnetic noise test list."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR", "MARINE"):
            raise ValidationFailed('self.type in ("GROUND", "AIR", "MARINE") failed')
        if not isinstance(self.survey_type, str):
            raise ValidationFailed("self.survey_type is not str")
        if self.survey_type not in ("TMI", "VMG", "MGRM"):
            raise ValidationFailed('self.survey_type in ("TMI", "VMG", "MGRM") failed')
        if not isinstance(self.magnetic_line_list, list):
            raise ValidationFailed("self.magnetic_line_list is not a list")
        for v in self.magnetic_line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.magnetic_line_list):
            raise ValidationFailed("1 <= len(self.magnetic_line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/magnetics/1.2.0/magnetics.schema.json":
            raise ValidationFailed('self.schema == "/objects/magnetics/1.2.0/magnetics.schema.json" failed')
        if self.gradient_magnetic is not None:
            if not isinstance(self.gradient_magnetic, Magnetics_V1_2_0_GradientMagnetic):
                raise ValidationFailed("self.gradient_magnetic is not Magnetics_V1_2_0_GradientMagnetic")
        if self.base_stations is not None:
            if not isinstance(self.base_stations, list):
                raise ValidationFailed("self.base_stations is not a list")
            for v in self.base_stations:
                if not isinstance(v, Magnetics_V1_2_0_BaseStations):
                    raise ValidationFailed("v is not Magnetics_V1_2_0_BaseStations")
            if not 1 <= len(self.base_stations):
                raise ValidationFailed("1 <= len(self.base_stations) failed")
        if self.qaqc_magnetic_azimuth_test_list is not None:
            if not isinstance(self.qaqc_magnetic_azimuth_test_list, list):
                raise ValidationFailed("self.qaqc_magnetic_azimuth_test_list is not a list")
            for v in self.qaqc_magnetic_azimuth_test_list:
                if not isinstance(v, SurveyLine_V1_1_0):
                    raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if self.qaqc_noise_test_list is not None:
            if not isinstance(self.qaqc_noise_test_list, list):
                raise ValidationFailed("self.qaqc_noise_test_list is not a list")
            for v in self.qaqc_noise_test_list:
                if not isinstance(v, SurveyLine_V1_1_0):
                    raise ValidationFailed("v is not SurveyLine_V1_1_0")
