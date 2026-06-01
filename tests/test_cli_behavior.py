import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "fitness_coach.py"
LIB = ROOT / "scripts" / "fitness_coach_lib"


def run_cli(workspace: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """在隔离工作区运行 CLI，避免读写用户真实健身档案。"""
    env = os.environ.copy()
    env["COW_WORKSPACE"] = str(workspace)
    env["PYTHONPATH"] = str(ROOT / "scripts")
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def run_cli_with_env(
    workspace: Path,
    extra_env: dict[str, str],
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["COW_WORKSPACE"] = str(workspace)
    env["PYTHONPATH"] = str(ROOT / "scripts")
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def runtime_dir(workspace: Path) -> Path:
    return workspace / "fitness_coach" / "users" / "default"


def today() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()


def profile_payload() -> dict:
    return {
        "identity": {"nickname": "张三", "sex": "male", "age_or_birth_year": 1996},
        "body": {"height_cm": 175, "current_weight_kg": 72.5},
        "goals": {"primary": "增肌"},
        "training": {"experience": "intermediate", "available_days_per_week": 4},
        "nutrition": {"allergies": "无"},
        "health": {"injuries_or_limitations": "无"},
    }


def complete_daily_payload() -> dict:
    return {
        "body": {"weight_kg": 72.0},
        "nutrition": {"summary": "蛋白质 160g，热量 2600 kcal"},
        "training": {"status": "卧推 4x8，RIR 2"},
        "recovery": {"sleep_hours": 8, "mood": "稳定"},
    }


def extract_payload(markdown: str) -> dict:
    match = re.search(r"```json payload\n(.*?)\n```", markdown, re.S)
    assert match, "Markdown 中应包含 ```json payload 结构化数据块"
    return json.loads(match.group(1))


def extract_json_object(text: str) -> dict:
    start = text.find("{")
    assert start != -1, f"输出中应包含 JSON 对象：{text}"
    decoder = json.JSONDecoder()
    payload, _ = decoder.raw_decode(text[start:])
    return payload


def extract_export_path(stdout: str) -> Path:
    match = re.search(r"OK exported:\s*(.+)", stdout)
    assert match, f"export 输出应包含导出文件路径：{stdout}"
    return Path(match.group(1).strip())


def write_config_with_receiver(workspace: Path) -> None:
    config_path = runtime_dir(workspace) / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "daily_check_time": "22:00",
                "timezone": "Asia/Shanghai",
                "auto_setup_schedule": {"enabled": True, "daily_check_time": "22:00"},
                "required_daily_fields": [
                    "body.weight_kg",
                    "nutrition.summary",
                    "training.status",
                    "recovery.sleep_hours",
                    "recovery.mood",
                ],
                "version_check_url": "file:///dev/null",
                "skipped_versions": [],
                "receiver": "test-user",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_cli_entrypoint_and_library_layout_are_split_across_modules() -> None:
    assert CLI.exists(), "CLI 入口应为 scripts/fitness_coach.py"
    assert LIB.is_dir(), "业务实现应拆分到 scripts/fitness_coach_lib/ 多个模块中"

    module_files = sorted(
        path
        for path in LIB.glob("*.py")
        if path.name != "__init__.py" and not path.name.startswith("_")
    )
    assert len(module_files) >= 3, "持久化、档案、记录、导入导出等逻辑不应全部写在一个 py 中"


def test_profile_init_creates_persistent_profile_and_update_completes_it(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"

    init_result = run_cli(workspace, "profile", "init")
    profile_path = runtime_dir(workspace) / "profile.md"
    initial_text = profile_path.read_text(encoding="utf-8")
    initial_payload = extract_payload(initial_text)

    assert init_result.returncode == 0
    assert profile_path.exists()
    assert "用户基础信息档案" in initial_text
    assert initial_payload["identity"]["nickname"] == "unknown"

    update_result = run_cli(
        workspace,
        "profile",
        "update",
        "--payload-json",
        json.dumps(profile_payload(), ensure_ascii=False),
        "--raw-text",
        "首次建档：每周训练四天，目标增肌。",
    )
    show_result = run_cli(workspace, "profile", "show")
    status = extract_json_object(show_result.stdout)

    assert update_result.returncode == 0
    assert status["exists"] is True
    assert status["initialized"] is True
    assert status["missing_core_fields"] == []
    assert "张三" in show_result.stdout


def test_record_writes_markdown_daily_note(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    day = "2026-06-01"

    result = run_cli(
        workspace,
        "record",
        "--date",
        day,
        "--payload-json",
        json.dumps(complete_daily_payload(), ensure_ascii=False),
        "--raw-text",
        "状态稳定，训练完成。",
    )

    note_path = runtime_dir(workspace) / "data" / "daily" / f"{day}.md"
    note = note_path.read_text(encoding="utf-8")
    payload = extract_payload(note)

    assert result.returncode == 0
    assert note_path.exists()
    assert f"# 每日健身饮食记录 {day}" in note
    assert payload["body"]["weight_kg"] == 72.0
    assert payload["nutrition"]["summary"] == "蛋白质 160g，热量 2600 kcal"
    assert "状态稳定，训练完成。" in note


def test_daily_check_creates_reminder_when_required_fields_are_missing(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    write_config_with_receiver(workspace)

    result = run_cli(workspace, "daily-check")
    tasks = json.loads((workspace / "scheduler" / "tasks.json").read_text(encoding="utf-8"))
    created_task = tasks["tasks"][f"fitness-daily-check-{today()}"]
    content = created_task["action"]["content"]

    assert result.returncode == 0
    assert "created reminder task" in result.stdout
    assert "body.weight_kg" in content
    assert "nutrition.summary" in content
    assert "training.status" in content


def test_daily_check_accepts_complete_daily_record(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    write_config_with_receiver(workspace)
    run_cli(
        workspace,
        "record",
        "--date",
        today(),
        "--payload-json",
        json.dumps(complete_daily_payload(), ensure_ascii=False),
        "--raw-text",
        "今日记录完整。",
    )

    result = run_cli(workspace, "daily-check")

    assert result.returncode == 0
    assert "今日记录已完整" in result.stdout
    assert not (workspace / "scheduler" / "tasks.json").exists()


def test_export_and_import_round_trip_with_manifest(tmp_path: Path) -> None:
    source_workspace = tmp_path / "source-cow"
    target_workspace = tmp_path / "target-cow"
    day = "2026-06-01"

    run_cli(source_workspace, "profile", "init")
    run_cli(
        source_workspace,
        "profile",
        "update",
        "--payload-json",
        json.dumps(profile_payload(), ensure_ascii=False),
    )
    run_cli(
        source_workspace,
        "record",
        "--date",
        day,
        "--payload-json",
        json.dumps(complete_daily_payload(), ensure_ascii=False),
    )

    export_result = run_cli(source_workspace, "export")
    zip_path = extract_export_path(export_result.stdout)

    with zipfile.ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        manifest_paths = {item["path"] for item in manifest["files"]}

    assert zip_path.exists()
    assert manifest["schema_version"]
    assert manifest["skill_version"]
    assert manifest["created_at"]
    assert "profile.md" in manifest_paths
    assert f"data/daily/{day}.md" in manifest_paths

    import_result = run_cli(target_workspace, "import", "--from", str(zip_path))

    assert import_result.returncode == 0
    assert (runtime_dir(target_workspace) / "profile.md").exists()
    assert (runtime_dir(target_workspace) / "data" / "daily" / f"{day}.md").exists()


def test_skip_version_and_check_update_use_persisted_state(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    remote_skill = tmp_path / "remote-SKILL.md"
    remote_skill.write_text("---\nname: fitness-coach-skill\nversion: 0.2.0\n---\n", encoding="utf-8")

    skip_result = run_cli(workspace, "skip-version", "--version", "0.2.0")
    check_result = run_cli(workspace, "check-update", "--remote-url", remote_skill.as_uri())
    payload = extract_json_object(check_result.stdout)

    assert skip_result.returncode == 0
    assert payload["current_version"] == "0.1.3"
    assert payload["remote_version"] == "0.2.0"
    assert payload["has_update"] is True
    assert payload["skipped"] is True


def test_check_update_returns_nonzero_when_remote_version_cannot_be_read(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"

    result = run_cli(workspace, "check-update", "--remote-url", "file:///definitely/missing/SKILL.md", check=False)

    assert result.returncode == 1
    assert "check update failed" in result.stdout


def test_uninstall_dry_run_reports_targets_without_deleting_data(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    day = "2026-06-01"
    run_cli(workspace, "profile", "init")
    run_cli(
        workspace,
        "record",
        "--date",
        day,
        "--payload-json",
        json.dumps(complete_daily_payload(), ensure_ascii=False),
    )

    result = run_cli(workspace, "uninstall", "--dry-run")

    assert result.returncode == 0
    assert "DRY-RUN uninstall plan" in result.stdout
    assert str(runtime_dir(workspace)) in result.stdout
    assert (runtime_dir(workspace) / "profile.md").exists()
    assert (runtime_dir(workspace) / "data" / "daily" / f"{day}.md").exists()


def test_runtime_dir_can_be_isolated_by_instance_id(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    result = run_cli_with_env(
        workspace,
        {"FITNESS_COACH_INSTANCE_ID": "wxbot/main"},
        "profile",
        "init",
    )

    assert result.returncode == 0
    assert (workspace / "fitness_coach" / "instances" / "wxbot-main" / "users" / "default" / "profile.md").exists()
    assert not (workspace / "fitness_coach" / "users" / "default" / "profile.md").exists()


def test_explicit_data_dir_has_highest_priority(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    data_dir = tmp_path / "custom-data" / "fitness"
    result = run_cli_with_env(
        workspace,
        {
            "FITNESS_COACH_INSTANCE_ID": "ignored",
            "FITNESS_COACH_DATA_DIR": str(data_dir),
        },
        "profile",
        "init",
    )

    assert result.returncode == 0
    assert (data_dir / "profile.md").exists()
    assert not (workspace / "fitness_coach" / "instances" / "ignored" / "profile.md").exists()


def test_runtime_dir_can_be_isolated_by_user_id(tmp_path: Path) -> None:
    workspace = tmp_path / "cow"
    result_a = run_cli_with_env(workspace, {}, "--user-id", "wx/user/a", "profile", "init")
    result_b = run_cli_with_env(workspace, {}, "--user-id", "wx-user-b", "profile", "init")

    assert result_a.returncode == 0
    assert result_b.returncode == 0
    assert (workspace / "fitness_coach" / "users" / "wx-user-a" / "profile.md").exists()
    assert (workspace / "fitness_coach" / "users" / "wx-user-b" / "profile.md").exists()
    assert not (workspace / "fitness_coach" / "users" / "default" / "profile.md").exists()
