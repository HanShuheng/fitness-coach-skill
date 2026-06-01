from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from .settings import BACKUP_DIR, DATA_SCHEMA_VERSION, EXPORT_DIR, RUNTIME_DIR, SKILL_VERSION, ensure_dirs, now_local
from .storage import atomic_write_json, timestamp_id


EXCLUDED_DATA_DIRS = {"backups", "exports"}


def is_excluded_runtime_path(root: Path, path: Path) -> bool:
    try:
        rel = path.relative_to(root).parts
    except ValueError:
        return False
    return len(rel) >= 2 and rel[0] == "data" and rel[1] in EXCLUDED_DATA_DIRS


def iter_data_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not is_excluded_runtime_path(root, path):
            yield path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_manifest(root: Path) -> dict:
    files = []
    for path in iter_data_files(root):
        rel = path.relative_to(root).as_posix()
        files.append({"path": rel, "sha256": sha256_file(path), "size": path.stat().st_size})
    return {
        "created_at": now_local().isoformat(),
        "schema_version": DATA_SCHEMA_VERSION,
        "skill_version": SKILL_VERSION,
        "files": files,
    }


def export_data() -> Path:
    ensure_dirs()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_id = timestamp_id("fitness-coach-export")
    zip_path = EXPORT_DIR / f"{export_id}.zip"
    manifest = make_manifest(RUNTIME_DIR)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for item in manifest["files"]:
            path = RUNTIME_DIR / item["path"]
            zf.write(path, item["path"])
    return zip_path


def cmd_export() -> int:
    path = export_data()
    print(f"OK exported: {path}")
    return 0


def backup(label: str = "backup") -> Path:
    ensure_dirs()
    backup_dir = BACKUP_DIR / timestamp_id(label)
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME_DIR.iterdir():
        if path.name == "data":
            shutil.copytree(path, backup_dir / path.name, ignore=shutil.ignore_patterns(*EXCLUDED_DATA_DIRS))
        elif path.is_file():
            shutil.copy2(path, backup_dir / path.name)
    atomic_write_json(backup_dir / "manifest.json", make_manifest(backup_dir))
    return backup_dir


def cmd_backup() -> int:
    path = backup()
    print(f"OK backup created: {path}")
    return 0


def restore(backup_path: str) -> int:
    src = Path(backup_path).expanduser()
    if not src.exists() or not src.is_dir():
        print(f"ERROR backup not found: {src}")
        return 1
    backup("pre-restore")
    for item in src.iterdir():
        target = RUNTIME_DIR / item.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    print(f"OK restored from: {src}")
    return 0


def import_zip(zip_file: str) -> int:
    src = Path(zip_file).expanduser()
    if not src.exists():
        print(f"ERROR import file not found: {src}")
        return 1
    backup("pre-import")
    with zipfile.ZipFile(src) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        for item in manifest.get("files", []):
            info = zf.getinfo(item["path"])
            target = RUNTIME_DIR / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as dest:
                shutil.copyfileobj(source, dest)
            if sha256_file(target) != item["sha256"]:
                raise RuntimeError(f"sha256 mismatch after import: {item['path']}")
    print(f"OK imported: {src}")
    return 0
