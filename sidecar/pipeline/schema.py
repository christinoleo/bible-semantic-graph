"""Pydantic models for frontmatter validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Argumentation(BaseModel):
    """Structured classification for argumentative Nodes (Arguments, Theories,
    Concepts that ARE arguments, Events that crystallize a dispute).

    Each axis is an open list — values are validated against `ontology.yaml`
    and auto-registered as `status: seen` when new.
    """

    model_config = ConfigDict(extra="forbid")

    stance: list[str] = Field(default_factory=list)       # against-christianity, for-islam, ...
    tradition: list[str] = Field(default_factory=list)    # islamic-apologetic, reformed, ...
    method: list[str] = Field(default_factory=list)       # textual-critique, philosophical, ...
    subject: list[str] = Field(default_factory=list)      # christology, theodicy, ...


class EdgeDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    target: str  # a slug; existence is checked separately by the ingestor
    note: str | None = None
    # primary=True marks the "main deepening line" out of this Node — UI
    # highlights it as the recommended next step when reading hierarchically.
    primary: bool = False


class Frontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    name: str
    also: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    edges: list[EdgeDecl] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    # For Text Nodes (Bible books, deuterocanonicals, pseudepigrapha, etc.):
    # which canonical traditions include this book. Empty / omitted for
    # non-Text Nodes or for texts that are universally non-canonical.
    # Allowed values: tanakh, protestant, catholic, orthodox-eastern,
    # orthodox-ethiopian. See ADR 0006.
    canon: list[str] = Field(default_factory=list)
    # For "relational" Nodes (an Argument, Event, Theory, etc. that exists in
    # virtue of its relata): the slugs of the entities the Node is between.
    # Materialized by the pipeline as `concerns` edges. Allows the UI to
    # render "Between X and Y" prominently. Empty / omitted = substantial Node.
    concerns: list[str] = Field(default_factory=list)
    # Structured classification for argumentative Nodes. Four axes:
    # stance (for/against), tradition (intellectual lineage), method
    # (how it argues), subject (what it's about). Values validated against
    # `argumentation_axes` section of ontology.yaml.
    argumentation: Argumentation | None = None

    @model_validator(mode="after")
    def _argument_must_be_classified(self) -> "Frontmatter":
        """Every `type: Argument` Node MUST declare argumentation with all
        four axes non-empty. This is what makes the classification trustworthy
        for downstream analysis (stance distribution, refutation patterns by
        tradition, method-vs-subject heat-maps, etc.)."""
        if self.type != "Argument":
            return self
        if self.argumentation is None:
            raise ValueError(
                "type: Argument requires an `argumentation:` block declaring "
                "stance, tradition, method, and subject"
            )
        missing = [
            axis
            for axis in ("stance", "tradition", "method", "subject")
            if not getattr(self.argumentation, axis)
        ]
        if missing:
            raise ValueError(
                f"Argument Node is missing required axes: {', '.join(missing)}. "
                f"Every Argument must declare at least one value per axis."
            )
        return self


class NodeRecord(BaseModel):
    """A fully ingested Node, ready to be written to SQLite."""

    slug: str
    type: str
    also: list[str]
    name: str
    aliases: list[str]
    tags: list[str]
    sources: list[str]
    canon: list[str]
    argumentation: Argumentation | None
    body_md: str
    body_html: str
    file_path: str


class EdgeRecord(BaseModel):
    source: str
    type: str
    target: str
    note: str | None = None
    primary: bool = False
    origin: Literal["frontmatter", "wikilink", "inferred"]
