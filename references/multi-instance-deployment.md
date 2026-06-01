# 多 CowAgent 实例数据隔离部署说明

重要：本项目是 CowAgent skill，不是常驻服务。skill 代码可以被多个 CowAgent 或多个用户共用；真正区分数据的是“调用脚本时传入的环境变量或参数”。

如果不传用户标识，默认数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/users/default/
```

这意味着：多个用户都不传 `--user-id` 时，会共用 `default` 这套数据。

## 第一层：区分用户或会话

每次调用脚本时，推荐传稳定用户 ID：

```bash
python scripts/fitness_coach.py --user-id wx-user-001 profile status
python scripts/fitness_coach.py --user-id wx-user-001 record --payload-json '{"body":{"weight_kg":70}}'
```

这个用户的数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/users/wx-user-001/
```

另一个用户：

```bash
python scripts/fitness_coach.py --user-id wx-user-002 profile status
```

会保存到：

```text
$COW_WORKSPACE/fitness_coach/users/wx-user-002/
```

如果 CowAgent 能提供会话或接收人 ID，也可以设置环境变量：

```bash
export FITNESS_COACH_USER_ID=wx-user-001
```

支持的用户变量优先级：

```text
--user-id / --profile-id
FITNESS_COACH_USER_ID
COW_USER_ID
COW_SESSION_ID
COW_NOTIFY_SESSION_ID
```

## 第二层：区分 CowAgent 实例

如果一台服务器运行多个 CowAgent，还要给每个实例设置不同的环境变量，否则不同 CowAgent 实例可能共用同一个 `users/` 根目录。

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
$COW_WORKSPACE/fitness_coach/instances/wxbot-main/users/<user-id>/
```

另一个实例如果设置：

```bash
FITNESS_COACH_INSTANCE_ID=wxbot-test
```

它的数据会保存到：

```text
$COW_WORKSPACE/fitness_coach/instances/wxbot-test/users/<user-id>/
```

这样两个 CowAgent 实例不会共用同一个用户数据根目录；同一个实例内的不同用户再由 `--user-id` 区分。

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

主实例某个用户应该类似：

```text
/root/cow/fitness_coach/instances/wxbot-main/users/wx-user-001
```

测试实例某个用户应该类似：

```text
/root/cow/fitness_coach/instances/wxbot-test/users/wx-user-001
```

如果两个不同用户或不同实例输出同一个 `runtime_dir`，说明还没有隔离成功。

## 已有数据怎么办

如果之前已经在默认目录产生了数据：

```text
$COW_WORKSPACE/fitness_coach/users/default/
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
> --user-id / FITNESS_COACH_USER_ID / COW_USER_ID / COW_SESSION_ID / COW_NOTIFY_SESSION_ID
> $COW_WORKSPACE/fitness_coach/users/default
```

普通多实例部署，用 `FITNESS_COACH_INSTANCE_ID` 就够了；需要指定数据盘时，再用 `FITNESS_COACH_DATA_DIR`。
