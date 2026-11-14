"""Tests for the ARIA intent router."""

from aria_backend.intent import Action, resolve


def test_resolve_time_question():
    intent = resolve("What time is it?")
    assert intent.action is Action.GET_TIME
    assert intent.confidence > 0


def test_resolve_timer_extracts_slots():
    intent = resolve("set a timer for 5 minutes")
    assert intent.action is Action.SET_TIMER
    assert intent.slots == {"value": "5", "unit": "minutes"}


def test_resolve_open_app_slot():
    intent = resolve("please open firefox")
    assert intent.action is Action.OPEN_APP
    assert intent.slots.get("app") == "firefox"


def test_resolve_system_status():
    intent = resolve("show me the cpu and memory status")
    assert intent.action is Action.SYSTEM_STATUS


def test_resolve_unknown_phrase():
    intent = resolve("tell me a joke about penguins")
    assert intent.action is Action.UNKNOWN
    assert intent.confidence == 0.0


def test_resolve_empty_transcript():
    intent = resolve("   ")
    assert intent.action is Action.UNKNOWN
