import dataclasses
import typing
import uuid

from ..elements.serialiser import Serialiser, ValidationFailed
from .lineage import Lineage_V1_0_0

BaseObjectProperties_V1_0_1_Uuid = uuid.UUID | None


def is_base_object_properties_v1_0_1_uuid(value):
    if isinstance(value, uuid.UUID):
        # Previously assigned universally unique identifier.
        return True
    if value is None:
        # Identifier used for a new object.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class BaseObjectProperties_V1_0_1(Serialiser):
    """Properties common to all types of Geoscience Objects such as their name, unique identifier."""

    SCHEMA_ID = "/components/base-object-properties/1.0.1/base-object-properties.schema.json"

    name: str
    """Name of the object."""
    uuid: BaseObjectProperties_V1_0_1_Uuid
    """Identifier of the object."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    extensions: dict[str, typing.Any] | None = None
    """Extended properties that may be associated to the object, but not specified in the schema"""
    tags: dict[str, str] | None = None
    """Key-value pairs of user-defined metadata"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not is_base_object_properties_v1_0_1_uuid(self.uuid):
            raise ValidationFailed("is_base_object_properties_v1_0_1_uuid(self.uuid) failed")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.extensions is not None:
            if not isinstance(self.extensions, dict):
                raise ValidationFailed("self.extensions is not a dict")
            for k in self.extensions:
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
        if self.tags is not None:
            if not isinstance(self.tags, dict):
                raise ValidationFailed("self.tags is not a dict")
            for k, v in self.tags.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, str):
                    raise ValidationFailed("v is not str")


BaseObjectProperties_V1_1_0_Uuid = uuid.UUID | None


def is_base_object_properties_v1_1_0_uuid(value):
    if isinstance(value, uuid.UUID):
        # Previously assigned universally unique identifier.
        return True
    if value is None:
        # Identifier used for a new object.
        return True
    return False


@dataclasses.dataclass(kw_only=True)
class BaseObjectProperties_V1_1_0(Serialiser):
    """Properties common to all types of Geoscience Objects such as their name, unique identifier."""

    SCHEMA_ID = "/components/base-object-properties/1.1.0/base-object-properties.schema.json"

    name: str
    """Name of the object."""
    uuid: BaseObjectProperties_V1_1_0_Uuid
    """Identifier of the object."""
    description: str | None = None
    """Optional field for adding additional description to uniquely identify this object."""
    extensions: dict[str, typing.Any] | None = None
    """Extended properties that may be associated to the object, but not specified in the schema"""
    tags: dict[str, str] | None = None
    """Key-value pairs of user-defined metadata"""
    lineage: Lineage_V1_0_0 | None = None
    """Information about the history of the object"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not is_base_object_properties_v1_1_0_uuid(self.uuid):
            raise ValidationFailed("is_base_object_properties_v1_1_0_uuid(self.uuid) failed")
        if self.description is not None:
            if not isinstance(self.description, str):
                raise ValidationFailed("self.description is not str")
        if self.extensions is not None:
            if not isinstance(self.extensions, dict):
                raise ValidationFailed("self.extensions is not a dict")
            for k in self.extensions:
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
        if self.tags is not None:
            if not isinstance(self.tags, dict):
                raise ValidationFailed("self.tags is not a dict")
            for k, v in self.tags.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, str):
                    raise ValidationFailed("v is not str")
        if self.lineage is not None:
            if not isinstance(self.lineage, Lineage_V1_0_0):
                raise ValidationFailed("self.lineage is not Lineage_V1_0_0")
