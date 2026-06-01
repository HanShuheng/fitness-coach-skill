from __future__ import annotations

import os
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SKILL_VERSION = "0.1.6"
DATA_SCHEMA_VERSION = 1
TIMEZONE = ZoneInfo("Asia/Shanghai")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = Path(os.environ.get("COW_WORKSPACE", "~/cow")).expanduser()


def resolve_runtime_dir() -> Path:
    explicit_dir = os.environ.get("FITNESS_COACH_DATA_DIR")
    if explicit_dir:
        return Path(explicit_dir).expanduser()
    return WORKSPACE / "fitness_coach"


RUNTIME_DIR = resolve_runtime_dir()
CONFIG_FILE = RUNTIME_DIR / "config.json"
PROFILE_FILE = RUNTIME_DIR / "profile.md"
DATA_DIR = RUNTIME_DIR / "data"
DAILY_DIR = DATA_DIR / "daily"
MEMORY_DIR = DATA_DIR / "memory"
SUMMARY_DIR = DATA_DIR / "summaries"
WEEKLY_SUMMARY_DIR = SUMMARY_DIR / "weekly"
MONTHLY_SUMMARY_DIR = SUMMARY_DIR / "monthly"
EXPORT_DIR = DATA_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"
MIGRATION_DIR = DATA_DIR / "migrations"
INDEX_FILE = DATA_DIR / "index.json"
UPDATE_STATE_FILE = DATA_DIR / "update_state.json"
TASKS_FILE = WORKSPACE / "scheduler" / "tasks.json"
WEIXIN_CREDS_FILE = Path("~/.weixin_cow_credentials.json").expanduser()

DEFAULT_UPDATE_CHECK_URL = (
    "https://raw.githubusercontent.com/HanShuheng/fitness-coach-skill/main/SKILL.md"
)
DEFAULT_REQUIRED_DAILY_FIELDS = [
    "body.weight_kg",
    "nutrition.summary",
    "training.status",
    "recovery.sleep_hours",
    "recovery.mood",
]
DEFAULT_CONFIG = {
    "schema_version": DATA_SCHEMA_VERSION,
    "daily_check_time": "22:00",
    "timezone": "Asia/Shanghai",
    "auto_setup_schedule": {"enabled": True, "daily_check_time": "22:00"},
    "required_daily_fields": DEFAULT_REQUIRED_DAILY_FIELDS,
    "version_check_url": DEFAULT_UPDATE_CHECK_URL,
    "skipped_versions": [],
}


def runtime_context() -> dict[str, str | bool]:
    explicit_dir = os.environ.get("FITNESS_COACH_DATA_DIR")
    return {
        "workspace": str(WORKSPACE),
        "runtime_dir": str(RUNTIME_DIR),
        "explicit_data_dir": bool(explicit_dir),
    }


def now_local() -> datetime:
    return datetime.now(TIMEZONE)


def today_local() -> date:
    return now_local().date()


def ensure_dirs() -> None:
    for path in (
        RUNTIME_DIR,
        DAILY_DIR,
        MEMORY_DIR,
        WEEKLY_SUMMARY_DIR,
        MONTHLY_SUMMARY_DIR,
        EXPORT_DIR,
        BACKUP_DIR,
        MIGRATION_DIR,
        TASKS_FILE.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)
