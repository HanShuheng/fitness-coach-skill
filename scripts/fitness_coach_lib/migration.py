from __future__ import annotations

from .archive import backup
from .daily import rebuild_index
from .settings import DATA_SCHEMA_VERSION, MIGRATION_DIR, now_local
from .storage import atomic_write_text


def migrate(dry_run: bool, yes: bool) -> int:
    if dry_run:
        print(f"DRY-RUN current schema is compatible: {DATA_SCHEMA_VERSION}")
        return 0
    if not yes:
        print("ERROR migrate requires --yes or --dry-run")
        return 2
    backup_path = backup("pre-migrate")
    log_path = MIGRATION_DIR / f"migration-{now_local().strftime('%Y%m%d-%H%M%S')}.md"
    atomic_write_text(
        log_path,
        "\n".join([
            "# Migration log",
            "",
            f"- time: {now_local().isoformat()}",
            f"- target_schema_version: {DATA_SCHEMA_VERSION}",
            f"- backup: {backup_path}",
            "- action: no destructive migration required",
            "",
        ]),
    )
    rebuild_index()
    print(f"OK migration completed: {log_path}")
    return 0
