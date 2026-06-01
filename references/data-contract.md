# 数据契约

## 目录

真实数据只保存到 `~/cow/fitness_coach/`：

```text
fitness_coach/
├── config.json
├── profile.md
└── data/
    ├── daily/YYYY-MM-DD.md
    ├── memory/*.md
    ├── summaries/weekly/*.md
    ├── summaries/monthly/*.md
    ├── index.json
    ├── update_state.json
    ├── exports/*.zip
    ├── backups/
    └── migrations/
```

## 主真相

- Markdown 文件是主真相：`profile.md`、`daily/*.md`、`memory/*.md`。
- `index.json` 和 summaries 是派生数据，可重建。
- `references/` 只存模板，不存真实用户数据。

## 扩展规则

- 每个 Markdown 文件必须保留 frontmatter：`schema_version`、`created_at`、`updated_at`、`record_id`、`source`。
- 新字段优先加入已有对象；无法归类时放入 `custom`。
- 旧版本脚本必须忽略未知字段并原样保留。
- 字段重命名时保留旧字段兼容读取，不做破坏性删除。
