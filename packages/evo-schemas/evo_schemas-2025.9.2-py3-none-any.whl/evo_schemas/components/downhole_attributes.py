import dataclasses

from ..elements.serialiser import ValidationFailed
from .data_table import DataTable_V1_2_0
from .distance_table import DistanceTable_V1_2_0
from .hole_chunks import HoleChunks_V1_0_0
from .interval_table import IntervalTable_V1_2_0
from .relative_lineation_data_table import RelativeLineationDataTable_V1_2_0
from .relative_planar_data_table import RelativePlanarDataTable_V1_2_0


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_DataTable(DataTable_V1_2_0):
    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_DistanceTable(DistanceTable_V1_2_0):
    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_IntervalTable(IntervalTable_V1_2_0):
    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_RelativePlanarDataTable(RelativePlanarDataTable_V1_2_0):
    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_RelativeLineationDataTable(RelativeLineationDataTable_V1_2_0):
    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


DownholeAttributes_V1_0_0_Item = (
    DownholeAttributes_V1_0_0_Item_DataTable
    | DownholeAttributes_V1_0_0_Item_DistanceTable
    | DownholeAttributes_V1_0_0_Item_IntervalTable
    | DownholeAttributes_V1_0_0_Item_RelativePlanarDataTable
    | DownholeAttributes_V1_0_0_Item_RelativeLineationDataTable
)
DownholeAttributes_V1_0_0 = list[DownholeAttributes_V1_0_0_Item]
