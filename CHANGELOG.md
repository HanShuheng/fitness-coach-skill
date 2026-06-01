# 更新日志

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
