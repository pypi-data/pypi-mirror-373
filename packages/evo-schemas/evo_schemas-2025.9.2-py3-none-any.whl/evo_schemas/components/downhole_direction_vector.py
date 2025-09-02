import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from .attribute_list_property import AttributeListProperty_V1_2_0


@dataclasses.dataclass(kw_only=True)
class DownholeDirectionVector_V1_0_0(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Represents the direction and size of a downhole segment and any associated attributes. Columns: distance, azimuth, dip."""

    SCHEMA_ID = "/components/downhole-direction-vector/1.0.0/downhole-direction-vector.schema.json"

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
