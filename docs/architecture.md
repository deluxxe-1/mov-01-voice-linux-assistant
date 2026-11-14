# Architecture — ARIA Voice Linux Assistant

## Goals

1. **Offline-first**: the default path never sends audio or text off-device.
2. **Testable core**: intent resolution is deterministic and covered by unit tests.
3. **Replaceable adapters**: STT, TTS, and LLM are stubs behind narrow interfaces so real engines
   can be dropped in without touching the API layer.

## Components

```
Flutter app (mobile/lib/main.dart)
        │  HTTP (JSON)
        ▼
FastAPI backend (backend/src/aria_backend/main.py)
        │
        ├─ intent.resolve(transcript)        → Action + slots + confidence
        ├─ STT adapter  (stub: accepts text)  → transcript
        ├─ LLM adapter  (stub: canned reply)  → natural-language answer
        ├─ TTS adapter  (stub: metadata)      → audio descriptor
        └─ SQLite history (ARIA_DB_PATH)
```

### Intent layer

`intent.py` compiles a small, ordered list of regular expressions into an `Action` enum. It is the
first stage in the pipeline because it answers the most common commands (time, timers, app launch,
system status) deterministically and instantly, without loading a model.

### Adapters

Each adapter (STT/TTS/LLM) is intentionally a stub in this scaffold. The signatures and response
shapes mirror the real engines (faster-whisper, piper/espeak-ng, Ollama) so the contract is stable.

## Request lifecycle

1. App captures a transcript and `POST`s it to `/api/assistant/query`.
2. Backend runs the intent router.
3. If matched, the backend executes the stub action and returns a reply.
4. If not matched, the backend asks the (stubbed) LLM for a reply.
5. The app optionally calls `/api/assistant/tts` to obtain playback metadata.

## Offline-first approach

- All endpoints work with no internet access; stubs never call the network.
- `ARIA_OLLAMA_URL` points to a loopback address by default.
- `ARIA_ALLOW_REMOTE=false` guarantees the API rejects non-loopback clients unless explicitly enabled.

## Failure modes

| Failure                  | Behaviour                                             |
| ------------------------ | ----------------------------------------------------- |
| Empty transcript         | HTTP 422 (Pydantic validation).                       |
| Unknown phrase           | `action: "unknown"` with LLM fallback reply.          |
| Remote client (default)  | HTTP 403 from the security guard.                     |
| STT/TTS engine offline   | Stub response — the pipeline degrades gracefully.     |

## Performance notes

- Intent matching is regex-based and O(patterns); sub-millisecond on typical hardware.
- Model calls are a fallback only, keeping the p95 latency of common commands very low.
