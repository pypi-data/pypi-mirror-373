from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from threading import RLock
from typing import Any

from mcp_agentmemory.models import (
    Entity,
    Event,
    KnowledgeGraph,
    Observation,
    ObservationAdd,
    ObservationKind,
    Relation,
)


class KnowledgeGraphManager:
    def __init__(self, snapshot: Path, log: Path):
        self.snapshot_path = snapshot
        self.log_path = log
        self._lock = RLock()
        self._graph = KnowledgeGraph()
        self._entities: dict[str, Entity] = {}
        self._load_data()

    def _normalize_tags(self, tags: list[str] | None) -> list[str]:
        if not tags:
            return []
        return list(dict.fromkeys(tag.strip().lower() for tag in tags if tag.strip()))

    def _generate_hash(self, obs: Observation) -> str:
        content = {
            "kind": obs.kind,
            "text": (obs.text or "").strip(),
            "code": (obs.code or "").strip(),
            "language": (obs.language or "").lower() if obs.language else None,
            "tags": sorted(self._normalize_tags(obs.tags)),
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def _append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        with self._lock:
            event = Event(type=event_type, payload=payload)
            with self.log_path.open("a", encoding="utf-8") as f:
                print(event.model_dump_json(), file=f)

    def _load_data(self) -> None:
        # Load snapshot
        if self.snapshot_path.exists():
            try:
                data = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
                self._graph = KnowledgeGraph.model_validate(data)
            except Exception:
                self._graph = KnowledgeGraph()

        # Build entity index
        self._entities = {e.name: e for e in self._graph.entities}

        # Replay log
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        event = Event.model_validate_json(line)
                        self._apply_event(event)

    def _apply_event(self, event: Event) -> None:
        # Simplified event application - just the essentials
        if event.type == "entity_upserted":
            self._update_entity_from_payload(event.payload)
        elif event.type == "relation_created":
            rel = Relation.model_validate(event.payload)
            if not self._relation_exists(rel):
                self._graph.relations.append(rel)
        elif event.type == "insight_added":
            self._add_insight_from_payload(event.payload)

    def _update_entity_from_payload(self, payload: dict) -> None:
        name = payload["name"]
        entity = self._entities.get(name)
        if not entity:
            entity = Entity(name=name)
            self._graph.entities.append(entity)
            self._entities[name] = entity

        if "entity_type" in payload:
            entity.entity_type = payload["entity_type"]
        if "description" in payload:
            entity.description = payload["description"]
        if "tags" in payload:
            entity.tags = self._normalize_tags(payload["tags"])

    def _add_insight_from_payload(self, payload: dict) -> None:
        entity_name = payload["entity_name"]
        obs_data = payload["observation"]
        obs = Observation.model_validate(obs_data)

        entity = self._entities.get(entity_name)
        if entity and not any(o.hash == obs.hash for o in entity.observations):
            entity.observations.append(obs)

    def _relation_exists(self, rel: Relation) -> bool:
        return any(
            r.from_ == rel.from_
            and r.to == rel.to
            and r.relation_type == rel.relation_type
            for r in self._graph.relations
        )

    def _get_or_create_entity(
        self, name: str, entity_type: str | None = None
    ) -> Entity:
        entity = self._entities.get(name)
        if not entity:
            entity = Entity(name=name, entity_type=entity_type or "Concept")
            self._graph.entities.append(entity)
            self._entities[name] = entity
        return entity

    # Public API methods (simplified)
    def upsert_entity(
        self,
        name: str,
        entity_type: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
    ) -> Entity:
        with self._lock:
            entity = self._get_or_create_entity(name, entity_type)

            if entity_type:
                entity.entity_type = entity_type
            if description is not None:
                entity.description = description
            if tags is not None:
                normalized_tags = self._normalize_tags(tags)
                entity.tags = list(dict.fromkeys(entity.tags + normalized_tags))

            self._append_event(
                "entity_upserted",
                {
                    "name": name,
                    "entity_type": entity.entity_type,
                    "tags": entity.tags,
                    "description": entity.description,
                },
            )
            return Entity.model_validate(entity.model_dump())

    def create_relations(self, relations: list[Relation]) -> list[Relation]:
        created = []
        with self._lock:
            for rel in relations:
                # Ensure referenced entities exist
                self._get_or_create_entity(rel.from_)
                self._get_or_create_entity(rel.to)

                if not self._relation_exists(rel):
                    self._graph.relations.append(rel)
                    self._append_event(
                        "relation_created", rel.model_dump(by_alias=True)
                    )
                    created.append(rel)
        return created

    def add_insights(self, items: list[ObservationAdd]) -> list[dict]:
        results = []
        with self._lock:
            for item in items:
                entity = self._get_or_create_entity(item.entity_name)
                added = []

                for content in item.contents:
                    if isinstance(content, str):
                        obs = Observation(kind=ObservationKind.NOTE, text=content)
                    else:
                        obs = content

                    obs.tags = self._normalize_tags(obs.tags)
                    obs.hash = self._generate_hash(obs)

                    if not any(o.hash == obs.hash for o in entity.observations):
                        entity.observations.append(obs)
                        self._append_event(
                            "insight_added",
                            {
                                "entity_name": entity.name,
                                "observation": obs.model_dump(),
                            },
                        )
                        added.append(obs.hash)

                results.append({"entity_name": entity.name, "added": added})
        return results

    def read_graph(self) -> KnowledgeGraph:
        with self._lock:
            return KnowledgeGraph.model_validate(self._graph.model_dump())

    def search_insights(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        kinds: list[str] | None = None,
        language: str | None = None,
    ) -> KnowledgeGraph:
        with self._lock:
            query_lower = (query or "").lower()
            tag_set = set(self._normalize_tags(tags)) if tags else set()
            kind_set = set(kinds) if kinds else set()

            matching_entities = []
            for entity in self._graph.entities:
                # build matching observations with a list comprehension
                matching_obs = [
                    obs
                    for obs in entity.observations
                    if self._matches_criteria(
                        obs, query_lower, tag_set, kind_set, language
                    )
                ]

                # Match on entity tags if tag filter is provided and no obs matched
                entity_tag_match = bool(tag_set and tag_set.intersection(set(entity.tags)))

                if entity_tag_match and not matching_obs:
                    matching_obs = list(entity.observations)

                if matching_obs or entity_tag_match:
                    matching_entities.append(
                        Entity(
                            name=entity.name,
                            entity_type=entity.entity_type,
                            tags=entity.tags,
                            description=entity.description,
                            observations=matching_obs,
                        )
                    )

            entity_names = {e.name for e in matching_entities}
            matching_relations = [
                r
                for r in self._graph.relations
                if r.from_ in entity_names and r.to in entity_names
            ]

            return KnowledgeGraph(
                entities=matching_entities, relations=matching_relations
            )

    def _matches_criteria(
        self,
        obs: Observation,
        query: str,
        tag_set: set,
        kind_set: set,
        language: str | None,
    ) -> bool:
        if query and query not in (obs.text or "").lower() + (obs.code or "").lower():
            return False
        if tag_set and not tag_set.intersection(set(self._normalize_tags(obs.tags))):
            return False
        if kind_set and obs.kind not in kind_set:
            return False
        # return True if no language filter was provided, or if the observation
        # language matches
        return (not language) or (obs.language or "").lower() == language.lower()

    # Agent-specific methods
    def start_session(
        self,
        feature: str,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, str]:
        with self._lock:
            self.upsert_entity(feature, "Feature", tags, description)
            session_id = str(uuid.uuid4())
            session_name = f"session:{session_id}"
            session_tags = [feature] + (self._normalize_tags(tags) if tags else [])

            self.upsert_entity(session_name, "Session", session_tags, description)
            self.create_relations(
                [Relation(from_=session_name, to=feature, relation_type="implements")]
            )

            return {"session_id": session_id, "session_entity": session_name}

    def log_event(
        self,
        session_id: str,
        kind: ObservationKind = ObservationKind.NOTE,
        text: str | None = None,
        code: str | None = None,
        **kwargs,
    ) -> dict[str, str]:
        with self._lock:
            session_name = f"session:{session_id}"
            obs = Observation(
                kind=kind,
                text=text,
                code=code,
                language=kwargs.get("language", "python"),
                tags=self._normalize_tags(kwargs.get("tags") or []),
                source=kwargs.get("source"),
                metadata=kwargs.get("metadata") or {},
            )
            obs.hash = self._generate_hash(obs)

            self.add_insights([ObservationAdd(entity_name=session_name, contents=[obs])])
            return {"hash": obs.hash}

    def record_error(
        self, feature: str, exception_type: str, message: str, traceback: str, **kwargs
    ) -> dict[str, str]:
        with self._lock:
            # Create error fingerprint
            fingerprint_data = {
                "type": exception_type.strip(),
                "message": message.strip(),
                "feature": feature.strip(),
                "file": (kwargs.get("file") or "").strip(),
            }
            fingerprint = hashlib.sha256(
                json.dumps(fingerprint_data, sort_keys=True).encode()
            ).hexdigest()

            error_name = f"error:{fingerprint[:12]}"
            self.upsert_entity(error_name, "Error", ["python", "error"])
            self.upsert_entity(feature, "Feature")
            self.create_relations(
                [Relation(from_=feature, to=error_name, relation_type="encounters")]
            )

            error_obs = Observation(
                kind=ObservationKind.ERROR,
                text=f"{exception_type}: {message}",
                code=kwargs.get("code"),
                language="python",
                tags=["traceback"],
                source=kwargs.get("file"),
                metadata={"traceback": traceback, "line": kwargs.get("line")},
            )
            self.add_insights(
                [ObservationAdd(entity_name=error_name, contents=[error_obs])]
            )

            return {"error_entity": error_name, "fingerprint": fingerprint}

    def end_session(
        self, session_id: str, success: bool, summary: str | None = None
    ) -> dict[str, str]:
        with self._lock:
            session_name = f"session:{session_id}"
            text = summary or (
                "Session completed successfully"
                if success
                else "Session ended with issues"
            )

            self.add_insights(
                [
                    ObservationAdd(
                        entity_name=session_name,
                        contents=[
                            Observation(
                                kind=ObservationKind.NOTE,
                                text=text,
                                tags=["summary", "session-end"],
                            )
                        ],
                    )
                ]
            )
            return {"session_entity": session_name}

    def record_fix(
        self,
        error_entity: str,
        description: str | None = None,
        code: str | None = None,
        pattern_name: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, str]:
        with self._lock:
            pattern_name = pattern_name or f"fix-pattern-{uuid.uuid4().hex[:8]}"

            self.upsert_entity(
                pattern_name,
                "Pattern",
                ["python", "fix"] + (self._normalize_tags(tags) if tags else []),
                description,
            )

            if code:
                fix_obs = Observation(
                    kind=ObservationKind.SNIPPET,
                    text=description,
                    code=code,
                    language="python",
                    tags=["fix", "solution"]
                    + (self._normalize_tags(tags) if tags else []),
                )
                self.add_insights(
                    [ObservationAdd(entity_name=pattern_name, contents=[fix_obs])]
                )

            self.create_relations(
                [Relation(from_=error_entity, to=pattern_name, relation_type="fixed_by")]
            )

            return {"pattern_entity": pattern_name}

    def export_markdown(self) -> str:
        with self._lock:
            lines = ["# Knowledge Graph\n"]

            for entity in sorted(self._graph.entities, key=lambda x: x.name):
                lines.append(f"## {entity.name}")
                lines.append(f"*Type*: {entity.entity_type}")

                if entity.tags:
                    lines.append(f"*Tags*: {', '.join(sorted(entity.tags))}")

                if entity.description:
                    lines.append(f"\n{entity.description}")

                for obs in entity.observations:
                    lines.append(f"\n### {obs.kind.upper()}")
                    if obs.text:
                        lines.append(obs.text)
                    if obs.code:
                        lang = obs.language or ""
                        lines.append(f"```{lang}")
                        lines.append(obs.code)
                        lines.append("```")

                lines.append("")

            return "\n".join(lines)

    def compact_store(self) -> dict[str, Any]:
        with self._lock:
            # Write snapshot
            self.snapshot_path.write_text(
                self._graph.model_dump_json(), encoding="utf-8"
            )

            # Clear log
            log_size_before = (
                self.log_path.stat().st_size if self.log_path.exists() else 0
            )
            if self.log_path.exists():
                self.log_path.unlink()

            return {
                "entities": len(self._graph.entities),
                "relations": len(self._graph.relations),
                "log_bytes_before": log_size_before,
                "log_bytes_after": 0,
            }
