import dataclasses
import typing
import uuid

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent_Run(Serialiser):
    runId: uuid.UUID
    """The globally unique ID of the run associated with the job."""
    facets: dict[str, dict[str, typing.Any]] | None = None
    """The run facets."""

    def __post_init__(self):
        if not isinstance(self.runId, uuid.UUID):
            raise ValidationFailed("self.runId is not uuid.UUID")
        if self.facets is not None:
            if not isinstance(self.facets, dict):
                raise ValidationFailed("self.facets is not a dict")
            for k, v in self.facets.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, dict):
                    raise ValidationFailed("v is not a dict")
                for k in v:
                    if not isinstance(k, str):
                        raise ValidationFailed("isinstance(k, str) failed")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent_Job(Serialiser):
    namespace: str
    """The namespace containing that job"""
    name: str
    """The unique name for that job within that namespace"""
    facets: dict[str, dict[str, typing.Any]] | None = None
    """The job facets."""

    def __post_init__(self):
        if not isinstance(self.namespace, str):
            raise ValidationFailed("self.namespace is not str")
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if self.facets is not None:
            if not isinstance(self.facets, dict):
                raise ValidationFailed("self.facets is not a dict")
            for k, v in self.facets.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, dict):
                    raise ValidationFailed("v is not a dict")
                for k in v:
                    if not isinstance(k, str):
                        raise ValidationFailed("isinstance(k, str) failed")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent_Inputdataset_Dataset(Serialiser):
    namespace: str
    """The namespace containing that dataset"""
    name: str
    """The unique name for that dataset within that namespace"""
    facets: dict[str, dict[str, typing.Any]] | None = None
    """The facets for this dataset"""

    def __post_init__(self):
        if not isinstance(self.namespace, str):
            raise ValidationFailed("self.namespace is not str")
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if self.facets is not None:
            if not isinstance(self.facets, dict):
                raise ValidationFailed("self.facets is not a dict")
            for k, v in self.facets.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, dict):
                    raise ValidationFailed("v is not a dict")
                for k in v:
                    if not isinstance(k, str):
                        raise ValidationFailed("isinstance(k, str) failed")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent_Inputdataset(Lineage_V1_0_0_Runevent_Inputdataset_Dataset):
    """An input dataset"""

    inputFacets: dict[str, dict[str, typing.Any]] | None = None
    """The input facets for this dataset."""

    def __post_init__(self):
        Lineage_V1_0_0_Runevent_Inputdataset_Dataset.__post_init__(self)
        if self.inputFacets is not None:
            if not isinstance(self.inputFacets, dict):
                raise ValidationFailed("self.inputFacets is not a dict")
            for k, v in self.inputFacets.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, dict):
                    raise ValidationFailed("v is not a dict")
                for k in v:
                    if not isinstance(k, str):
                        raise ValidationFailed("isinstance(k, str) failed")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent_Outputdataset(Lineage_V1_0_0_Runevent_Inputdataset_Dataset):
    """An output dataset"""

    outputFacets: dict[str, dict[str, typing.Any]] | None = None
    """The output facets for this dataset"""

    def __post_init__(self):
        Lineage_V1_0_0_Runevent_Inputdataset_Dataset.__post_init__(self)
        if self.outputFacets is not None:
            if not isinstance(self.outputFacets, dict):
                raise ValidationFailed("self.outputFacets is not a dict")
            for k, v in self.outputFacets.items():
                if not isinstance(k, str):
                    raise ValidationFailed("isinstance(k, str) failed")
                if not isinstance(v, dict):
                    raise ValidationFailed("v is not a dict")
                for k in v:
                    if not isinstance(k, str):
                        raise ValidationFailed("isinstance(k, str) failed")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0_Runevent(Serialiser):
    eventTime: str
    """the time the event occurred at"""
    producer: str
    """URI identifying the producer of this metadata. For example this could be a git url with a given tag or sha"""
    schemaURL: str
    """URI identifying the corresponding version of the schema definition for this RunEvent"""
    run: Lineage_V1_0_0_Runevent_Run
    job: Lineage_V1_0_0_Runevent_Job
    eventType: str | None = None
    """the current transition of the run state. It is required to issue 1 START event and 1 of [ COMPLETE, ABORT, FAIL ] event per run. Additional events with OTHER eventType can be added to the same run. For example to send additional metadata after the run is complete"""
    inputs: list[Lineage_V1_0_0_Runevent_Inputdataset] | None = None
    """The set of **input** datasets."""
    outputs: list[Lineage_V1_0_0_Runevent_Outputdataset] | None = None
    """The set of **output** datasets."""

    def __post_init__(self):
        if not isinstance(self.eventTime, str):
            raise ValidationFailed("self.eventTime is not str")
        if not Serialiser.is_date_time(self.eventTime):
            raise ValidationFailed("Serialiser.is_date_time(self.eventTime) failed")
        if not isinstance(self.producer, str):
            raise ValidationFailed("self.producer is not str")
        if not Serialiser.is_uri(self.producer):
            raise ValidationFailed("Serialiser.is_uri(self.producer) failed")
        if not isinstance(self.schemaURL, str):
            raise ValidationFailed("self.schemaURL is not str")
        if not Serialiser.is_uri(self.schemaURL):
            raise ValidationFailed("Serialiser.is_uri(self.schemaURL) failed")
        if not isinstance(self.run, Lineage_V1_0_0_Runevent_Run):
            raise ValidationFailed("self.run is not Lineage_V1_0_0_Runevent_Run")
        if not isinstance(self.job, Lineage_V1_0_0_Runevent_Job):
            raise ValidationFailed("self.job is not Lineage_V1_0_0_Runevent_Job")
        if self.eventType is not None:
            if not isinstance(self.eventType, str):
                raise ValidationFailed("self.eventType is not str")
            if self.eventType not in ("START", "RUNNING", "COMPLETE", "ABORT", "FAIL", "OTHER"):
                raise ValidationFailed(
                    'self.eventType in ("START", "RUNNING", "COMPLETE", "ABORT", "FAIL", "OTHER") failed'
                )
        if self.inputs is not None:
            if not isinstance(self.inputs, list):
                raise ValidationFailed("self.inputs is not a list")
            for v in self.inputs:
                if not isinstance(v, Lineage_V1_0_0_Runevent_Inputdataset):
                    raise ValidationFailed("v is not Lineage_V1_0_0_Runevent_Inputdataset")
        if self.outputs is not None:
            if not isinstance(self.outputs, list):
                raise ValidationFailed("self.outputs is not a list")
            for v in self.outputs:
                if not isinstance(v, Lineage_V1_0_0_Runevent_Outputdataset):
                    raise ValidationFailed("v is not Lineage_V1_0_0_Runevent_Outputdataset")


@dataclasses.dataclass(kw_only=True)
class Lineage_V1_0_0(Serialiser):
    """Events describing segments of the input lineage graph of this object"""

    SCHEMA_ID = "/components/lineage/1.0.0/lineage.schema.json"

    events: list[Lineage_V1_0_0_Runevent]
    """List of zero or more OpenLineage run events"""
    self_link: str | None = None
    """Self link pointing to where this Geoscience Object is referenced within the events array"""

    def __post_init__(self):
        if not isinstance(self.events, list):
            raise ValidationFailed("self.events is not a list")
        for v in self.events:
            if not isinstance(v, Lineage_V1_0_0_Runevent):
                raise ValidationFailed("v is not Lineage_V1_0_0_Runevent")
        if self.self_link is not None:
            if not isinstance(self.self_link, str):
                raise ValidationFailed("self.self_link is not str")
            if not Serialiser.is_json_pointer(self.self_link):
                raise ValidationFailed("Serialiser.is_json_pointer(self.self_link) failed")
