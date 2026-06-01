from __future__ import annotations

import json
from datetime import date
from typing import Any

from .settings import DAILY_DIR, DATA_SCHEMA_VERSION, today_local, now_local, ensure_dirs
from .storage import atomic_write_text, deep_merge, extract_latest_payload, format_frontmatter


def daily_file(day: date | None = None) -> Any:
    day = day or today_local()
    return DAILY_DIR / f"{day.isoformat()}.md"


def load_daily_payload(day: date | None = None) -> dict[str, Any]:
    path = daily_file(day)
    try:
        return extract_latest_payload(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def render_daily(day: date, payload: dict[str, Any], raw_entries: list[str]) -> str:
    now = now_local().isoformat()
    meta = {
        "schema_version": DATA_SCHEMA_VERSION,
        "initialized": True,
        "created_at": now,
        "updated_at": now,
        "record_id": f"daily-{day.isoformat()}",
        "source": "fitness-coach-skill",
    }
    lines = [
        f"# 每日健身饮食记录 {day.isoformat()}",
        "",
        "## 结构化数据",
        "",
        "```json payload",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 原始记录",
        "",
    ]
    lines.extend(raw_entries or ["- 暂无"])
    lines.append("")
    return format_frontmatter(meta) + "\n".join(lines)


def parse_raw_entries(text: str) -> list[str]:
    marker = "## 原始记录"
    idx = text.find(marker)
    if idx == -1:
        return []
    entries = []
    for line in text[idx + len(marker) :].splitlines():
        if line.strip().startswith("- "):
            entries.append(line.rstrip())
    return [line for line in entries if line.strip() != "- 暂无"]


def record(payload_json: str | None, raw_text: str | None, day: str | None = None) -> int:
    ensure_dirs()
    target_day = date.fromisoformat(day) if day else today_local()
    path = daily_file(target_day)
    current = load_daily_payload(target_day)
    raw_entries: list[str] = []
    if path.exists():
        raw_entries = parse_raw_entries(path.read_text(encoding="utf-8"))
    incoming: dict[str, Any] = {}
    if payload_json:
        parsed = json.loads(payload_json)
        if not isinstance(parsed, dict):
            raise ValueError("--payload-json must be a JSON object")
        incoming = parsed
    merged = deep_merge(current, incoming)
    if raw_text:
        raw_entries.append(f"- {now_local().isoformat()} {raw_text.strip()}")
    atomic_write_text(path, render_daily(target_day, merged, raw_entries))
    print(f"OK daily record saved: {path}")
    return 0


def rebuild_index() -> int:
    from .settings import INDEX_FILE
    from .storage import atomic_write_json

    ensure_dirs()
    days = []
    for path in sorted(DAILY_DIR.glob("*.md")):
        payload = extract_latest_payload(path.read_text(encoding="utf-8"))
        days.append({"date": path.stem, "path": str(path), "payload": payload})
    atomic_write_json(INDEX_FILE, {"version": 1, "days": days, "updated_at": now_local().isoformat()})
    print(f"OK rebuilt index: {INDEX_FILE}")
    return 0


def has_field(payload: dict[str, Any], dotted: str) -> bool:
    cur: Any = payload
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return cur not in (None, "", [], {}, "unknown")


def missing_daily_fields(required: list[str]) -> list[str]:
    payload = load_daily_payload()
    return [field for field in required if not has_field(payload, field)]
