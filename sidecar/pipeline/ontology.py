"""Ontology loader + auto-maintenance.

The on-disk format is `ontology.yaml` at the project root. We read it,
expose lookup tables, and append entries for newly-seen types (with
`status: seen`) so the author can promote them to `canonical` later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EdgeTypeDef:
    name: str
    status: str = "seen"
    inverse: str | None = None
    symmetric: bool = False
    description: str | None = None
    # Human-readable phrase used by the UI as the section header.
    # Read as: "[this node] [label] [linked node]". Falls back to the
    # snake_case'd type name when missing.
    label: str | None = None


@dataclass
class NodeTypeDef:
    name: str
    status: str = "seen"
    description: str | None = None


ARGUMENTATION_AXES = ("stance", "tradition", "method", "subject")


@dataclass
class Ontology:
    path: Path
    node_types: dict[str, NodeTypeDef] = field(default_factory=dict)
    edge_types: dict[str, EdgeTypeDef] = field(default_factory=dict)
    source_readers: dict[str, Any] = field(default_factory=dict)
    # axis-name → value-name → status ('canonical' | 'seen')
    argumentation_axes: dict[str, dict[str, str]] = field(default_factory=dict)
    _dirty: bool = False
    _new_node_types: list[str] = field(default_factory=list)
    _new_edge_types: list[str] = field(default_factory=list)
    _new_axis_values: dict[str, list[str]] = field(default_factory=dict)

    def see_node_type(self, name: str) -> bool:
        """Register a node type if unknown. Returns True if it was new."""
        if name in self.node_types:
            return False
        self.node_types[name] = NodeTypeDef(name=name, status="seen")
        self._dirty = True
        self._new_node_types.append(name)
        return True

    def see_edge_type(self, name: str) -> bool:
        if name in self.edge_types:
            return False
        self.edge_types[name] = EdgeTypeDef(name=name, status="seen")
        self._dirty = True
        self._new_edge_types.append(name)
        return True

    def see_axis_value(self, axis: str, value: str) -> bool:
        if axis not in ARGUMENTATION_AXES:
            raise ValueError(f"unknown argumentation axis '{axis}'")
        bucket = self.argumentation_axes.setdefault(axis, {})
        if value in bucket:
            return False
        bucket[value] = "seen"
        self._dirty = True
        self._new_axis_values.setdefault(axis, []).append(value)
        return True

    def inverse_of(self, edge_type: str) -> str | None:
        """Return the inverse edge type, or the same type if symmetric, or None."""
        defn = self.edge_types.get(edge_type)
        if defn is None:
            return None
        if defn.symmetric:
            return edge_type
        return defn.inverse

    def save_if_dirty(self) -> bool:
        if not self._dirty:
            return False
        existing = yaml.safe_load(self.path.read_text())
        existing.setdefault("node_types", [])
        existing.setdefault("edge_types", [])
        existing.setdefault("argumentation_axes", {})
        for name in self._new_node_types:
            existing["node_types"].append({"name": name, "status": "seen"})
        for name in self._new_edge_types:
            existing["edge_types"].append({"name": name, "status": "seen"})
        for axis, values in self._new_axis_values.items():
            axis_bucket = existing["argumentation_axes"].setdefault(axis, [])
            for v in values:
                axis_bucket.append({"name": v, "status": "seen"})
        self.path.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=True))
        self._dirty = False
        self._new_node_types.clear()
        self._new_edge_types.clear()
        self._new_axis_values.clear()
        return True


def load_ontology(path: Path) -> Ontology:
    raw = yaml.safe_load(path.read_text())
    onto = Ontology(path=path)
    for entry in raw.get("node_types") or []:
        onto.node_types[entry["name"]] = NodeTypeDef(
            name=entry["name"],
            status=entry.get("status", "seen"),
            description=entry.get("description"),
        )
    for entry in raw.get("edge_types") or []:
        onto.edge_types[entry["name"]] = EdgeTypeDef(
            name=entry["name"],
            status=entry.get("status", "seen"),
            inverse=entry.get("inverse"),
            symmetric=bool(entry.get("symmetric", False)),
            description=entry.get("description"),
            label=entry.get("label"),
        )
    onto.source_readers = raw.get("source_readers") or {}
    for axis, entries in (raw.get("argumentation_axes") or {}).items():
        bucket = onto.argumentation_axes.setdefault(axis, {})
        for entry in entries or []:
            bucket[entry["name"]] = entry.get("status", "seen")
    return onto
