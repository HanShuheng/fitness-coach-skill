# 多 CowAgent 实例部署说明

本 skill 的数据隔离只依赖 CowAgent 实例的 `COW_WORKSPACE`。它不维护 `FITNESS_COACH_USER_ID`、`--user-id`、`FITNESS_COACH_INSTANCE_ID` 或 `users/default`。

## 一句话结论

一台服务器跑多个 CowAgent 时，每个 CowAgent 实例都必须有自己的 `COW_WORKSPACE`。

```text
CowAgent A: COW_WORKSPACE=/root/cow-a
CowAgent B: COW_WORKSPACE=/root/cow-b
```

对应的 skill 数据目录：

```text
/root/cow-a/fitness_coach/
/root/cow-b/fitness_coach/
```

这样档案、每日记录、提醒任务、导出包、备份和迁移文件都会隔离。

## 安装位置

每个 CowAgent 实例应把 skill 安装到自己的 workspace：

```text
/root/cow-a/skills/fitness-coach-skill/
/root/cow-b/skills/fitness-coach-skill/
```

不要让多个 CowAgent 实例共用同一个 workspace。否则它们会共用同一套 skill 数据和 scheduler 任务。

## systemd 示例

CowAgent A：

```ini
[Service]
Environment=COW_WORKSPACE=/root/cow-a
WorkingDirectory=/root/CowAgent-A
```

CowAgent B：

```ini
[Service]
Environment=COW_WORKSPACE=/root/cow-b
WorkingDirectory=/root/CowAgent-B
```

修改后重载并重启对应服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart cowagent-a.service
sudo systemctl restart cowagent-b.service
```

## 手动运行示例

```bash
COW_WORKSPACE=/root/cow-a cow start
COW_WORKSPACE=/root/cow-b cow start
```

## 验证

在各自 skill 目录下运行：

```bash
COW_WORKSPACE=/root/cow-a python scripts/fitness_coach.py info
COW_WORKSPACE=/root/cow-b python scripts/fitness_coach.py info
```

重点看：

- `runtime_context.workspace`
- `runtime_context.runtime_dir`
- `scheduler_file`

## 每日提醒

运行：

```bash
COW_WORKSPACE=/root/cow-a python scripts/fitness_coach.py setup-schedule
```

预览的 cron 行应包含：

```text
COW_WORKSPACE=/root/cow-a
```

写入 cron：

```bash
COW_WORKSPACE=/root/cow-a python scripts/fitness_coach.py setup-schedule --yes
```

## 可选：完整数据目录覆盖

通常不需要设置 `FITNESS_COACH_DATA_DIR`。只有你明确要把健身数据放到 workspace 之外时才使用：

```bash
COW_WORKSPACE=/root/cow-a \
FITNESS_COACH_DATA_DIR=/data/cow-a/fitness_coach \
python scripts/fitness_coach.py info
```

设置后，数据会写入 `FITNESS_COACH_DATA_DIR`，但 scheduler 任务仍属于 `COW_WORKSPACE`。

## 不覆盖的场景

如果一个 CowAgent 实例内部服务多个真实用户，本 skill 暂不做用户级隔离。此时不要试图通过 `FITNESS_COACH_USER_ID` 区分，因为该变量已不再被读取。需要由 CowAgent 上层路由、独立 workspace 或未来新增的明确多用户方案解决。
