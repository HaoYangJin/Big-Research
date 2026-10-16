"""Pure release timing rules. PDT is intentionally a fixed UTC-07:00 offset."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta


def parse(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError("Release timestamps must include an offset")
    return result.astimezone(UTC)


def advance(state: dict, reason: str) -> dict:
    result = deepcopy(state)
    previous = result["target"]
    result["target"] = (parse(previous) + timedelta(days=1)).isoformat()
    result["deferrals"] = result.get("deferrals", 0) + 1
    result.setdefault("history", []).append({"from": previous, "to": result["target"], "reason": reason})
    return result


def release_action(state: dict, current: datetime, ready: bool, ready_at: str | None) -> str:
    if state.get("published"):
        return "published"
    target = parse(state["target"])
    if current < target:
        return "wait"
    if not ready or not ready_at or parse(ready_at) >= target:
        return "defer"
    # A delayed runner can publish only in this midnight's bounded delivery window.
    if current - target > timedelta(minutes=10):
        return "defer"
    return "publish"
