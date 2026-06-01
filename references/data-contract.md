# 数据契约

## 目录

真实数据只保存到运行数据目录。skill 不是服务，不能凭空知道当前用户是谁；调用方必须传入稳定用户/会话标识。

推荐调用方式：

```bash
python scripts/fitness_coach.py --user-id "<用户或会话ID>" info
```

默认结构是：

```text
fitness_coach/
└── users/
    └── <user-id>/
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

## 多实例隔离

同一台服务器运行多个 CowAgent 时，如果它们共用同一个 `COW_WORKSPACE`，默认路径会冲突。请使用环境变量隔离：

```bash
export FITNESS_COACH_INSTANCE_ID="wxbot-main"
```

保存路径会变为：

```text
$COW_WORKSPACE/fitness_coach/instances/wxbot-main/users/<user-id>/
```

也可以直接指定完整目录：

```bash
export FITNESS_COACH_DATA_DIR="/data/cowagent/wxbot-main/fitness_coach"
```

路径优先级：

1. `FITNESS_COACH_DATA_DIR`
2. `FITNESS_COACH_INSTANCE_ID` / `COWAGENT_INSTANCE_ID` / `COW_AGENT_INSTANCE_ID`
3. `--user-id` / `FITNESS_COACH_USER_ID` / `COW_USER_ID` / `COW_SESSION_ID`
4. `$COW_WORKSPACE/fitness_coach/users/default`

不会设置环境变量时，先读 `references/multi-instance-deployment.md`。里面写了 systemd、命令行手动启动和验证方法。

## 主真相

- Markdown 文件是主真相：`profile.md`、`daily/*.md`、`memory/*.md`。
- `index.json` 和 summaries 是派生数据，可重建。
- `references/` 只存模板，不存真实用户数据。

## 扩展规则

- 每个 Markdown 文件必须保留 frontmatter：`schema_version`、`created_at`、`updated_at`、`record_id`、`source`。
- 新字段优先加入已有对象；无法归类时放入 `custom`。
- 旧版本脚本必须忽略未知字段并原样保留。
- 字段重命名时保留旧字段兼容读取，不做破坏性删除。
