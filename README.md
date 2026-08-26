# 机场自动签到

基于 SSPanel 面板的每日自动签到脚本，运行在 GitHub Actions 上，账号密码通过环境变量（Secrets）传入，不写死在代码中。

> 请注意：本项目仅用于技术学习（GitHub Actions 自动化），不讨论任何其他话题。

## 功能

- 每日自动登录 SSPanel 面板并签到领流量
- 支持多渠道通知推送（Server酱 / Telegram Bot）
- 全程环境变量传参，零硬编码
- 签到流程：GET 登录页建立会话 → POST 登录 → POST 签到

## 部署

1. Fork 此仓库

2. 到 `Settings` → `Secrets and variables` → `Actions` → `Repository secrets` 添加以下参数：

| 参数 | 是否必须 | 内容 | 示例 |
|------|----------|------|------|
| EMAIL | 是 | 注册机场所用邮箱 | a@example.com |
| PASSWORD | 是 | 注册机场所用密码 | password1 |
| BASE_URL | 是 | 机场面板地址（不带尾部 `/`） | https://go.runba.cyou |
| SCKEY | 否 | Server酱密钥 | SCTxxxxxxxxxxxxxx |
| TGBOT | 否 | Telegram Bot Token | 5xxxxxxx:xxxxxxxxx |
| TGUSERID | 否 | Telegram 用户 ID | 8xxxxxxxxx |

3. （可选）在 `Settings` → `Secrets and variables` → `Actions` → `Variables` 中添加变量 `SCHEDULED`，值为**北京时间 HHMM**，例如 `0503` 表示每天 05:03。不设置则使用代码里的默认值 `0503`。

   > 说明：GitHub Actions 不允许在 `on.schedule.cron` 中使用变量，所以工作流改为**每 5 分钟轮询一次**，到达 `SCHEDULED` 设定的时间才真正签到。改时间只需改这个变量（或改 `checkin.yml` 里的默认值），无需改 cron 表达式。

4. 转到 `Actions` 页面，手动触发一次 `Airport Checkin` 工作流以验证配置。之后每天到达设定时间会自动执行。

5. 可在 Actions 的 Run 日志中查看签到结果，同时如果配置了 SCKEY 或 TGBOT，也会收到推送通知。

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量后运行
export EMAIL="你的邮箱"
export PASSWORD="你的密码"
export BASE_URL="https://go.runba.cyou"
python3 main.py
```

## 工作流说明

| 步骤 | 作用 |
|------|------|
| GET /auth/login | 建立会话 cookie，SSPanel 会校验会话 |
| POST /auth/login | 提交邮箱密码登录，校验返回 ret==1 |
| POST /user/checkin | 执行签到，ret==1 为成功，其他视为今日已签到 |
| 通知推送 | 可选，通过 Server酱或 Telegram 推送签到结果 |

## 定时是怎么工作的

`checkin.yml` 里的 cron 固定为 `*/5 * * * *`（每 5 分钟），真正的执行时机由变量 `SCHEDULED` 控制：

- 工作流每 5 分钟启动一次，先比对「当前北京时间」与 `SCHEDULED`
- 没到时间 → 直接跳过（约 1 秒结束）
- 到了时间且今天还没签过 → 执行签到，并写入 `.signed_date` 标记防止当天重复
- 手动触发（`workflow_dispatch`）不受时间限制，总是执行

这样做的好处：改时间只改一个变量，且对 GitHub 定时延迟不敏感（即使某次轮询被延后，后续轮询仍会在当天补上）。代价是 Actions 列表里会有较多「跳过」记录。

## 参考

- [zhjc1124/ssr_autocheckin](https://github.com/zhjc1124/ssr_autocheckin) — 原始机场签到代码
- [sirodeneko/genshin-sign](https://github.com/sirodeneko/genshin-sign) — Actions 工作流参考
