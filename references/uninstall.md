# 卸载说明

卸载 skill 代码不会自动删除用户数据。默认数据在 `$COW_WORKSPACE/fitness_coach/`；如果配置了 `FITNESS_COACH_DATA_DIR`，请先用同一组环境变量运行 `info` 确认实际目录。

## 推荐卸载顺序

1. 导出数据：

   ```bash
   python scripts/fitness_coach.py export --format zip
   ```

2. 移除每日提醒：

   ```bash
   python scripts/fitness_coach.py uninstall --remove-schedules --yes
   ```

3. 使用 CowAgent 的 skill uninstall/remove 命令删除 skill 代码。

## 只停用提醒但保留 skill

```bash
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

这不会删除 `$COW_WORKSPACE/fitness_coach/`。

## 彻底删除数据

删除前先确认 `export` 生成的 zip 路径已经存在：

```bash
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py uninstall --remove-data --yes
```

`--remove-data --yes` 会先自动导出，再删除当前运行目录。

## 恢复

重新安装 skill 后运行：

```bash
python scripts/fitness_coach.py import --from <export.zip>
```

## 检查残留

```bash
python scripts/fitness_coach.py info
crontab -l | grep fitness_coach.py
ls "$COW_WORKSPACE/fitness_coach"
ls "$COW_WORKSPACE/scheduler"
```

如果曾使用 `FITNESS_COACH_DATA_DIR`，检查那个目录，而不是 `$COW_WORKSPACE/fitness_coach`。
