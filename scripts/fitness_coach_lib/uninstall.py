from __future__ import annotations

import shutil

from .archive import backup, export_data
from .scheduler import remove_schedules
from .settings import RUNTIME_DIR


def uninstall(dry_run: bool, remove_schedules_flag: bool, remove_data: bool, yes: bool) -> int:
    if dry_run:
        print("DRY-RUN uninstall plan")
        print("- remove cron entries containing fitness_coach.py if --remove-schedules --yes is used")
        print(f"- keep data directory by default: {RUNTIME_DIR}")
        print("- remove data only with --remove-data --yes; export zip will be created first")
        return 0
    if remove_schedules_flag:
        if not yes:
            print("ERROR --remove-schedules requires --yes")
            return 2
        backup("before-uninstall")
        remove_schedules(apply=True)
    if remove_data:
        if not yes:
            print("ERROR --remove-data requires --yes")
            return 2
        backup("before-purge")
        export_path = export_data("before-purge")
        print(f"OK export created before data removal: {export_path}")
        if RUNTIME_DIR.exists():
            shutil.rmtree(RUNTIME_DIR)
            print(f"OK removed data directory: {RUNTIME_DIR}")
    if not remove_schedules_flag and not remove_data:
        print("Nothing changed. Use --dry-run, --remove-schedules --yes, or --remove-data --yes.")
    return 0


def purge(yes: bool, confirm: str | None) -> int:
    if not yes or confirm != "确认清除":
        print("ERROR 清除数据需要 --yes --confirm 确认清除")
        print(f"将删除的数据目录：{RUNTIME_DIR}")
        print("此操作会先创建 before-purge 备份和导出包。")
        return 2
    return uninstall(False, False, True, True)
