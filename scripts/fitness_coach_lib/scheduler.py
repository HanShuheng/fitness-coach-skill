from __future__ import annotations

import shlex
import subprocess
import sys
from datetime import datetime
from typing import Any

from .daily import missing_daily_fields
from .settings import (
    CONFIG_FILE, PROJECT_ROOT, RUNTIME_DIR, TASKS_FILE, TIME_PATTERN, TIMEZONE,
    WEIXIN_CREDS_FILE, now_local,
)
from .storage import atomic_write_json, load_config, read_json


def resolve_notify_target() -> dict[str, Any] | None:
    config = load_config()
    receiver = config.get("receiver")
    if isinstance(receiver, str) and receiver.strip():
        return {
            "receiver": receiver.strip(),
            "receiver_name": config.get("receiver_name", "微信用户"),
            "is_group": bool(config.get("is_group", False)),
            "channel_type": config.get("channel_type", "weixin"),
            "notify_session_id": config.get("notify_session_id") or receiver.strip(),
        }
    creds = read_json(WEIXIN_CREDS_FILE, {})
    tokens = creds.get("context_tokens") if isinstance(creds, dict) else {}
    if isinstance(tokens, dict) and tokens:
        receivers = sorted(str(k) for k in tokens if str(k).strip())
        if receivers:
            receiver = receivers[0]
            return {
                "receiver": receiver,
                "receiver_name": "微信用户",
                "is_group": False,
                "channel_type": "weixin",
                "notify_session_id": receiver,
            }
    return None


def load_tasks() -> dict[str, Any]:
    data = read_json(TASKS_FILE, {"version": 1, "tasks": {}})
    if not isinstance(data, dict):
        data = {"version": 1, "tasks": {}}
    if not isinstance(data.get("tasks"), dict):
        data["tasks"] = {}
    return data


def local_naive(dt: datetime) -> str:
    return dt.astimezone(TIMEZONE).replace(tzinfo=None).isoformat()


def upsert_message_task(task_id: str, name: str, run_at: datetime, content: str) -> bool:
    target = resolve_notify_target()
    if target is None:
        print("ERROR notify target not found; cannot create scheduler task", file=sys.stderr)
        return False
    data = load_tasks()
    tasks = data["tasks"]
    timestamp = now_local().isoformat()
    task = tasks.get(task_id, {})
    tasks[task_id] = {
        "id": task_id,
        "name": name,
        "enabled": True,
        "created_at": task.get("created_at", timestamp),
        "updated_at": timestamp,
        "schedule": {"type": "once", "run_at": local_naive(run_at)},
        "action": {"type": "send_message", "content": content, **target},
        "next_run_at": local_naive(run_at),
    }
    data["version"] = 1
    data["updated_at"] = timestamp
    atomic_write_json(TASKS_FILE, data)
    return True


def daily_check() -> int:
    config = load_config()
    required = config.get("required_daily_fields", [])
    if not isinstance(required, list):
        required = []
    missing = missing_daily_fields([str(item) for item in required])
    if not missing:
        print("OK 今日记录已完整，不发送提醒")
        return 0
    now = now_local()
    content = (
        "今天的健身饮食记录还缺这些项目："
        + "、".join(missing)
        + "。可以直接回复，例如：体重70.2，今天练胸，睡了7小时，饮食正常。"
    )
    task_id = f"fitness-daily-check-{now.date().isoformat()}"
    if upsert_message_task(task_id, "健身饮食每日记录追问", now, content):
        print(f"OK created reminder task: {task_id}")
        return 0
    return 1


def read_crontab_raw_lines() -> list[str]:
    try:
        result = subprocess.run(["crontab", "-l"], check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def build_cron_line(run_time: str, python_bin: str | None = None) -> str:
    if not TIME_PATTERN.fullmatch(run_time):
        raise ValueError(f"invalid time: {run_time}")
    hour, minute = run_time.split(":", 1)
    script_path = PROJECT_ROOT / "scripts" / "fitness_coach.py"
    log_path = RUNTIME_DIR / "fitness_coach.log"
    python_path = python_bin or sys.executable or "python3"
    return (
        f"{minute} {hour} * * * {shlex.quote(str(python_path))} "
        f"{shlex.quote(str(script_path))} daily-check >> {shlex.quote(str(log_path))} 2>&1"
    )


def setup_schedule(apply: bool, replace: bool, daily_time: str | None, python_bin: str | None) -> int:
    config = load_config()
    run_time = daily_time or config.get("daily_check_time", "22:00")
    line = build_cron_line(str(run_time), python_bin)
    existing = read_crontab_raw_lines()
    new_lines = [item for item in existing if not (replace and "fitness_coach.py daily-check" in item)]
    already = any("fitness_coach.py daily-check" in item for item in new_lines)
    if already and not replace:
        print("INFO crontab already has fitness_coach.py daily-check")
        return 0
    new_lines.append(line)
    if apply:
        subprocess.run(["crontab", "-"], input="\n".join(new_lines).rstrip() + "\n", text=True, check=True, timeout=5)
        print("OK crontab updated")
    else:
        print("DRY-RUN cron line:")
        print(line)
    return 0


def remove_schedules(apply: bool) -> int:
    existing = read_crontab_raw_lines()
    kept = [line for line in existing if "fitness_coach.py" not in line]
    removed = len(existing) - len(kept)
    if apply and removed:
        subprocess.run(["crontab", "-"], input="\n".join(kept).rstrip() + "\n", text=True, check=True, timeout=5)
    print(f"{'OK' if apply else 'DRY-RUN'} cron entries removed: {removed}")
    return 0


def notify_target_status() -> str:
    return "已识别" if resolve_notify_target() else "未识别"
