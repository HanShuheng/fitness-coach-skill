# 数据契约

本文件说明 fitness-coach-skill 的真实数据保存位置、文件结构和兼容性规则。

## 隔离原则

本 skill 是 CowAgent 的一个 skill，不是单独服务。它不维护 `FITNESS_COACH_USER_ID`、`--user-id` 或用户级目录。

默认数据目录只由 CowAgent 实例的 `COW_WORKSPACE` 决定：

```text
$COW_WORKSPACE/fitness_coach/
```

如果同一台服务器运行多个 CowAgent 实例，必须给每个实例配置独立 `COW_WORKSPACE`。不要让多个实例共用同一个 workspace。

只有在明确需要把数据放到 workspace 之外时，才设置完整覆盖目录：

```bash
export FITNESS_COACH_DATA_DIR="/data/cowagent-a/fitness_coach"
```

路径优先级：

1. `FITNESS_COACH_DATA_DIR`
2. `$COW_WORKSPACE/fitness_coach`

## 目录结构

```text
$COW_WORKSPACE/fitness_coach/
├── profile.md
├── config.json
├── fitness_coach.log
└── data/
    ├── daily/
    │   └── YYYY-MM-DD.md
    ├── memory/
    ├── summaries/
    │   ├── weekly/
    │   └── monthly/
    ├── exports/
    ├── backups/
    ├── migrations/
    ├── index.json
    └── update_state.json
```

`$COW_WORKSPACE/scheduler/tasks.json` 属于 CowAgent workspace 的调度任务文件，不放在 `fitness_coach/` 内。

## 主真相

- Markdown 文件是主真相：`profile.md`、`data/daily/*.md`、`data/memory/*.md`、`data/summaries/**/*.md`。
- `index.json`、摘要和缓存类文件必须可重建。
- 更新 skill 代码不得覆盖 `$COW_WORKSPACE/fitness_coach/`。
- 迁移必须显式运行，并在写入前自动备份。

## Frontmatter

每个 Markdown 数据文件应包含 frontmatter：

```yaml
---
schema_version: 1
initialized: true
created_at: "2026-06-01T22:00:00+08:00"
updated_at: "2026-06-01T22:00:00+08:00"
record_id: "profile 或 YYYY-MM-DD"
source: "fitness-coach-skill"
---
```

## 扩展兼容

- 允许 `custom` / `extra` 保存未来字段。
- 旧脚本必须忽略未知字段，并尽量原样保留。
- 字段重命名不做破坏性迁移；优先新增字段并兼容读取旧字段。
- 导入、迁移、卸载删除数据前必须能先导出或备份。

## 验证命令

```bash
python scripts/fitness_coach.py info
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py rebuild-index
```
