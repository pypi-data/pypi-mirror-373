import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class MeshQuality_V1_0_1(Serialiser):
    """This component describes a mesh quality."""

    SCHEMA_ID = "/components/mesh-quality/1.0.1/mesh-quality.schema.json"

    characteristics: list[str]
    """Mesh characteristics."""

    def __post_init__(self):
        if not isinstance(self.characteristics, list):
            raise ValidationFailed("self.characteristics is not a list")
        for v in self.characteristics:
            if not isinstance(v, str):
                raise ValidationFailed("v is not str")
            if v not in ("Manifold", "ConsistentWinding", "NonDegenerate", "NonSelfIntersecting", "Continuous"):
                raise ValidationFailed(
                    'v in ("Manifold", "ConsistentWinding", "NonDegenerate", "NonSelfIntersecting", "Continuous") failed'
                )
