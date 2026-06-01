# 迁移与备份策略

## 原则

- 更新 skill 代码不等于迁移用户数据。
- 迁移必须由用户显式运行。
- 任何影响真实数据的操作前，先备份。

## 命令

```bash
python scripts/fitness_coach.py backup
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py import --from <zip>
python scripts/fitness_coach.py migrate --dry-run
python scripts/fitness_coach.py migrate --yes
python scripts/fitness_coach.py restore --backup-id <backup_dir>
```

## 迁移要求

- `migrate --dry-run` 不写入真实数据。
- `migrate --yes` 前自动创建 `pre-migrate` 备份。
- 导入前自动创建 `pre-import` 备份。
- 导出 zip 必须包含 `manifest.json`，记录 schema、skill 版本、文件清单和 sha256。
- `data/backups/` 与 `data/exports/` 不再递归进入新的备份或导出包，避免无限嵌套。
