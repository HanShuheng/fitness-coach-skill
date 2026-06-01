# fitness-coach-skill

面向 CowAgent 的长期健身饮食教练 skill。它把训练评估、饮食建议、每日记录、用户基础档案、上下文压缩、定时追问、导出迁移和版本检查放在一个可开源、可安装、可维护的技能目录里。

## 能力概览

- 首次调用先建立用户基础档案，避免无上下文给计划。
- 支持记录每日体重、饮食、训练、睡眠、心情、压力、疼痛等信息。
- 默认每天 `22:00` 检查当天关键数据是否缺失，并通过 CowAgent 消息任务主动追问。
- 咨询训练、减脂、增肌、饮食时，先读取用户档案和压缩历史上下文。
- 支持导出、导入、备份、迁移、卸载和版本更新检查，降低数据丢失风险。
- 编排已有子 skill：`assessment`、`program-creation`、`rp-training`、`rp-diet`、`schoenfeld-hypertrophy`、`sbs-training`、`nutritional-specialist`。

## 快速开始

### 1. 安装

```bash
cow skill install HanShuheng/fitness-coach-skill
```

如果你是手动安装，把本仓库放到 CowAgent 的技能目录，例如：

```bash
~/cow/skills/fitness-coach-skill
```

### 2. 初始化用户基础档案

```bash
python scripts/fitness_coach.py profile init
python scripts/fitness_coach.py profile status
```

首次真正服务用户时，skill 会先询问基础信息：目标、年龄或出生年份、性别、身高体重、训练经验、每周可训练时间、饮食限制、过敏和伤病限制。

### 3. 记录当天数据

```bash
python scripts/fitness_coach.py record \
  --payload-json '{"body":{"weight_kg":70.2},"nutrition":{"summary":"饮食正常"},"training":{"status":"trained"},"recovery":{"sleep_hours":7,"mood":"稳定"}}' \
  --raw-text "今天体重70.2，练胸，睡了7小时。"
```

### 4. 开启每日缺失项检查

默认检查时间是晚上 `22:00`：

```bash
python scripts/fitness_coach.py setup-schedule --yes
```

如果只想预览 crontab：

```bash
python scripts/fitness_coach.py setup-schedule
```

### 5. 查看状态

```bash
python scripts/fitness_coach.py info
```

## 数据保存位置

这个项目是 skill，不是常驻服务。它能区分“是谁”，靠的是 CowAgent 或调用命令传入一个稳定的用户/会话标识。

推荐每次调用脚本都带上。首次使用时，应先确认这个 ID：

```bash
python scripts/fitness_coach.py --user-id "<用户或会话ID>" info
```

例如微信用户 `wx-user-001`：

```bash
python scripts/fitness_coach.py --user-id wx-user-001 profile status
```

这个用户的数据会保存在：

```text
$COW_WORKSPACE/fitness_coach/users/wx-user-001/
```

如果不传 `--user-id`，会落到：

```text
$COW_WORKSPACE/fitness_coach/users/default/
```

这适合单用户测试，不适合多个真实用户长期使用。

`info` 和 `profile status` 会输出 `isolation.using_default_user`。如果它是 `true`，说明当前没有传用户 ID，多个用户可能共用 `default` 数据。

如果同一台服务器运行多个 CowAgent，再为每个 CowAgent 实例设置独立环境变量：

```bash
export FITNESS_COACH_INSTANCE_ID="wxbot-main"
```

设置后，真实数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/instances/wxbot-main/users/<user-id>/
```

也可以直接指定完整数据目录，优先级最高：

```bash
export FITNESS_COACH_DATA_DIR="/data/cowagent/wxbot-main/fitness_coach"
```

路径解析优先级：

1. `FITNESS_COACH_DATA_DIR`
2. `FITNESS_COACH_INSTANCE_ID` / `COWAGENT_INSTANCE_ID` / `COW_AGENT_INSTANCE_ID`
3. `--user-id` / `FITNESS_COACH_USER_ID` / `COW_USER_ID` / `COW_SESSION_ID`
4. `$COW_WORKSPACE/fitness_coach/users/default`

如果你不知道“在哪里设置环境变量”，看这里：

- systemd 服务：`sudo systemctl edit cowagent.service`，在 `[Service]` 下写 `Environment=FITNESS_COACH_INSTANCE_ID=wxbot-main`。
- 手动启动：运行 `FITNESS_COACH_INSTANCE_ID=wxbot-main cow start`。
- 验证：运行 `python scripts/fitness_coach.py info`，查看输出里的 `runtime_dir`。

完整步骤见 `references/multi-instance-deployment.md`。

主要文件：

- `profile.md`：用户基础档案。
- `config.json`：提醒时间、必填项、版本检查地址和跳过版本。
- `data/daily/YYYY-MM-DD.md`：每日记录。
- `data/memory/*.md`：长期记忆。
- `data/summaries/`：周/月摘要。
- `data/exports/`：导出包。
- `data/backups/`：备份。

`references/` 只保存模板和规范，不保存真实用户数据。

## 导出、迁移与恢复

导出全部用户数据：

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

卸载 skill 代码不会自动删除 `~/cow/fitness_coach/` 用户数据。推荐流程：

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
```

本地验证示例：

```bash
python -m compileall -q scripts tests
python scripts/fitness_coach.py version
python scripts/fitness_coach.py uninstall --dry-run
```

## 目录结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── examples/config.example.json
├── references/
├── scripts/
│   ├── fitness_coach.py
│   └── fitness_coach_lib/
└── tests/
```

## 免责声明

本项目仅用于学习、研究和个人健康管理自动化实践，不构成医疗建议、诊断、治疗方案或营养处方。涉及疾病、伤病、药物、进食障碍、妊娠、心血管、肾病等高风险情况时，请咨询合格医生、注册营养师或相关专业人士。

## 许可证

MIT License。详见 `LICENSE`。
