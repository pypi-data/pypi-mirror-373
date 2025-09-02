import dataclasses

from ..elements.integer_array_1 import IntegerArray1_V1_0_1
from ..elements.lookup_table import LookupTable_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class CategoryData_V1_0_1(Serialiser):
    """A base-class that describes a category lookup attribute"""

    SCHEMA_ID = "/components/category-data/1.0.1/category-data.schema.json"

    table: LookupTable_V1_0_1
    """Lookup table associated with the attributes."""
    values: IntegerArray1_V1_0_1
    """The index values of the attributes."""

    def __post_init__(self):
        if not isinstance(self.table, LookupTable_V1_0_1):
            raise ValidationFailed("self.table is not LookupTable_V1_0_1")
        if not isinstance(self.values, IntegerArray1_V1_0_1):
            raise ValidationFailed("self.values is not IntegerArray1_V1_0_1")
