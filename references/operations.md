# 操作手册

本手册集中说明 fitness-coach-skill 的日常操作。README 只保留快速入口，详细步骤统一放在这里，避免多份文档重复维护。

## 首次使用

先确认当前 CowAgent workspace：

```bash
python scripts/fitness_coach.py info
```

重点检查：

- `runtime_context.workspace` 是否是当前 CowAgent 实例的 `COW_WORKSPACE`。
- `runtime_context.runtime_dir` 是否是预期数据目录。

然后初始化基础档案：

```bash
python scripts/fitness_coach.py profile init
python scripts/fitness_coach.py profile status
```

第一次真正服务用户时，先问核心信息，不要直接生成长期计划：

1. 主要目标：减脂、增肌、维持、力量、体态、健康。
2. 性别、年龄或出生年份。
3. 身高、当前体重、目标体重。
4. 训练经验、每周可训练几天、每次多久。
5. 饮食限制、过敏、忌口。
6. 伤病、疼痛、医疗限制。

用户拒答的非核心字段记为 `unknown`，不得编造。

## 多 CowAgent 实例

本 skill 的数据隔离只依赖 `COW_WORKSPACE`。它不维护 `FITNESS_COACH_USER_ID`、`--user-id`、`FITNESS_COACH_INSTANCE_ID` 或 `users/default`。

同一台服务器运行多个 CowAgent 时，每个实例都必须有自己的 workspace：

```text
CowAgent A: COW_WORKSPACE=/root/cow-a
CowAgent B: COW_WORKSPACE=/root/cow-b
```

对应数据目录：

```text
/root/cow-a/fitness_coach/
/root/cow-b/fitness_coach/
```

systemd 示例：

```ini
[Service]
Environment=COW_WORKSPACE=/root/cow-a
WorkingDirectory=/root/CowAgent-A
```

手动启动示例：

```bash
COW_WORKSPACE=/root/cow-a cow start
```

安装 skill 时，也应安装到对应 workspace 的 `skills/` 下。

如果一个 CowAgent 实例内部服务多个真实用户，本 skill 暂不做用户级隔离。需要由 CowAgent 上层路由、独立 workspace 或未来明确的多用户方案解决。

## 每日提醒

默认每天 `22:00` 检查这些字段：

- `body.weight_kg`
- `nutrition.summary`
- `training.status`
- `recovery.sleep_hours`
- `recovery.mood`

预览 cron：

```bash
python scripts/fitness_coach.py setup-schedule
```

写入 cron：

```bash
python scripts/fitness_coach.py setup-schedule --yes
```

生成的 cron 行会显式包含 `COW_WORKSPACE`，避免系统 cron 运行时落到错误 workspace。

## 上下文读取

回答训练、减脂、饮食、增肌相关问题前，优先运行：

```bash
python scripts/fitness_coach.py build-context --topic general
```

默认包含：

- 基础档案。
- 最近 14 天每日记录。
- 最近 8 周周摘要、最近 3 个月月摘要。
- `data/memory/` 中和问题相关的长期要点。

主题可用：

- `training`
- `diet`
- `weight-loss`
- `general`

不要把所有历史原文一次塞入上下文；只保留决策需要的事实、趋势和风险。

## 导出、导入与迁移

导出：

```bash
python scripts/fitness_coach.py export --format zip
```

导入：

```bash
python scripts/fitness_coach.py import --from <export.zip>
```

备份和恢复：

```bash
python scripts/fitness_coach.py backup
python scripts/fitness_coach.py restore --backup-id <backup_dir>
```

迁移预览：

```bash
python scripts/fitness_coach.py migrate --dry-run
```

执行迁移：

```bash
python scripts/fitness_coach.py migrate --yes
```

安全要求：

- 更新 skill 代码不等于迁移用户数据。
- 迁移必须由用户显式运行。
- 导入、迁移、删除数据前必须自动备份。
- 导出 zip 必须包含 `manifest.json`，记录 schema、skill 版本、文件清单和 sha256。

## 版本更新

查看当前版本：

```bash
python scripts/fitness_coach.py version
```

检查更新：

```bash
python scripts/fitness_coach.py check-update
```

跳过版本：

```bash
python scripts/fitness_coach.py skip-version --version <version>
```

取消跳过：

```bash
python scripts/fitness_coach.py clear-skipped-version --version <version>
```

更新前准备：

```bash
python scripts/fitness_coach.py prepare-update --target-version <version>
```

更新后检查：

```bash
python scripts/fitness_coach.py post-update-check
```

版本检查失败必须明确报错，不能假装已是最新。

## 卸载

卸载 skill 代码不会自动删除 `$COW_WORKSPACE/fitness_coach/` 数据。推荐顺序：

```bash
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

然后再使用 CowAgent 的 skill uninstall/remove 命令删除 skill 代码。

只停用提醒但保留数据：

```bash
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

彻底删除数据：

```bash
python scripts/fitness_coach.py uninstall --remove-data --yes
```

`--remove-data --yes` 会先自动导出，再删除当前运行目录。

恢复：

```bash
python scripts/fitness_coach.py import --from <export.zip>
```
