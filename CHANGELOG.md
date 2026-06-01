# 更新日志

## 0.1.3 - 2026-06-01

- 增加用户/会话级数据隔离，支持 `--user-id` / `--profile-id` 和 `FITNESS_COACH_USER_ID`。
- 默认数据从实例目录进一步隔离到 `users/<user-id>`；未提供用户 ID 时使用 `users/default`。
- 补充“skill 不是服务，必须由 CowAgent 调用时传稳定用户标识”的说明。

## 0.1.2 - 2026-06-01

- 新增 `references/multi-instance-deployment.md`，说明多 CowAgent 实例如何设置环境变量。
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
