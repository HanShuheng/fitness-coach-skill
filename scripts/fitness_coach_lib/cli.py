from __future__ import annotations

import argparse

from .archive import cmd_backup, cmd_export, import_zip, restore
from .context import build_context, summarize
from .daily import rebuild_index, record
from .info import info
from .migration import migrate
from .profile import init_profile, profile_status, show_profile, update_profile
from .scheduler import daily_check, setup_schedule
from .state import status
from .storage import load_config
from .uninstall import purge, uninstall
from .versioning import check_update, post_update_check, prepare_update, skip_version, version


def main() -> int:
    parser = argparse.ArgumentParser(description="Fitness Coach Skill runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    p_profile = sub.add_parser("profile")
    p_profile_sub = p_profile.add_subparsers(dest="profile_command", required=True)
    p_profile_sub.add_parser("status")
    p_profile_sub.add_parser("init")
    p_update = p_profile_sub.add_parser("update")
    p_update.add_argument("--payload-json")
    p_update.add_argument("--raw-text")
    p_profile_sub.add_parser("show")

    p_record = sub.add_parser("record")
    p_record.add_argument("--payload-json")
    p_record.add_argument("--raw-text")
    p_record.add_argument("--date", help="YYYY-MM-DD; default today")

    sub.add_parser("daily-check")
    p_context = sub.add_parser("build-context")
    p_context.add_argument("--topic", default="general")
    p_summary = sub.add_parser("summarize")
    group = p_summary.add_mutually_exclusive_group(required=True)
    group.add_argument("--weekly", action="store_true")
    group.add_argument("--monthly", action="store_true")

    p_schedule = sub.add_parser("setup-schedule")
    p_schedule.add_argument("--yes", action="store_true")
    p_schedule.add_argument("--replace", action="store_true")
    p_schedule.add_argument("--daily-time")
    p_schedule.add_argument("--python", dest="python_bin")

    sub.add_parser("init")
    sub.add_parser("info")
    sub.add_parser("status")
    sub.add_parser("sync")
    sub.add_parser("backup")
    p_restore = sub.add_parser("restore")
    p_restore.add_argument("--backup-id", required=True)
    p_export = sub.add_parser("export")
    p_export.add_argument("--format", choices=["zip"], default="zip")
    p_export_data = sub.add_parser("export-data")
    p_export_data.add_argument("--format", choices=["zip"], default="zip")
    p_import = sub.add_parser("import")
    p_import.add_argument("--from", dest="from_path", required=True)
    p_import_data = sub.add_parser("import-data")
    p_import_data.add_argument("--from", dest="from_path", required=True)
    sub.add_parser("rebuild-index")
    sub.add_parser("repair")

    p_migrate = sub.add_parser("migrate")
    p_migrate.add_argument("--dry-run", action="store_true")
    p_migrate.add_argument("--yes", action="store_true")

    p_uninstall = sub.add_parser("uninstall")
    p_uninstall.add_argument("--dry-run", action="store_true")
    p_uninstall.add_argument("--remove-schedules", action="store_true")
    p_uninstall.add_argument("--remove-data", action="store_true")
    p_uninstall.add_argument("--yes", action="store_true")
    p_purge = sub.add_parser("purge")
    p_purge.add_argument("--yes", action="store_true")
    p_purge.add_argument("--confirm")

    sub.add_parser("version")
    p_check = sub.add_parser("check-update")
    p_check.add_argument("--remote-url")
    p_skip = sub.add_parser("skip-version")
    p_skip.add_argument("--version", required=True)
    p_clear = sub.add_parser("clear-skipped-version")
    p_clear.add_argument("--version", required=True)
    p_prepare = sub.add_parser("prepare-update")
    p_prepare.add_argument("--target-version", required=True)
    sub.add_parser("post-update-check")

    args = parser.parse_args()
    if args.command == "profile":
        if args.profile_command == "status":
            import json
            print(json.dumps(profile_status(), ensure_ascii=False, indent=2))
            return 0
        if args.profile_command == "init":
            return init_profile()
        if args.profile_command == "update":
            return update_profile(args.payload_json, args.raw_text)
        if args.profile_command == "show":
            return show_profile()
    if args.command == "record":
        return record(args.payload_json, args.raw_text, args.date)
    if args.command == "daily-check":
        return daily_check()
    if args.command == "build-context":
        return build_context(args.topic)
    if args.command == "summarize":
        return summarize("weekly" if args.weekly else "monthly")
    if args.command == "setup-schedule":
        return setup_schedule(args.yes, args.replace, args.daily_time, args.python_bin)
    if args.command == "init":
        load_config()
        return init_profile()
    if args.command == "info":
        return info()
    if args.command == "status":
        return status()
    if args.command == "sync":
        print("OK sync skipped: 本 skill 暂无必须同步的外部数据源。")
        return 0
    if args.command == "backup":
        return cmd_backup()
    if args.command == "restore":
        return restore(args.backup_id)
    if args.command in {"export", "export-data"}:
        return cmd_export()
    if args.command in {"import", "import-data"}:
        return import_zip(args.from_path)
    if args.command == "rebuild-index":
        return rebuild_index()
    if args.command == "repair":
        cmd_backup()
        return rebuild_index()
    if args.command == "migrate":
        return migrate(args.dry_run, args.yes)
    if args.command == "uninstall":
        return uninstall(args.dry_run, args.remove_schedules, args.remove_data, args.yes)
    if args.command == "purge":
        return purge(args.yes, args.confirm)
    if args.command == "version":
        return version()
    if args.command == "check-update":
        return check_update(args.remote_url)
    if args.command == "skip-version":
        return skip_version(args.version)
    if args.command == "clear-skipped-version":
        return skip_version(args.version, clear=True)
    if args.command == "prepare-update":
        return prepare_update(args.target_version)
    if args.command == "post-update-check":
        return post_update_check()
    return 2
