# 版本检查与更新策略

## 检查更新

```bash
python scripts/fitness_coach.py check-update
```

脚本会读取 `config.json` 的 `version_check_url`，解析远端 `SKILL.md` 中的 `version:`，并写入 `data/update_state.json`。

## 用户选择

- 更新：先运行 `prepare-update --target-version <version>`，再执行 CowAgent skill 更新流程，最后运行 `post-update-check`。
- 跳过：运行 `skip-version --version <version>`，后续不再提示该版本。
- 取消跳过：运行 `clear-skipped-version --version <version>`。
- 稍后提醒：不写入跳过列表，只保留最近检查状态。

## 安全要求

- 版本检查失败必须明确报错，不能假装已是最新。
- 更新前必须备份真实数据。
- 跳过某个版本后，只在出现更高版本时再次提示。
- `info` 应展示当前版本、远端版本、最近检查时间和已跳过版本。
