"""Python ML sidecar — FastAPI on granian.

Owns:
  - Embedding model (held in memory)
  - Semantic search endpoint (encode query → vector search → ranked slugs)
  - Health check

SvelteKit proxies semantic queries here via localhost HTTP.
"""

from __future__ import annotations

import struct
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pipeline import paths
from pipeline.db import open_db
from . import embed


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)


class SearchHit(BaseModel):
    slug: str
    distance: float


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Eager-load the encoder so the first request isn't slow.
    embed.get_model()
    yield


app = FastAPI(
    title="Bible Semantic Graph — ML sidecar",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow any origin in dev. The sidecar listens on the host's network
# interface for Tailscale access; the threat model is "anything that can
# reach this port is already authorized via Tailscale ACLs". Tighten via
# CORS_ORIGINS env var (comma-separated) in production.
_cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "model": paths.EMBEDDING_MODEL}


@app.post("/search/semantic", response_model=SearchResponse)
def search_semantic(req: SearchRequest) -> SearchResponse:
    if not paths.DB_PATH.exists():
        raise HTTPException(status_code=503, detail="index not built yet — run `bun run ingest`")
    vec = embed.encode(req.query)
    packed = struct.pack(f"{paths.EMBEDDING_DIM}f", *vec)
    conn = open_db(paths.DB_PATH)
    rows = list(
        conn.execute(
            """
            SELECT slug, distance
            FROM nodes_vec
            WHERE embedding MATCH ? AND k = ?
            ORDER BY distance
            """,
            (packed, req.limit),
        )
    )
    return SearchResponse(
        query=req.query,
        hits=[SearchHit(slug=row[0], distance=float(row[1])) for row in rows],
    )


def run() -> None:
    """Entry point for `uv run serve` (production-like local run)."""
    import granian
    from granian.constants import Interfaces

    server = granian.Granian(
        target="api.main:app",
        address="0.0.0.0",
        port=7655,
        interface=Interfaces.ASGI,
    )
    server.serve()
