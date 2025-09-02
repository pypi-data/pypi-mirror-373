import dataclasses

from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.resistivity_ip_dcip_survey_properties import ResistivityIpDcipSurveyProperties_V1_0_0
from ..components.resistivity_ip_line import ResistivityIpLine_V1_1_0
from ..components.resistivity_ip_phaseip_survey_properties import ResistivityIpPhaseipSurveyProperties_V1_0_0
from ..components.resistivity_ip_pldp_configuration_properties import ResistivityIpPldpConfigurationProperties_V1_0_0
from ..components.resistivity_ip_plpl_configuration_properties import ResistivityIpPlplConfigurationProperties_V1_0_0
from ..components.resistivity_ip_sip_survey_properties import ResistivityIpSipSurveyProperties_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_1_0_Survey_Type(Serialiser):
    type: str = "DCRES"
    """Type of survey."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "DCRES":
            raise ValidationFailed('self.type == "DCRES" failed')


ResistivityIp_V1_1_0_Survey = (
    ResistivityIpDcipSurveyProperties_V1_0_0
    | ResistivityIpSipSurveyProperties_V1_0_0
    | ResistivityIpPhaseipSurveyProperties_V1_0_0
    | ResistivityIp_V1_1_0_Survey_Type
)


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_1_0_Configuration_Type(Serialiser):
    type: str
    """Type of configuration."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GRAD", "SCHL", "WENN", "DPDP", "DPPL", "SBH", "BHBH", "EDPDP", "VECTOR", "GENERAL"):
            raise ValidationFailed(
                'self.type in ("GRAD", "SCHL", "WENN", "DPDP", "DPPL", "SBH", "BHBH", "EDPDP", "VECTOR", "GENERAL") failed'
            )


ResistivityIp_V1_1_0_Configuration = (
    ResistivityIpPlplConfigurationProperties_V1_0_0
    | ResistivityIpPldpConfigurationProperties_V1_0_0
    | ResistivityIp_V1_1_0_Configuration_Type
)


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_1_0(BaseSpatialDataProperties_V1_1_0):
    """Resistivity-IP data."""

    SCHEMA_ID = "/objects/resistivity-ip/1.1.0/resistivity-ip.schema.json"

    number_of_dimensions: str
    """Survey dimension."""
    number_contributing_electrodes: int
    """Number of contributing electrodes. Not including remote electrodes."""
    survey: ResistivityIp_V1_1_0_Survey
    """Survey information."""
    configuration: ResistivityIp_V1_1_0_Configuration
    """Configuration information."""
    line_list: list[ResistivityIpLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/resistivity-ip/1.1.0/resistivity-ip.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.number_of_dimensions, str):
            raise ValidationFailed("self.number_of_dimensions is not str")
        if self.number_of_dimensions not in ("1D", "2D", "3D"):
            raise ValidationFailed('self.number_of_dimensions in ("1D", "2D", "3D") failed')
        if not isinstance(self.number_contributing_electrodes, int):
            raise ValidationFailed("self.number_contributing_electrodes is not int")
        if not 1 <= self.number_contributing_electrodes:
            raise ValidationFailed("1 <= self.number_contributing_electrodes failed")
        if not isinstance(self.survey, ResistivityIp_V1_1_0_Survey):
            raise ValidationFailed("self.survey is not ResistivityIp_V1_1_0_Survey")
        if not isinstance(self.configuration, ResistivityIp_V1_1_0_Configuration):
            raise ValidationFailed("self.configuration is not ResistivityIp_V1_1_0_Configuration")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, ResistivityIpLine_V1_1_0):
                raise ValidationFailed("v is not ResistivityIpLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/resistivity-ip/1.1.0/resistivity-ip.schema.json":
            raise ValidationFailed('self.schema == "/objects/resistivity-ip/1.1.0/resistivity-ip.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_0_0_Survey_Type(Serialiser):
    type: str = "DCRES"
    """Type of survey."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "DCRES":
            raise ValidationFailed('self.type == "DCRES" failed')


ResistivityIp_V1_0_0_Survey = (
    ResistivityIpDcipSurveyProperties_V1_0_0
    | ResistivityIpSipSurveyProperties_V1_0_0
    | ResistivityIpPhaseipSurveyProperties_V1_0_0
    | ResistivityIp_V1_0_0_Survey_Type
)


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_0_0_Configuration_Type(Serialiser):
    type: str
    """Type of configuration."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GRAD", "SCHL", "WENN", "DPDP", "DPPL", "SBH", "BHBH", "EDPDP", "VECTOR", "GENERAL"):
            raise ValidationFailed(
                'self.type in ("GRAD", "SCHL", "WENN", "DPDP", "DPPL", "SBH", "BHBH", "EDPDP", "VECTOR", "GENERAL") failed'
            )


ResistivityIp_V1_0_0_Configuration = (
    ResistivityIpPlplConfigurationProperties_V1_0_0
    | ResistivityIpPldpConfigurationProperties_V1_0_0
    | ResistivityIp_V1_0_0_Configuration_Type
)


@dataclasses.dataclass(kw_only=True)
class ResistivityIp_V1_0_0(BaseSpatialDataProperties_V1_0_1):
    """Resistivity-IP data."""

    SCHEMA_ID = "/objects/resistivity-ip/1.0.0/resistivity-ip.schema.json"

    number_of_dimensions: str
    """Survey dimension."""
    number_contributing_electrodes: int
    """Number of contributing electrodes. Not including remote electrodes."""
    survey: ResistivityIp_V1_0_0_Survey
    """Survey information."""
    configuration: ResistivityIp_V1_0_0_Configuration
    """Configuration information."""
    line_list: list[ResistivityIpLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/resistivity-ip/1.0.0/resistivity-ip.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_dimensions, str):
            raise ValidationFailed("self.number_of_dimensions is not str")
        if self.number_of_dimensions not in ("1D", "2D", "3D"):
            raise ValidationFailed('self.number_of_dimensions in ("1D", "2D", "3D") failed')
        if not isinstance(self.number_contributing_electrodes, int):
            raise ValidationFailed("self.number_contributing_electrodes is not int")
        if not 1 <= self.number_contributing_electrodes:
            raise ValidationFailed("1 <= self.number_contributing_electrodes failed")
        if not isinstance(self.survey, ResistivityIp_V1_0_0_Survey):
            raise ValidationFailed("self.survey is not ResistivityIp_V1_0_0_Survey")
        if not isinstance(self.configuration, ResistivityIp_V1_0_0_Configuration):
            raise ValidationFailed("self.configuration is not ResistivityIp_V1_0_0_Configuration")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, ResistivityIpLine_V1_1_0):
                raise ValidationFailed("v is not ResistivityIpLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/resistivity-ip/1.0.0/resistivity-ip.schema.json":
            raise ValidationFailed('self.schema == "/objects/resistivity-ip/1.0.0/resistivity-ip.schema.json" failed')
