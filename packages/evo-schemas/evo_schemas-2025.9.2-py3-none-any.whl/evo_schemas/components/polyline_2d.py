import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Polyline2D_V1_0_1(Serialiser):
    """This component describes a 2D polyline."""

    SCHEMA_ID = "/components/polyline-2d/1.0.1/polyline-2d.schema.json"

    begin: int
    """Index of the first line segment in lines-2d."""
    count: int
    """The number of line segments."""
    closed: str
    """Closed or open."""
    shape: str
    """Straight or curved."""

    def __post_init__(self):
        if not isinstance(self.begin, int):
            raise ValidationFailed("self.begin is not int")
        if not 0 <= self.begin:
            raise ValidationFailed("0 <= self.begin failed")
        if not isinstance(self.count, int):
            raise ValidationFailed("self.count is not int")
        if not 0 <= self.count:
            raise ValidationFailed("0 <= self.count failed")
        if not isinstance(self.closed, str):
            raise ValidationFailed("self.closed is not str")
        if self.closed not in ("Open", "Closed"):
            raise ValidationFailed('self.closed in ("Open", "Closed") failed')
        if not isinstance(self.shape, str):
            raise ValidationFailed("self.shape is not str")
        if self.shape not in ("Straight", "Curved"):
            raise ValidationFailed('self.shape in ("Straight", "Curved") failed')
