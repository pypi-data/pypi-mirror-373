import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories
from .intervals import Intervals_V1_0_1


@dataclasses.dataclass(kw_only=True)
class FromTo_V1_0_1(Serialiser):
    """From-to description."""

    SCHEMA_ID = "/components/from-to/1.0.1/from-to.schema.json"

    intervals: Intervals_V1_0_1
    """From-to intervals. Columns: from, to."""
    unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Unit"""

    def __post_init__(self):
        if not isinstance(self.intervals, Intervals_V1_0_1):
            raise ValidationFailed("self.intervals is not Intervals_V1_0_1")
        if self.unit is not None:
            if not isinstance(self.unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.unit is not UnitLength_V1_0_1_UnitCategories")
