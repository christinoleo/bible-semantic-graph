"""Project paths — single source of truth for filesystem layout."""

from __future__ import annotations

from pathlib import Path

# sidecar/pipeline/paths.py → project root is two levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTENT_DIR = PROJECT_ROOT / "content"
ONTOLOGY_PATH = PROJECT_ROOT / "ontology.yaml"
DB_DIR = PROJECT_ROOT / ".db"
DB_PATH = DB_DIR / "index.sqlite"

# The embedding model used at ingestion AND at query time. Must match.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Compute device. Override via EMBEDDING_DEVICE env var (e.g., "cuda", "cpu", "mps").
# Default "auto" → cuda if available, else cpu. Resolved lazily on first access
# so importing `paths` for filesystem constants doesn't pay the ~1.7s torch +
# CUDA driver probe.
import os as _os

_cached_device: str | None = None


def _resolve_device() -> str:
    global _cached_device
    if _cached_device is not None:
        return _cached_device
    requested = _os.environ.get("EMBEDDING_DEVICE", "auto")
    if requested != "auto":
        _cached_device = requested
        return _cached_device
    import torch

    _cached_device = "cuda" if torch.cuda.is_available() else "cpu"
    return _cached_device


def __getattr__(name: str) -> str:
    if name == "EMBEDDING_DEVICE":
        return _resolve_device()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
