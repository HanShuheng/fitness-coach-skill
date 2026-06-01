# 首次使用问题清单

首次调用本 skill 时，不要直接生成训练或饮食计划。先确认当前 CowAgent workspace，再建立基础档案。

## 第零步：确认 workspace

先运行：

```bash
python scripts/fitness_coach.py info
```

确认输出中的：

- `runtime_context.workspace` 指向当前 CowAgent 实例的 `COW_WORKSPACE`。
- `runtime_context.runtime_dir` 指向该实例的 `$COW_WORKSPACE/fitness_coach`。

如果同一台服务器有多个 CowAgent 实例，并且它们显示同一个 `COW_WORKSPACE`，不要继续建档。应先给每个 CowAgent 配置不同 workspace。

本 skill 不询问 `FITNESS_COACH_USER_ID`，也不使用 `--user-id`。如果一个 CowAgent 实例内同时服务多个真实用户，本 skill 暂不负责用户级隔离。

## 第一轮必问

核心字段足够前，不直接生成长期计划：

1. 主要目标：减脂、增肌、维持、力量、体态、健康，优先级是什么。
2. 性别、年龄或出生年份。
3. 身高、当前体重、目标体重。
4. 训练经验和当前水平。
5. 每周可训练几天、每次大约多久。
6. 饮食限制、过敏、宗教或伦理限制。
7. 伤病、疼痛、医疗限制。

用户拒答的非核心字段记为 `unknown`，不得编造。

## 第二轮按目标追问

根据目标选择性追问：

- 目标期限和可接受变化速度。
- 当前饮食、外食频率、餐次数偏好、做饭能力、预算。
- 当前训练计划、器械条件、主要动作水平、弱项肌群、训练偏好。
- 平均睡眠、压力、步数或日常活动量。
- 高风险时期：加班、出差、考试、聚餐、容易暴食的时段。
- 沟通偏好：喜欢简短指令、详细解释、表格还是清单。

## 初始化完成标准

当核心字段足够时，执行：

```bash
python scripts/fitness_coach.py profile update --payload-json '<json>' --raw-text '<用户原文>'
```

然后用：

```bash
python scripts/fitness_coach.py profile status
```

确认 `initialized` 为 `true`。之后再进入 `assessment` 或 `program-creation`。
