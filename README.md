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

3. 转到 `Actions` 页面，手动触发一次 `Airport Checkin` 工作流以验证配置。之后每天北京时间 06:00 会自动执行。

4. 可在 Actions 的 Run 日志中查看签到结果，同时如果配置了 SCKEY 或 TGBOT，也会收到推送通知。

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

## 参考

- [zhjc1124/ssr_autocheckin](https://github.com/zhjc1124/ssr_autocheckin) — 原始机场签到代码
- [sirodeneko/genshin-sign](https://github.com/sirodeneko/genshin-sign) — Actions 工作流参考
