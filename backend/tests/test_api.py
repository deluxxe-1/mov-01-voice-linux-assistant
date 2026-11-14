"""Tests for the ARIA HTTP API surface."""

from fastapi.testclient import TestClient

from aria_backend.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "aria-backend"


def test_query_returns_intent_and_reply():
    response = client.post("/api/assistant/query", json={"transcript": "set a timer for 2 minutes"})
    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "set_timer"
    assert "2 minutes" in body["reply"]
    assert body["confidence"] > 0


def test_query_rejects_empty_transcript():
    response = client.post("/api/assistant/query", json={"transcript": ""})
    assert response.status_code == 422


def test_tts_returns_placeholder_metadata():
    response = client.post("/api/assistant/tts", json={"text": "hello there friend"})
    assert response.status_code == 200
    body = response.json()
    assert body["format"] == "wav"
    assert body["duration_ms"] == 3 * 400
