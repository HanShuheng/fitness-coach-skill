---
name: fitness-coach-skill
description: 用于健身教练场景的 CowAgent 编排 skill，覆盖训练评估、增肌训练、SBS 模板、饮食宏量、餐食个性化、长期记录和完整训练饮食计划，并按需要路由到子 skill。
version: "0.1.4"
entrypoint: "scripts/fitness_coach.py"
post_install_command: "python scripts/fitness_coach.py profile init"
config_file: "$FITNESS_COACH_DATA_DIR/config.json 或 $COW_WORKSPACE/fitness_coach[/instances/<id>]/users/<user-id>/config.json"
runtime_data_dir: "$FITNESS_COACH_DATA_DIR 或 $COW_WORKSPACE/fitness_coach[/instances/<id>]/users/<user-id>"
scheduler_file: "$COW_WORKSPACE/scheduler/tasks.json"
timezone: "Asia/Shanghai"
data_schema_version: 1
version_check_url: "https://raw.githubusercontent.com/HanShuheng/fitness-coach-skill/main/SKILL.md"
---

# Fitness Coach Skill

这是一个面向 CowAgent 的健身教练编排 skill。用户询问训练、增肌、力量计划、减脂、重组、热量与宏量、餐食建议、饮食执行、每日记录或完整训练饮食方案时使用它。

## 安全边界

- 不诊断或治疗疾病；涉及伤病、进食障碍、妊娠、糖尿病、心血管、肾病等高风险情况时，只给保守的一般建议，并建议咨询合格专业人士。
- 涉及食物时，必须严格尊重过敏、禁忌、宗教或饮食限制。
- 优先做实用教练：上下文不足时先评估，再给最小可执行下一步。

## CowAgent 运行方式

- 入口命令：`python scripts/fitness_coach.py <command>`。
- 首次服务用户时，先确认数据隔离身份：能否拿到稳定的用户/会话 ID；如果拿不到，必须提醒用户会落到 `users/default` 并可能多人共用。之后再运行 `profile init` 建立用户基础档案。
- 长期数据默认保存在 `$COW_WORKSPACE/fitness_coach/users/<user-id>`：`profile.md` 存基础档案，`data/daily/` 存每日记录，`data/summaries/` 存周/月摘要，`config.json` 存提醒时间、必填字段和版本检查地址。
- 调用脚本时必须尽量传 `--user-id <稳定用户或会话ID>`，否则会落到 `users/default`，多个用户会共用默认档案。
- 多 CowAgent 共用同一服务器时，再给每个实例设置 `FITNESS_COACH_INSTANCE_ID`，数据会隔离到 `$COW_WORKSPACE/fitness_coach/instances/<id>/users/<user-id>`；也可以用 `FITNESS_COACH_DATA_DIR` 直接指定完整数据目录。具体操作见 `references/multi-instance-deployment.md`。
- 自动追问使用 `setup-schedule --yes` 写入 crontab；每日检查会根据缺失字段向 `$COW_WORKSPACE/scheduler/tasks.json` 写入 CowAgent 消息任务。
- 具体命令、数据结构和实现细节以 `scripts/fitness_coach_lib/` 为准；面向用户的长期说明和迁移说明应放入 `references/`。

## 常用命令

| 场景 | 命令 |
|---|---|
| 首次建档 | `python scripts/fitness_coach.py --user-id '<用户ID>' profile init` |
| 查看档案状态 | `python scripts/fitness_coach.py --user-id '<用户ID>' profile status` |
| 更新档案 | `python scripts/fitness_coach.py profile update --payload-json '<json>' --raw-text '<用户原文>'` |
| 记录当天数据 | `python scripts/fitness_coach.py record --payload-json '<json>' --raw-text '<用户原文>'` |
| 读取教练上下文 | `python scripts/fitness_coach.py build-context --topic general` |
| 生成摘要 | `python scripts/fitness_coach.py summarize --weekly` 或 `--monthly` |
| 设置每日检查 | `python scripts/fitness_coach.py setup-schedule --yes` |
| 导出迁移包 | `python scripts/fitness_coach.py export` |
| 导入迁移包 | `python scripts/fitness_coach.py import --from <zip>` |
| 卸载预览 | `python scripts/fitness_coach.py uninstall --dry-run` |
| 移除提醒 | `python scripts/fitness_coach.py uninstall --remove-schedules --yes` |
| 导出后删除数据 | `python scripts/fitness_coach.py uninstall --remove-data --yes` |
| 检查版本 | `python scripts/fitness_coach.py check-update` |

