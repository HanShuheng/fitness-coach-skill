# fitness-coach-skill

面向 CowAgent 的长期健身饮食教练 skill。它把训练评估、饮食建议、每日记录、基础档案、上下文压缩、定时追问、导出迁移和版本检查放在一个可开源、可安装、可维护的技能目录里。

## 能力概览

- 首次调用先建立基础档案，避免无上下文给计划。
- 支持记录每日体重、饮食、训练、睡眠、心情、压力、疼痛等信息。
- 默认每天 `22:00` 检查当天关键数据是否缺失，并通过 CowAgent 消息任务主动追问。
- 咨询训练、减脂、增肌、饮食时，先读取档案和压缩历史上下文。
- 支持导出、导入、备份、迁移、卸载和版本更新检查，降低数据丢失风险。
- 编排已有子 skill：`assessment`、`program-creation`、`rp-training`、`rp-diet`、`schoenfeld-hypertrophy`、`sbs-training`、`nutritional-specialist`。

## 快速开始

### 1. 安装

```bash
cow skill install HanShuheng/fitness-coach-skill
```

如果你是手动安装，把本仓库放到 CowAgent 的技能目录，例如：

```bash
$COW_WORKSPACE/skills/fitness-coach-skill
```

### 2. 确认当前 CowAgent workspace

这个项目只是一个 skill，不是服务。它不会自己识别“是哪一个 CowAgent 实例”，也不再维护 `FITNESS_COACH_USER_ID` 或 `--user-id`。

它只按当前进程的 `COW_WORKSPACE` 保存数据：

```bash
python scripts/fitness_coach.py info
```

请确认输出里的：

- `runtime_context.workspace` 是当前 CowAgent 实例的 workspace。
- `runtime_context.runtime_dir` 是这个实例的健身数据目录。

默认数据目录是：

```text
$COW_WORKSPACE/fitness_coach/
```

### 3. 初始化基础档案

```bash
python scripts/fitness_coach.py profile init
python scripts/fitness_coach.py profile status
```

首次真正服务用户时，skill 会先询问基础信息：目标、年龄或出生年份、性别、身高体重、训练经验、每周可训练时间、饮食限制、过敏和伤病限制。

### 4. 记录当天数据

```bash
python scripts/fitness_coach.py record \
  --payload-json '{"body":{"weight_kg":70.2},"nutrition":{"summary":"饮食正常"},"training":{"status":"trained"},"recovery":{"sleep_hours":7,"mood":"稳定"}}' \
  --raw-text "今天体重70.2，练胸，睡了7小时。"
```

### 5. 开启每日缺失项检查

默认检查时间是晚上 `22:00`：

```bash
python scripts/fitness_coach.py setup-schedule --yes
```

如果只想预览 crontab：

```bash
python scripts/fitness_coach.py setup-schedule
```

`setup-schedule` 生成的 cron 行会显式带上当前 `COW_WORKSPACE`，避免系统 cron 运行时丢失 workspace。

## 多 CowAgent 实例怎么隔离数据

本 skill 的隔离边界是 `COW_WORKSPACE`。

如果同一台服务器运行多个 CowAgent，请给每个 CowAgent 实例配置不同 workspace，例如：

```text
CowAgent A: COW_WORKSPACE=/root/cow-a
CowAgent B: COW_WORKSPACE=/root/cow-b
```

对应数据目录分别是：

```text
/root/cow-a/fitness_coach/
/root/cow-b/fitness_coach/
```

这样两个 CowAgent 不会共用档案、每日记录、提醒任务、导出包和备份。

注意：

- 不要让多个 CowAgent 实例共用同一个 `COW_WORKSPACE`。
- 安装 skill 时，应安装到各自 workspace 的 `skills/` 下。
- 首次使用前运行 `python scripts/fitness_coach.py info`，确认 `runtime_context.workspace`。
- 如果一个 CowAgent 实例内部同时服务多个真实用户，本 skill 暂不做用户级隔离；需要由 CowAgent 上层路由或独立 workspace 解决。

完整说明见：

- `references/cowagent-multi-instance-workspace.md`
- `references/multi-instance-deployment.md`

## 可选数据目录覆盖

通常只需要配置 `COW_WORKSPACE`。只有在你明确希望把健身数据放到 workspace 之外时，才设置：

```bash
export FITNESS_COACH_DATA_DIR="/data/cowagent-a/fitness_coach"
```

路径解析优先级：

1. `FITNESS_COACH_DATA_DIR`
2. `$COW_WORKSPACE/fitness_coach`

## 数据文件

主要文件：

- `profile.md`：基础档案。
- `config.json`：提醒时间、必填项、版本检查地址和跳过版本。
- `data/daily/YYYY-MM-DD.md`：每日记录。
- `data/memory/*.md`：长期记忆。
- `data/summaries/`：周/月摘要。
- `data/exports/`：导出包。
- `data/backups/`：备份。

`references/` 只保存模板和规范，不保存真实用户数据。

## 导出、迁移与恢复

导出全部数据：

```bash
python scripts/fitness_coach.py export --format zip
```

导入到新环境：

```bash
python scripts/fitness_coach.py import --from <export.zip>
```

迁移前预览：

```bash
python scripts/fitness_coach.py migrate --dry-run
```

执行迁移：

```bash
python scripts/fitness_coach.py migrate --yes
```

迁移和导入前会自动创建备份。Markdown 是主真相，索引和摘要可以重建。

## 版本更新

查看当前版本：

```bash
python scripts/fitness_coach.py version
```

检查远端更新：

```bash
python scripts/fitness_coach.py check-update
```

跳过某个版本：

```bash
python scripts/fitness_coach.py skip-version --version 0.2.0
```

更新前建议先准备备份：

```bash
python scripts/fitness_coach.py prepare-update --target-version 0.2.0
```

## 卸载

卸载 skill 代码不会自动删除 `$COW_WORKSPACE/fitness_coach/` 数据。推荐流程：

```bash
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

然后再使用 CowAgent 的 skill 卸载命令删除代码。

彻底删除数据前，命令会先自动导出：

```bash
python scripts/fitness_coach.py uninstall --remove-data --yes
```

更完整的卸载说明见 `references/uninstall.md`。

## 开发与测试

本项目运行时只使用 Python 标准库。测试需要 `pytest`：

```bash
python -m pytest -q tests
python -m compileall -q scripts tests
```

测试时请使用临时 `COW_WORKSPACE`，避免污染真实数据。
