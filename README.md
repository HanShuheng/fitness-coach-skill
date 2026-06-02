# fitness-coach-skill

面向 CowAgent 的长期健身饮食教练 skill。它负责建立基础档案、记录每日体重/饮食/训练/恢复、在缺失数据时主动追问，并在回答训练、减脂、增肌、饮食问题前读取历史上下文。

## 能力

- 首次使用先建档：目标、身体数据、训练背景、饮食限制、伤病限制。
- 每日记录：体重、饮食、训练、睡眠、心情、压力、疼痛等。
- 默认每天 `22:00` 检查缺失项，并写入 CowAgent scheduler 任务。
- 回答相关问题前读取基础档案、最近记录、摘要和长期记忆。
- 支持备份、导出、导入、迁移、卸载和版本检查。
- 编排子 skill：`assessment`、`program-creation`、`rp-training`、`rp-diet`、`schoenfeld-hypertrophy`、`sbs-training`、`nutritional-specialist`。

## 快速开始

安装：

```bash
cow skill install HanShuheng/fitness-coach-skill
```

确认当前 CowAgent workspace 和数据目录：

```bash
python scripts/fitness_coach.py info
```

初始化基础档案：

```bash
python scripts/fitness_coach.py init
python scripts/fitness_coach.py profile init
python scripts/fitness_coach.py profile status
```

记录当天数据：

```bash
python scripts/fitness_coach.py record \
  --payload-json '{"body":{"weight_kg":70.2},"nutrition":{"summary":"饮食正常"},"training":{"status":"trained"},"recovery":{"sleep_hours":7,"mood":"稳定"}}' \
  --raw-text "今天体重70.2，练胸，睡了7小时。"
```

预览每日检查 cron：

```bash
python scripts/fitness_coach.py setup-schedule
```

写入每日检查 cron：

```bash
python scripts/fitness_coach.py setup-schedule --yes
```

## 数据保存在哪里

默认数据目录：

```text
$COW_WORKSPACE/fitness_coach/
```

本 skill 只按 `COW_WORKSPACE` 隔离 CowAgent 实例，不再维护 `FITNESS_COACH_USER_ID` 或 `--user-id`。一台服务器跑多个 CowAgent 时，请给每个实例配置不同 `COW_WORKSPACE`。

可选完整覆盖目录：

```bash
export FITNESS_COACH_DATA_DIR="/data/cowagent-a/fitness_coach"
```

路径优先级：

1. `FITNESS_COACH_DATA_DIR`
2. `$COW_WORKSPACE/fitness_coach`

## 常用命令

| 场景 | 命令 |
|---|---|
| 查看状态 | `python scripts/fitness_coach.py info` |
| 详细诊断 | `python scripts/fitness_coach.py status` |
| 初始化 | `python scripts/fitness_coach.py init` |
| 建立档案 | `python scripts/fitness_coach.py profile init` |
| 更新档案 | `python scripts/fitness_coach.py profile update --payload-json '<json>' --raw-text '<原文>'` |
| 记录每日数据 | `python scripts/fitness_coach.py record --payload-json '<json>' --raw-text '<原文>'` |
| 构建上下文 | `python scripts/fitness_coach.py build-context --topic general` |
| 每日缺失检查 | `python scripts/fitness_coach.py daily-check` |
| 设置提醒 | `python scripts/fitness_coach.py setup-schedule --yes` |
| 导出数据 | `python scripts/fitness_coach.py export --format zip` |
| 标准导出别名 | `python scripts/fitness_coach.py export-data --format zip` |
| 导入数据 | `python scripts/fitness_coach.py import --from <export.zip>` |
| 标准导入别名 | `python scripts/fitness_coach.py import-data --from <export.zip>` |
| 修复可恢复状态 | `python scripts/fitness_coach.py repair` |
| 检查更新 | `python scripts/fitness_coach.py check-update` |
| 卸载预览 | `python scripts/fitness_coach.py uninstall --dry-run` |
| 清除数据 | `python scripts/fitness_coach.py purge --yes --confirm 确认清除` |

## 文档地图

- [操作手册](references/operations.md)：首次使用、多实例 workspace、提醒、导出导入、迁移、更新、卸载。
- [数据契约](references/data-contract.md)：运行目录、文件结构、frontmatter、兼容性要求。
- [基础档案模板](references/profile-template.md)
- [每日记录模板](references/daily-log-template.md)
- [长期记忆模板](references/memory-template.md)

`references/` 只保存模板和规范，不保存真实用户数据。

## 免责声明

本 skill 只提供一般健身、训练和饮食管理建议，不提供医疗诊断或治疗。涉及伤病、慢性病、进食障碍、妊娠、药物、医生限制或其他高风险情况时，请咨询合格专业人士。

## 开发与测试

本项目运行时只使用 Python 标准库，`requirements.txt` 仅作为安装规范入口。测试需要 `pytest`：

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m compileall -q scripts tests
```

测试时请使用临时 `COW_WORKSPACE`，避免污染真实数据。
