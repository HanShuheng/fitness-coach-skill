from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from .settings import CONFIG_FILE, DEFAULT_CONFIG, ensure_dirs, now_local


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def load_config() -> dict[str, Any]:
    ensure_dirs()
    data = read_json(CONFIG_FILE, {})
    if not isinstance(data, dict):
        data = {}
    changed = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in data:
            data[key] = value
            changed = True
    if changed:
        save_config(data)
    return data


def save_config(data: dict[str, Any]) -> None:
    ensure_dirs()
    atomic_write_json(CONFIG_FILE, data)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    body = text[end + 5 :]
    meta: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.lower() == "true":
            parsed: Any = True
        elif value.lower() == "false":
            parsed = False
        elif value.startswith('"') and value.endswith('"'):
            parsed = value[1:-1]
        else:
            parsed = value
        meta[key.strip()] = parsed
    return meta, body


def format_frontmatter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif value is None:
            rendered = "null"
        else:
            rendered = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def extract_latest_payload(text: str) -> dict[str, Any]:
    marker = "```json payload"
    last = text.rfind(marker)
    if last == -1:
        return {}
    start = text.find("\n", last)
    end = text.find("```", start + 1)
    if start == -1 or end == -1:
        return {}
    try:
        data = json.loads(text[start + 1 : end].strip())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def copy_tree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def timestamp_id(prefix: str) -> str:
    return f"{prefix}-{now_local().strftime('%Y%m%d-%H%M%S')}"
