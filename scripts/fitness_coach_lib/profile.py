from __future__ import annotations

import json
from typing import Any

from .settings import DATA_SCHEMA_VERSION, PROFILE_FILE, ensure_dirs, now_local
from .storage import atomic_write_text, deep_merge, extract_latest_payload, format_frontmatter, parse_frontmatter


CORE_FIELDS = [
    "goals.primary",
    "identity.sex",
    "identity.age_or_birth_year",
    "body.height_cm",
    "body.current_weight_kg",
    "training.experience",
    "training.available_days_per_week",
    "nutrition.allergies",
    "health.injuries_or_limitations",
]


def empty_profile_payload() -> dict[str, Any]:
    return {
        "identity": {
            "nickname": "unknown",
            "age_or_birth_year": "unknown",
            "sex": "unknown",
        },
        "body": {
            "height_cm": "unknown",
            "current_weight_kg": "unknown",
            "start_weight_kg": "unknown",
            "target_weight_kg": "unknown",
        },
        "goals": {
            "primary": "unknown",
            "deadline": "unknown",
            "priority": "unknown",
            "acceptable_rate": "unknown",
        },
        "training": {
            "experience": "unknown",
            "level": "unknown",
            "available_days_per_week": "unknown",
            "session_minutes": "unknown",
            "equipment": "unknown",
            "current_program": "unknown",
            "preferences": "unknown",
        },
        "nutrition": {
            "goal": "unknown",
            "allergies": "unknown",
            "restrictions": "unknown",
            "dislikes": "unknown",
            "favorite_foods": "unknown",
            "cooking_skill": "unknown",
            "budget": "unknown",
            "eating_out_frequency": "unknown",
        },
        "lifestyle": {
            "sleep": "unknown",
            "activity": "unknown",
            "stress": "unknown",
            "high_risk_periods": "unknown",
        },
        "health": {
            "conditions": "unknown",
            "medications": "unknown",
            "injuries_or_limitations": "unknown",
            "medical_constraints": "unknown",
        },
        "coach_notes": [],
        "custom": {},
    }


def nested_get(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def missing_core_fields(payload: dict[str, Any]) -> list[str]:
    missing = []
    for field in CORE_FIELDS:
        value = nested_get(payload, field)
        if value in (None, "", [], {}, "unknown"):
            missing.append(field)
    return missing


def render_profile(payload: dict[str, Any], initialized: bool, raw_text: str = "") -> str:
    now = now_local().isoformat()
    meta = {
        "schema_version": DATA_SCHEMA_VERSION,
        "initialized": initialized,
        "created_at": now,
        "updated_at": now,
        "record_id": "profile",
        "source": "fitness-coach-skill",
    }
    body = [
        "# 用户基础信息档案",
        "",
        "此文件是长期健身饮食建议的基础上下文。未知或用户拒答的字段保留为 `unknown`。",
        "",
        "## 结构化数据",
        "",
        "```json payload",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    if raw_text:
        body += ["## 原始补充", "", raw_text.strip(), ""]
    return format_frontmatter(meta) + "\n".join(body)


def load_profile() -> tuple[dict[str, Any], dict[str, Any], str]:
    try:
        text = PROFILE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}, {}, ""
    meta, _ = parse_frontmatter(text)
    return meta, extract_latest_payload(text), text


def profile_status() -> dict[str, Any]:
    meta, payload, _ = load_profile()
    initialized = bool(meta.get("initialized", False))
    if not payload:
        payload = empty_profile_payload()
    missing = missing_core_fields(payload)
    return {
        "exists": PROFILE_FILE.exists(),
        "initialized": initialized and not missing,
        "missing_core_fields": missing,
        "path": str(PROFILE_FILE),
    }


def init_profile() -> int:
    ensure_dirs()
    if PROFILE_FILE.exists():
        print(f"INFO profile already exists: {PROFILE_FILE}")
        return 0
    payload = empty_profile_payload()
    atomic_write_text(PROFILE_FILE, render_profile(payload, False))
    print(f"OK created profile: {PROFILE_FILE}")
    return 0


def update_profile(payload_json: str | None, raw_text: str | None) -> int:
    ensure_dirs()
    current = empty_profile_payload()
    _, existing, _ = load_profile()
    if existing:
        current = deep_merge(current, existing)
    incoming: dict[str, Any] = {}
    if payload_json:
        parsed = json.loads(payload_json)
        if not isinstance(parsed, dict):
            raise ValueError("--payload-json must be a JSON object")
        incoming = parsed
    merged = deep_merge(current, incoming)
    missing = missing_core_fields(merged)
    initialized = not missing
    atomic_write_text(PROFILE_FILE, render_profile(merged, initialized, raw_text or ""))
    print("OK profile updated")
    print(f"initialized: {str(initialized).lower()}")
    if missing:
        print("missing_core_fields:")
        for item in missing:
            print(f"- {item}")
    return 0


def show_profile() -> int:
    status = profile_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    _, payload, _ = load_profile()
    if payload:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
