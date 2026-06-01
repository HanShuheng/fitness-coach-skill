from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "fitness_coach.py"


def run_cli(tmp_path: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    env["COW_WORKSPACE"] = str(tmp_path / "cow")
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=input_text,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def test_profile_init_update_and_status(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "profile", "status")
    assert result.returncode == 0
    assert '"initialized": false' in result.stdout

    assert run_cli(tmp_path, "profile", "init").returncode == 0
    payload = {
        "goals": {"primary": "减脂"},
        "identity": {"sex": "男", "age_or_birth_year": "1998"},
        "body": {"height_cm": 175, "current_weight_kg": 75},
        "training": {"experience": "2年", "available_days_per_week": 4},
        "nutrition": {"allergies": "无"},
        "health": {"injuries_or_limitations": "无"},
        "custom": {"source": "test"},
    }
    result = run_cli(tmp_path, "profile", "update", "--payload-json", json.dumps(payload, ensure_ascii=False))
    assert result.returncode == 0
    assert "initialized: true" in result.stdout

    profile_path = tmp_path / "cow" / "fitness_coach" / "profile.md"
    text = profile_path.read_text(encoding="utf-8")
    assert "custom" in text
    assert "减脂" in text


def test_record_daily_check_and_rebuild_index(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "daily-check")
    assert result.returncode == 1
    assert "notify target not found" in result.stderr

    payload = {
        "body": {"weight_kg": 75.2},
        "nutrition": {"summary": "正常"},
        "training": {"status": "trained"},
        "recovery": {"sleep_hours": 7, "mood": "ok"},
    }
    result = run_cli(
        tmp_path,
        "record",
        "--payload-json",
        json.dumps(payload, ensure_ascii=False),
        "--raw-text",
        "今天训练正常",
    )
    assert result.returncode == 0
    result = run_cli(tmp_path, "daily-check")
    assert result.returncode == 0
    assert "已完整" in result.stdout

    index = tmp_path / "cow" / "fitness_coach" / "data" / "index.json"
    assert run_cli(tmp_path, "rebuild-index").returncode == 0
    assert index.exists()


def test_export_import_manifest(tmp_path: Path) -> None:
    run_cli(tmp_path, "profile", "init")
    run_cli(tmp_path, "record", "--payload-json", '{"body":{"weight_kg":70}}')
    result = run_cli(tmp_path, "export", "--format", "zip")
    assert result.returncode == 0
    zip_path = Path(result.stdout.strip().split("OK exported: ", 1)[1])
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        assert "manifest.json" in zf.namelist()
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    assert manifest["files"]
    assert all("sha256" in item for item in manifest["files"])

    other = tmp_path / "other"
    result = run_cli(other, "import", "--from", str(zip_path))
    assert result.returncode == 0
    assert (other / "cow" / "fitness_coach" / "profile.md").exists()


def test_migrate_uninstall_and_version_skip(tmp_path: Path) -> None:
    assert run_cli(tmp_path, "migrate", "--dry-run").returncode == 0
    assert run_cli(tmp_path, "uninstall", "--dry-run").returncode == 0
    assert run_cli(tmp_path, "skip-version", "--version", "9.9.9").returncode == 0
    config = json.loads((tmp_path / "cow" / "fitness_coach" / "config.json").read_text(encoding="utf-8"))
    assert "9.9.9" in config["skipped_versions"]
    assert run_cli(tmp_path, "clear-skipped-version", "--version", "9.9.9").returncode == 0
