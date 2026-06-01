from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

from .archive import backup
from .settings import DEFAULT_UPDATE_CHECK_URL, SKILL_VERSION, UPDATE_STATE_FILE, now_local
from .storage import atomic_write_json, load_config, read_json


def parse_version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value)[:4] or [0])


def read_remote_version(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:
        text = response.read().decode("utf-8")
    match = re.search(r"version:\s*([0-9][0-9A-Za-z.\-]*)", text)
    if not match:
        raise RuntimeError("remote version not found")
    return match.group(1)


def load_update_state() -> dict[str, Any]:
    data = read_json(UPDATE_STATE_FILE, {})
    return data if isinstance(data, dict) else {}


def save_update_state(data: dict[str, Any]) -> None:
    atomic_write_json(UPDATE_STATE_FILE, data)


def version() -> int:
    print(f"fitness-coach-skill {SKILL_VERSION}")
    return 0


def check_update(remote_url: str | None = None) -> int:
    url = remote_url or load_config().get("version_check_url") or DEFAULT_UPDATE_CHECK_URL
    state = load_update_state()
    skipped = set(load_config().get("skipped_versions", [])) | set(state.get("skipped_versions", []))
    try:
        remote = read_remote_version(str(url))
    except Exception as exc:
        print(f"ERROR check update failed: {exc}")
        return 1
    has_update = parse_version_tuple(remote) > parse_version_tuple(SKILL_VERSION)
    skipped_remote = remote in skipped
    state.update({
        "current_version": SKILL_VERSION,
        "remote_version": remote,
        "last_checked_at": now_local().isoformat(),
        "has_update": has_update,
        "skipped": skipped_remote,
    })
    save_update_state(state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    if has_update and not skipped_remote:
        print("发现新版本。更新前请先运行 prepare-update；如果不更新，可运行 skip-version。")
    return 0


def skip_version(version_value: str, clear: bool = False) -> int:
    config = load_config()
    versions = list(config.get("skipped_versions", []))
    if clear:
        versions = [item for item in versions if item != version_value]
        print(f"OK cleared skipped version: {version_value}")
    elif version_value not in versions:
        versions.append(version_value)
        print(f"OK skipped version: {version_value}")
    config["skipped_versions"] = versions
    from .storage import save_config

    save_config(config)
    state = load_update_state()
    state["skipped_versions"] = versions
    save_update_state(state)
    return 0


def prepare_update(target_version: str) -> int:
    path = backup(f"pre-update-{target_version}")
    print(f"OK pre-update backup created: {path}")
    return 0


def post_update_check() -> int:
    from .profile import profile_status
    from .scheduler import notify_target_status

    print(f"skill_version: {SKILL_VERSION}")
    print(f"profile: {json.dumps(profile_status(), ensure_ascii=False)}")
    print(f"notify_target: {notify_target_status()}")
    return 0
