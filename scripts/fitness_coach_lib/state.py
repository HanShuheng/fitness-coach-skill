from __future__ import annotations

import json
from typing import Any

from .profile import profile_status
from .scheduler import notify_target_status
from .settings import CONFIG_FILE, DATA_SCHEMA_VERSION, RUNTIME_DIR, SKILL_VERSION, UPDATE_STATE_FILE, runtime_context
from .storage import read_json


def initialization_state() -> dict[str, Any]:
    config_exists = CONFIG_FILE.exists()
    config = read_json(CONFIG_FILE, {}) if config_exists else {}
    profile = profile_status()
    notify = notify_target_status()
    missing: list[str] = []

    if not RUNTIME_DIR.exists():
        missing.append("data_directory")
    if not config_exists:
        missing.append("config_file")
    if not profile.get("initialized"):
        missing.append("profile")
    if config.get("schema_version", DATA_SCHEMA_VERSION) != DATA_SCHEMA_VERSION:
        missing.append("schema_migration")

    if "schema_migration" in missing:
        state = "migration_required"
    elif "profile" in missing:
        state = "profile_required"
    elif "config_file" in missing:
        state = "config_required"
    elif missing:
        state = "uninitialized"
    else:
        state = "ready"

    return {
        "state": state,
        "ready": state == "ready",
        "missing": missing,
        "next_step": next_step_for(state),
        "reason": reason_for(state),
        "progress_saved": RUNTIME_DIR.exists(),
        "skill_version": SKILL_VERSION,
        "data_schema_version": DATA_SCHEMA_VERSION,
        "runtime_context": runtime_context(),
        "config_file": str(CONFIG_FILE),
        "profile": profile,
        "notify_target": notify,
        "update_state": read_json(UPDATE_STATE_FILE, {}),
    }


def next_step_for(state: str) -> str:
    if state == "profile_required":
        return "python scripts/fitness_coach.py profile init"
    if state == "config_required":
        return "python scripts/fitness_coach.py init"
    if state == "migration_required":
        return "python scripts/fitness_coach.py migrate --dry-run"
    if state == "ready":
        return "可以使用 record、build-context、daily-check 等业务命令。"
    return "python scripts/fitness_coach.py init"


def reason_for(state: str) -> str:
    messages = {
        "uninitialized": "当前 skill 尚未完成初始化。",
        "profile_required": "基础档案缺失或核心字段不足，暂不能生成长期个性化建议。",
        "config_required": "配置文件缺失，需要先生成默认配置。",
        "migration_required": "检测到数据 schema 不兼容，需要先迁移。",
        "ready": "初始化已完成。",
    }
    return messages.get(state, "当前状态需要人工检查。")


def status() -> int:
    print(json.dumps(initialization_state(), ensure_ascii=False, indent=2))
    return 0
