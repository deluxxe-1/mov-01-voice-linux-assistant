"""ARIA FastAPI application.

Exposes a liveness probe and two assistant endpoints. STT/TTS/LLM are stubbed
so the service runs fully offline; see ``docs/architecture.md``.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field

from .intent import Action, Intent, default_reply, resolve

app = FastAPI(title="ARIA Voice Assistant API", version="0.1.0")


class QueryRequest(BaseModel):
    """Incoming transcript from the mobile app."""

    transcript: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", max_length=8)


class QueryResponse(BaseModel):
    """Resolved intent and the assistant reply."""

    action: Action
    reply: str
    slots: dict[str, str] = Field(default_factory=dict)
    confidence: float


class TTSRequest(BaseModel):
    """Text to synthesise into speech metadata."""

    text: str = Field(min_length=1, max_length=2000)
    voice: str = Field(default="default", max_length=64)


class TTSResponse(BaseModel):
    """Placeholder audio descriptor returned by the stub TTS adapter."""

    audio_url: str
    format: str
    duration_ms: int
    voice: str


def allow_remote() -> bool:
    """Whether non-loopback clients are allowed (see ``ARIA_ALLOW_REMOTE``)."""

    return os.getenv("ARIA_ALLOW_REMOTE", "false").strip().lower() in {"1", "true", "yes"}


def client_guard(request: Request) -> None:
    """Reject non-loopback clients unless explicitly enabled.

    ``ARIA_ALLOW_REMOTE=false`` (the default) keeps the assistant private to the
    host it runs on.
    """

    if allow_remote():
        return
    client = request.client.host if request.client else "unknown"
    if client not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Remote access is disabled (set ARIA_ALLOW_REMOTE=true to enable).",
        )


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker and CI."""

    return {"status": "ok", "service": "aria-backend", "version": app.version}


@app.post(
    "/api/assistant/query",
    response_model=QueryResponse,
    dependencies=[Depends(client_guard)],
)
def query(payload: QueryRequest) -> QueryResponse:
    """Resolve a transcript to an intent and a stubbed assistant reply."""

    intent: Intent = resolve(payload.transcript)
    return QueryResponse(
        action=intent.action,
        reply=default_reply(intent),
        slots=intent.slots,
        confidence=intent.confidence,
    )


@app.post(
    "/api/assistant/tts",
    response_model=TTSResponse,
    dependencies=[Depends(client_guard)],
)
def tts(payload: TTSRequest) -> TTSResponse:
    """Return placeholder speech-audio metadata (no real synthesis)."""

    words = max(len(payload.text.split()), 1)
    return TTSResponse(
        audio_url="/static/stub/tts-placeholder.wav",
        format="wav",
        duration_ms=words * 400,
        voice=payload.voice,
    )
