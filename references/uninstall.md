# 卸载说明

卸载 skill 代码不会自动删除 `~/cow/fitness_coach/` 用户数据。推荐先导出，再移除提醒，最后删除代码。

## 推荐流程

```bash
python scripts/fitness_coach.py export --format zip
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

然后使用 CowAgent 的 skill uninstall/remove 命令删除 skill 代码。

## 只停用提醒

```bash
python scripts/fitness_coach.py uninstall --remove-schedules --yes
```

这只移除包含 `fitness_coach.py` 的 crontab 任务，不删除数据。

## 彻底删除数据

```bash
python scripts/fitness_coach.py uninstall --remove-data --yes
```

该命令会先自动导出 zip，再删除 `~/cow/fitness_coach/`。执行前请确认导出路径存在。

## 恢复

重新安装 skill 后运行：

```bash
python scripts/fitness_coach.py import --from <zip>
```

## 检查残留

```bash
python scripts/fitness_coach.py info
crontab -l | grep fitness_coach.py
```
