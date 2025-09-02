import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .surface_mesh import SurfaceMesh_V1_0_1


@dataclasses.dataclass(kw_only=True)
class BrepContainer_V1_0_1_Brep(Serialiser):
    """BRep object."""

    data: BinaryBlob_V1_0_1
    """Data stored as a binary blob."""
    length: int = 0
    """length of array"""
    width: int = 1
    """number of columns"""
    data_type: str = "uint8"
    """Data type."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 1:
            raise ValidationFailed("self.width == 1 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "uint8":
            raise ValidationFailed('self.data_type == "uint8" failed')


@dataclasses.dataclass(kw_only=True)
class BrepContainer_V1_0_1(Serialiser):
    """This component describes a BRep container."""

    SCHEMA_ID = "/components/brep-container/1.0.1/brep-container.schema.json"

    format: str
    """The format."""
    producer: str
    """Product used to generate the BREP."""
    brep: BrepContainer_V1_0_1_Brep
    """BRep object."""
    discretized_brep: SurfaceMesh_V1_0_1 | None = None
    """Optional discretized version of BREP data."""

    def __post_init__(self):
        if not isinstance(self.format, str):
            raise ValidationFailed("self.format is not str")
        if not isinstance(self.producer, str):
            raise ValidationFailed("self.producer is not str")
        if not isinstance(self.brep, BrepContainer_V1_0_1_Brep):
            raise ValidationFailed("self.brep is not BrepContainer_V1_0_1_Brep")
        if self.discretized_brep is not None:
            if not isinstance(self.discretized_brep, SurfaceMesh_V1_0_1):
                raise ValidationFailed("self.discretized_brep is not SurfaceMesh_V1_0_1")
