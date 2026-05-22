"""Embedding model held in a module-level singleton.

Loaded lazily on first use so app startup isn't blocked while
sentence-transformers downloads weights on first run.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from pipeline import paths

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

_model: "SentenceTransformer | None" = None
_lock = threading.Lock()


def get_model() -> "SentenceTransformer":
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(paths.EMBEDDING_MODEL, device=paths.EMBEDDING_DEVICE)
    return _model


def encode(text: str) -> list[float]:
    model = get_model()
    vec = model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0]
    return vec.tolist()
