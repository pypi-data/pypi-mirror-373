import dataclasses

from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class LineationData_V1_0_1(Serialiser):
    """An extension used to associate lineation data with locations."""

    SCHEMA_ID = "/components/lineation-data/1.0.1/lineation-data.schema.json"

    lineations: FloatArray2_V1_0_1
    """Lineation data. Columns: trend, plunge."""

    def __post_init__(self):
        if not isinstance(self.lineations, FloatArray2_V1_0_1):
            raise ValidationFailed("self.lineations is not FloatArray2_V1_0_1")
