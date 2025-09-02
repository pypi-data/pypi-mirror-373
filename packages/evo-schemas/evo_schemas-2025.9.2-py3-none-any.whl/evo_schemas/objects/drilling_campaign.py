import dataclasses

from ..components.attribute_list_property import AttributeListProperty_V1_2_0
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_1_0
from ..components.category_data import CategoryData_V1_0_1
from ..components.desurvey_method import DesurveyMethod_V1_0_0
from ..components.downhole_attributes import DownholeAttributes_V1_0_0, DownholeAttributes_V1_0_0_Item
from ..components.downhole_direction_vector import DownholeDirectionVector_V1_0_0
from ..components.hole_collars import HoleCollars_V1_0_0
from ..elements.float_array_6 import FloatArray6_V1_0_1
from ..elements.float_array_md import FloatArrayMd_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.string_array import StringArray_V1_0_1
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0_Planned_Path_NaturalDeviation(FloatArray6_V1_0_1, AttributeListProperty_V1_2_0):
    """The path taken by the planned drillhole using only natural deviations. Columns: distance, azimuth, dip, lift rate, drift rate, deviation rate distance"""

    deviation_type: str = "natural"
    """Type of deviation"""

    def __post_init__(self):
        FloatArray6_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.deviation_type, str):
            raise ValidationFailed("self.deviation_type is not str")
        if not self.deviation_type == "natural":
            raise ValidationFailed('self.deviation_type == "natural" failed')


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation_SegmentProperties(FloatArrayMd_V1_0_1):
    """The path taken by the planned drillhole using both natural and directed deviations. Columns: distance, azimuth, dip, lift rate, drift rate, deviation rate distance, toolface angle, dogleg severity"""

    width: int = 8
    """number of columns"""

    def __post_init__(self):
        FloatArrayMd_V1_0_1.__post_init__(self)
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 8:
            raise ValidationFailed("self.width == 8 failed")


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation(AttributeListProperty_V1_2_0):
    """The path taken by the planned drillhole using both natural and directed deviations."""

    segment_type: StringArray_V1_0_1
    """Type of segment deviation, 'natural' or 'directed'"""
    segment_properties: DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation_SegmentProperties
    """The path taken by the planned drillhole using both natural and directed deviations. Columns: distance, azimuth, dip, lift rate, drift rate, deviation rate distance, toolface angle, dogleg severity"""
    deviation_type: str = "mixed"
    """Type of deviation"""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.segment_type, StringArray_V1_0_1):
            raise ValidationFailed("self.segment_type is not StringArray_V1_0_1")
        if not isinstance(
            self.segment_properties, DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation_SegmentProperties
        ):
            raise ValidationFailed(
                "self.segment_properties is not DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation_SegmentProperties"
            )
        if not isinstance(self.deviation_type, str):
            raise ValidationFailed("self.deviation_type is not str")
        if not self.deviation_type == "mixed":
            raise ValidationFailed('self.deviation_type == "mixed" failed')


DrillingCampaign_V1_0_0_Planned_Path = (
    DrillingCampaign_V1_0_0_Planned_Path_NaturalDeviation | DrillingCampaign_V1_0_0_Planned_Path_MixedDeviation
)


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0_Planned(Serialiser):
    """Planned data for the drilling campaign."""

    collar: HoleCollars_V1_0_0
    """Collar data for the planned drillholes."""
    path: DrillingCampaign_V1_0_0_Planned_Path
    """The path taken by the downhole segment. Columns required depends on deviations used."""
    collections: DownholeAttributes_V1_0_0 | None = None
    """Projected attributes for the planned drillholes."""

    def __post_init__(self):
        if not isinstance(self.collar, HoleCollars_V1_0_0):
            raise ValidationFailed("self.collar is not HoleCollars_V1_0_0")
        if not isinstance(self.path, DrillingCampaign_V1_0_0_Planned_Path):
            raise ValidationFailed("self.path is not DrillingCampaign_V1_0_0_Planned_Path")
        if self.collections is not None:
            if not isinstance(self.collections, list):
                raise ValidationFailed("self.collections is not a list")
            for v in self.collections:
                if not isinstance(v, DownholeAttributes_V1_0_0_Item):
                    raise ValidationFailed("v is not DownholeAttributes_V1_0_0_Item")


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0_Interim(Serialiser):
    """Interim drillhole data for the drilling campaign."""

    collar: HoleCollars_V1_0_0
    """Collar data for the interim drillholes."""
    path: DownholeDirectionVector_V1_0_0
    """The path taken by the downhole segment. Columns: distance, azimuth, dip."""
    desurvey: DesurveyMethod_V1_0_0 | None = None
    """The desurvey method used."""
    collections: DownholeAttributes_V1_0_0 | None = None
    """Collection of attributes for the interim drilling data."""

    def __post_init__(self):
        if not isinstance(self.collar, HoleCollars_V1_0_0):
            raise ValidationFailed("self.collar is not HoleCollars_V1_0_0")
        if not isinstance(self.path, DownholeDirectionVector_V1_0_0):
            raise ValidationFailed("self.path is not DownholeDirectionVector_V1_0_0")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, DesurveyMethod_V1_0_0):
                raise ValidationFailed("self.desurvey is not DesurveyMethod_V1_0_0")
        if self.collections is not None:
            if not isinstance(self.collections, list):
                raise ValidationFailed("self.collections is not a list")
            for v in self.collections:
                if not isinstance(v, DownholeAttributes_V1_0_0_Item):
                    raise ValidationFailed("v is not DownholeAttributes_V1_0_0_Item")


@dataclasses.dataclass(kw_only=True)
class DrillingCampaign_V1_0_0(BaseSpatialDataProperties_V1_1_0):
    """A planned drillholes and interim drillhole data for a drilling campaign."""

    SCHEMA_ID = "/objects/drilling-campaign/1.0.0/drilling-campaign.schema.json"

    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    planned: DrillingCampaign_V1_0_0_Planned
    """Planned data for the drilling campaign."""
    schema: str = "/objects/drilling-campaign/1.0.0/drilling-campaign.schema.json"
    type: str = "campaign"
    """The type of the planned drillholes."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """The units of depth for the drillholes."""
    interim: DrillingCampaign_V1_0_0_Interim | None = None
    """Interim drillhole data for the drilling campaign."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.planned, DrillingCampaign_V1_0_0_Planned):
            raise ValidationFailed("self.planned is not DrillingCampaign_V1_0_0_Planned")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/drilling-campaign/1.0.0/drilling-campaign.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/drilling-campaign/1.0.0/drilling-campaign.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "campaign":
            raise ValidationFailed('self.type == "campaign" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.interim is not None:
            if not isinstance(self.interim, DrillingCampaign_V1_0_0_Interim):
                raise ValidationFailed("self.interim is not DrillingCampaign_V1_0_0_Interim")
