from __future__ import annotations

import json

from .daily import missing_daily_fields
from .profile import profile_status
from .scheduler import notify_target_status
from .settings import CONFIG_FILE, RUNTIME_DIR, SKILL_VERSION, UPDATE_STATE_FILE, runtime_context
from .state import initialization_state
from .storage import load_config, read_json


def info() -> int:
    config = load_config()
    required = [str(item) for item in config.get("required_daily_fields", [])]
    data = {
        "skill_version": SKILL_VERSION,
        "runtime_dir": str(RUNTIME_DIR),
        "runtime_context": runtime_context(),
        "initialization": initialization_state(),
        "config_file": str(CONFIG_FILE),
        "profile": profile_status(),
        "missing_daily_fields": missing_daily_fields(required),
        "notify_target": notify_target_status(),
        "update_state": read_json(UPDATE_STATE_FILE, {}),
        "skipped_versions": config.get("skipped_versions", []),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0
