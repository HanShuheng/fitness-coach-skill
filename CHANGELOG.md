# 更新日志

## 0.1.8 - 2026-06-02

- 按 CowAgent skill 开发规范补齐标准命令入口：`init`、`status`、`sync`、`repair`、`purge`、`export-data`、`import-data`。
- 新增初始化 preflight 状态，`info` 输出 `initialization`，`status` 输出详细诊断和下一步命令。
- 新增 `requirements.txt`，明确运行时仅使用 Python 标准库。
- 备份/导出命名加入 skill、reason、schema 版本和时间戳。
- 清除数据流程增加 `purge --yes --confirm 确认清除` 二次确认入口。
- README、SKILL 和操作手册同步补充规范命令和初始化状态说明。

## 0.1.7 - 2026-06-01

- 精简文档结构，合并首次使用、多实例、提醒、上下文、导出迁移、更新和卸载说明到 `references/operations.md`。
- 删除重复的操作类 references 文档，只保留数据契约和模板文档。
- README 改为轻量入口，避免与 `SKILL.md` 和 references 重复维护。
- 模板中的默认路径统一为 `$COW_WORKSPACE/fitness_coach`。

## 0.1.6 - 2026-06-01

- 移除用户层数据隔离实现，脚本不再解析 `--user-id` / `--profile-id`，也不再读取 `FITNESS_COACH_USER_ID` 等用户身份环境变量。
- 默认数据目录恢复为 `$COW_WORKSPACE/fitness_coach`，多 CowAgent 实例只通过独立 `COW_WORKSPACE` 隔离。
- `info` 和 `profile status` 改为输出 `runtime_context`，展示 `workspace`、`runtime_dir` 和是否使用显式数据目录。
- `setup-schedule` 生成的 crontab 只保留 `COW_WORKSPACE` 和可选 `FITNESS_COACH_DATA_DIR`，避免把已经废弃的身份变量写入计划任务。
- README、SKILL 和引用文档改为中文说明 workspace 隔离模型。

## 0.1.5 - 2026-06-01

- 根据 CowAgent 多实例 workspace 文档校正隔离说明：多实例首要使用独立 `COW_WORKSPACE`。
- `setup-schedule` 生成的 crontab 显式写入 `COW_WORKSPACE`，并保留当前用户/实例相关环境变量。
- `post_install_command` 改为 `version`，避免安装后自动创建 `users/default` 数据。
- 常用命令示例补充 `--user-id`，避免误写默认用户目录。

## 0.1.4 - 2026-06-01

- 首次使用流程增加“先确认数据隔离身份”的说明。
- `info` 和 `profile status` 输出当前隔离状态，包含 `user_id`、`instance_id`、`runtime_dir` 和是否使用 `users/default`。
- 文档明确：拿不到稳定用户 ID 时，应先提醒用户 default 目录可能被多人共用。

## 0.1.3 - 2026-06-01

- 增加用户/会话级数据隔离，支持 `--user-id` / `--profile-id` 和 `FITNESS_COACH_USER_ID`。
- 默认数据从实例目录进一步隔离到 `users/<user-id>`；未提供用户 ID 时使用 `users/default`。
- 补充“skill 不是服务，必须由 CowAgent 调用时传稳定用户标识”的说明。

## 0.1.2 - 2026-06-01

- 补充多 CowAgent 实例如何设置环境变量的说明。
- 在 README 和数据契约中补充 systemd、手动启动和验证命令。
- 版本同步到 `0.1.2`，方便用户通过 `check-update` 获取说明更新。

## 0.1.1 - 2026-06-01

- 增加多 CowAgent 实例数据隔离。
- 支持 `FITNESS_COACH_DATA_DIR` 显式指定数据目录。
- 支持 `FITNESS_COACH_INSTANCE_ID` / `COWAGENT_INSTANCE_ID` / `COW_AGENT_INSTANCE_ID` 将数据保存到独立实例目录。
- 补充 README、数据契约和示例配置中的多实例说明。

## 0.1.0 - 2026-06-01

- 初始化 CowAgent 健身饮食教练 skill。
- 增加首次建档、每日记录、上下文读取、每日缺失项追问。
- 增加导出、导入、备份、迁移、卸载和版本检查命令。
- 增加中文模板和规范文档。
- 增加 pytest 覆盖核心 CLI 行为。
