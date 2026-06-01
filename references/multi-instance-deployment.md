# 多 CowAgent 实例数据隔离部署说明

如果一台服务器只运行一个 CowAgent，不需要额外配置。本 skill 默认把数据保存到：

```text
$COW_WORKSPACE/fitness_coach/
```

如果一台服务器运行多个 CowAgent，就必须给每个实例设置不同的环境变量，否则它们可能共用同一份 `profile.md`、每日记录、备份和导出数据。

## 你要设置哪个变量

推荐设置：

```bash
FITNESS_COACH_INSTANCE_ID
```

例如：

```bash
FITNESS_COACH_INSTANCE_ID=wxbot-main
```

这个实例的数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/instances/wxbot-main/
```

另一个实例如果设置：

```bash
FITNESS_COACH_INSTANCE_ID=wxbot-test
```

它的数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/instances/wxbot-test/
```

这样两个 CowAgent 就不会共用同一套健身数据。

## systemd 启动方式

多数服务器上的 CowAgent 是 systemd 服务。先看服务名：

```bash
systemctl list-units --type=service | grep -i cow
```

假设主实例服务名是 `cowagent.service`，运行：

```bash
sudo systemctl edit cowagent.service
```

填入：

```ini
[Service]
Environment=FITNESS_COACH_INSTANCE_ID=wxbot-main
```

保存后重载并重启：

```bash
sudo systemctl daemon-reload
sudo systemctl restart cowagent.service
```

如果还有测试实例，例如服务名是 `cowagent-test.service`：

```bash
sudo systemctl edit cowagent-test.service
```

填入：

```ini
[Service]
Environment=FITNESS_COACH_INSTANCE_ID=wxbot-test
```

然后：

```bash
sudo systemctl daemon-reload
sudo systemctl restart cowagent-test.service
```

## 手动启动方式

如果你是手动启动 CowAgent：

```bash
FITNESS_COACH_INSTANCE_ID=wxbot-main cow start
```

或者先 export：

```bash
export FITNESS_COACH_INSTANCE_ID=wxbot-main
cow start
```

另一个实例换成另一个 ID：

```bash
FITNESS_COACH_INSTANCE_ID=wxbot-test cow start
```

## 完全指定数据目录

如果你希望把数据放到明确的数据盘或备份目录，使用：

```bash
FITNESS_COACH_DATA_DIR=/data/cowagent/wxbot-main/fitness_coach
```

systemd 写法：

```ini
[Service]
Environment=FITNESS_COACH_DATA_DIR=/data/cowagent/wxbot-main/fitness_coach
```

`FITNESS_COACH_DATA_DIR` 优先级最高。设置了它以后，`FITNESS_COACH_INSTANCE_ID` 会被忽略。

## 验证是否生效

进入 skill 目录后运行：

```bash
python scripts/fitness_coach.py info
```

看输出中的 `runtime_dir`。

主实例应该类似：

```text
/root/cow/fitness_coach/instances/wxbot-main
```

测试实例应该类似：

```text
/root/cow/fitness_coach/instances/wxbot-test
```

如果两个实例输出同一个 `runtime_dir`，说明还没有隔离成功。

## 已有数据怎么办

如果之前已经在默认目录产生了数据：

```text
$COW_WORKSPACE/fitness_coach/
```

建议先导出：

```bash
python scripts/fitness_coach.py export --format zip
```

再给目标实例设置环境变量，重启 CowAgent，然后导入：

```bash
python scripts/fitness_coach.py import --from <export.zip>
```

确认新实例的 `runtime_dir` 正确后，再决定是否清理旧目录。

## 变量优先级

```text
FITNESS_COACH_DATA_DIR
> FITNESS_COACH_INSTANCE_ID / COWAGENT_INSTANCE_ID / COW_AGENT_INSTANCE_ID
> $COW_WORKSPACE/fitness_coach
```

普通多实例部署，用 `FITNESS_COACH_INSTANCE_ID` 就够了；需要指定数据盘时，再用 `FITNESS_COACH_DATA_DIR`。
