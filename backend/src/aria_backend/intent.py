"""Deterministic intent routing for the ARIA voice assistant.

This module maps a natural-language transcript to a structured :class:`Intent`.
It is intentionally offline and model-free so it can be unit tested quickly and
used as the first, fast stage of the assistant pipeline.

Real speech-to-text / LLM integration is out of scope here and lives behind
adapters documented in ``docs/architecture.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum


class Action(StrEnum):
    """Actions the assistant knows how to perform."""

    GET_TIME = "get_time"
    SET_TIMER = "set_timer"
    OPEN_APP = "open_app"
    SYSTEM_STATUS = "system_status"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Intent:
    """A resolved intent: an action plus extracted slots and confidence."""

    action: Action
    slots: dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0


# Ordered patterns: the first match wins. Order matters, so more specific
# patterns are placed before generic ones.
_RULES: list[tuple[re.Pattern[str], Action]] = [
    (re.compile(r"\b(what|tell me|which).{0,20}\btime\b", re.IGNORECASE), Action.GET_TIME),
    (re.compile(r"\btime is it\b", re.IGNORECASE), Action.GET_TIME),
    (re.compile(r"\b(set|start|create).{0,20}\btimer\b", re.IGNORECASE), Action.SET_TIMER),
    (re.compile(r"\b(open|launch|start|run)\s+(?P<app>[\w.\-]+)", re.IGNORECASE), Action.OPEN_APP),
    (
        re.compile(r"\b(status|cpu|memory|ram|uptime|load|disk)\b", re.IGNORECASE),
        Action.SYSTEM_STATUS,
    ),
]

_DURATION_RE = re.compile(
    r"(?P<value>\d+)\s*(?P<unit>seconds?|secs?|minutes?|mins?|hours?|hrs?)\b",
    re.IGNORECASE,
)

_UNIT_ALIASES = {
    "second": "seconds",
    "sec": "seconds",
    "secs": "seconds",
    "minute": "minutes",
    "min": "minutes",
    "mins": "minutes",
    "hour": "hours",
    "hr": "hours",
    "hrs": "hours",
}


def _normalize_unit(unit: str) -> str:
    unit = unit.lower()
    return _UNIT_ALIASES.get(unit, unit)


def resolve(transcript: str) -> Intent:
    """Resolve ``transcript`` into an :class:`Intent`.

    The function never raises for normal input; unmatched phrases return
    :attr:`Action.UNKNOWN` with zero confidence.
    """

    text = (transcript or "").strip()
    if not text:
        return Intent(action=Action.UNKNOWN, confidence=0.0)

    for pattern, action in _RULES:
        match = pattern.search(text)
        if not match:
            continue

        slots: dict[str, str] = {}
        if action is Action.SET_TIMER:
            duration = _DURATION_RE.search(text)
            if duration:
                slots["value"] = duration.group("value")
                slots["unit"] = _normalize_unit(duration.group("unit"))
        elif action is Action.OPEN_APP:
            app = match.groupdict().get("app")
            if app:
                slots["app"] = app.strip()

        return Intent(action=action, slots=slots, confidence=0.9)

    return Intent(action=Action.UNKNOWN, confidence=0.0)


def default_reply(intent: Intent) -> str:
    """Return a short, deterministic reply for a resolved intent."""

    if intent.action is Action.GET_TIME:
        return "Current system time is available on the host clock."  # pragma: no cover - stub
    if intent.action is Action.SET_TIMER:
        value = intent.slots.get("value", "?")
        unit = intent.slots.get("unit", "seconds")
        return f"Timer set for {value} {unit}."
    if intent.action is Action.OPEN_APP:
        app = intent.slots.get("app", "the application")
        return f"Opening {app}."
    if intent.action is Action.SYSTEM_STATUS:
        return "System status: CPU, memory and load collected from local probes."
    return "I did not understand that yet; routing to the local language model."
