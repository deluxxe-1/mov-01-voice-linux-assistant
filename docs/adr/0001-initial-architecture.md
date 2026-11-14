# ADR 0001 — Initial architecture for ARIA

- **Status**: Accepted
- **Date**: 2026-11-14
- **Deciders**: ARIA maintainers

## Context

We want a voice assistant for Linux desktop/server that respects privacy and works offline. The
project must be a portfolio-quality scaffold: runnable backend, tested core logic, and a mobile
companion app with a real screen.

## Decision

1. **Python + FastAPI** for the backend. It is fast to build, has first-class typing via Pydantic v2,
   and is trivial to containerise and test.
2. **A deterministic intent router** (`intent.py`) as the first pipeline stage, with the LLM only as a
   fallback. This keeps the common path instant and unit-testable.
3. **Stub adapters for STT/TTS/LLM** with real-world-shaped interfaces, so the scaffold runs offline
   and the real engines can be integrated later without API churn.
4. **Flutter** for the companion app: a single, cross-platform codebase with a native mic experience.
5. **Security by default**: configuration through environment variables, loopback-only clients unless
   `ARIA_ALLOW_REMOTE=true`.

## Consequences

- Positive: fully offline, fast, testable, and easy to extend.
- Negative: stub responses are not real transcriptions/synthesis/answers; real engines add heavy
  native dependencies to be managed later.
- Neutral: SQLite is used for history but is not yet wired into endpoints in this scaffold.

## Alternatives considered

- **Node/Express backend**: rejected — Python has the strongest local ML/STT ecosystem (Whisper, Ollama).
- **Cloud STT (e.g., hosted APIs)**: rejected — violates the offline-first / privacy goal.
- **LLM-only intent handling**: rejected — non-deterministic, slower, and harder to test.
