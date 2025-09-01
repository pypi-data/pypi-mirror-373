# Models
import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Add a string enum for observation kinds
class ObservationKind(StrEnum):
    NOTE = "note"
    SNIPPET = "snippet"
    ERROR = "error"
    COMMAND = "command"
    QA = "qa"


class Observation(BaseModel):
    kind: ObservationKind = ObservationKind.NOTE
    text: str | None = None
    code: str | None = None
    language: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    hash: str | None = None


class Entity(BaseModel):
    name: str
    entity_type: str = "Concept"
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    observations: list[Observation] = Field(default_factory=list)


class Relation(BaseModel):
    from_: str = Field(serialization_alias="from", validation_alias="from")
    to: str
    relation_type: str = "related"
    confidence: float | None = None
    source: str | None = None
    model_config = ConfigDict(populate_by_name=True)


class KnowledgeGraph(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relations: list[Relation] = Field(default_factory=list)


# Payload models
class ObservationAdd(BaseModel):
    entity_name: str
    contents: list[Observation | str]


class ObservationDeletion(BaseModel):
    entity_name: str
    observations: list[str]


class Event(BaseModel):
    type: str
    ts: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    payload: dict[str, Any]