## 数据记录与上下文读取

- 首次服务用户前，先确认 `profile status`；如果档案不存在或核心字段缺失，收集目标、身体、训练、饮食、生活方式和健康限制中的必要字段。
- 用户给出体重、训练、饮食、睡眠、情绪、伤病或执行反馈时，用 `record` 写入每日记录；能结构化就放入 `payload-json`，原话放入 `raw-text`。
- 回答个性化建议前，优先运行 `build-context` 读取基础档案、最近 14 天记录、周摘要和月摘要，再结合当前对话回答。
- 周期性复盘时运行 `summarize --weekly` 或 `summarize --monthly`；摘要只保留决策所需信息，避免重复堆积长日志。

## 导出、迁移与卸载

- 迁移前运行 `export`，它会在 `data/exports/` 生成 zip，并附带 manifest 与校验信息。
- 在新环境用 `import --from <zip>` 导入；导入前会自动创建 `pre-import` 备份。
- 卸载默认不删除任何数据。先运行 `uninstall --dry-run` 看影响范围；移除提醒用 `--remove-schedules --yes`；删除数据必须显式使用 `--remove-data --yes`，且会先自动导出。
- 更新前运行 `prepare-update --target-version <version>` 生成备份，更新后运行 `post-update-check` 查看版本、档案和通知目标状态。

## 版本检查

- 当前版本来自 frontmatter 的 `version` 与运行时 `SKILL_VERSION`。
- 默认检查地址为 `version_check_url`；`check-update` 会读取远端 `SKILL.md` 中的 `version:` 并写入 `data/update_state.json`。
- 用户暂不更新时，可用 `skip-version --version <version>` 跳过指定版本；需要恢复提醒时用 `clear-skipped-version --version <version>`。

## 子 Skill 路由

| 用户意图 | 路由到 | 用途 |
|---|---|---|
| 不知道从哪里开始、训练/饮食复盘、平台期、执行问题 | `assessment` | 先做结构化评估，再决定是否调整。 |
| 要完整训练计划、饮食计划或训练饮食一体化方案 | `program-creation` | 完成必要发现后输出可执行方案。 |
| 增肌训练、训练量、频率、RIR/RPE、deload、动作选择、周期安排 | `rp-training` | 使用 RP 增肌训练原则处理实践编程问题。 |
| 热量、宏量、减脂/增肌/维持、营养周期、餐次时机、补剂 | `rp-diet` | 使用 RP 饮食原则处理体成分营养策略。 |
| 肌肥大机制、训练变量、休息时间、高级技术、研究解释 | `schoenfeld-hypertrophy` | 用研究导向内容解释“为什么”。 |
| SBS 模板、训练最大值、自调节、RTF/RIR/set-threshold、表格设置 | `sbs-training` | 专门处理 Stronger By Science 模板选择和运行。 |
| 餐食建议、菜谱、购物清单、替换、偏好、过敏和忌口 | `nutritional-specialist` | 先读取或建立食物偏好，再给个性化建议。 |

常见组合：

- 新用户目标模糊：先用 `assessment`，用户同意后再用 `program-creation`。
- 增肌训练计划：`program-creation` + `rp-training`，需要机制解释时补 `schoenfeld-hypertrophy`。
- 减脂或增重计划：`program-creation` + `rp-diet`；涉及具体餐食时补 `nutritional-specialist`。
- SBS 设置或排障：优先 `sbs-training`；只有需要整体训练饮食整合时再加 `program-creation`。

## 输出标准

- 默认使用简体中文；除非用户要求，不切换语言。
- 能给数字时给具体数字：组数、次数、RIR/RPE、频率、热量、宏量、体重变化速度和周期长度。
- 上下文缺失时只问当前最关键的一两个问题，不一次性抛长表单。
- 完整方案要说明计算依据、关键权衡和执行检查点。
- 引用底层子 skill 时，遵循该子 skill 的来源标注要求。
