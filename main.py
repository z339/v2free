"""
SSPanel 机场自动签到脚本（适配 GitHub Actions）

流程（与 runba-checkin 一致）:
  1. GET 登录页 → 建立会话 cookie
  2. POST /auth/login → 登录（校验 ret==1）
  3. POST /user/checkin → 签到
  4. 可选：通过 Server酱 / Telegram 推送结果

环境变量:
  EMAIL      — 登录邮箱（必须）
  PASSWORD   — 登录密码（必须）
  BASE_URL   — 面板地址，如 https://go.runba.cyou（必须）
  SCKEY      — Server酱密钥（可选）
  TGBOT      — Telegram Bot Token（可选）
  TGUSERID   — Telegram 用户 ID（可选）
"""

import os
import sys
from datetime import datetime

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0 Safari/537.36"
)


def log(msg):
    """带时间戳的日志输出"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def checkin(email, password, base_url):
    """执行签到，返回签到结果消息字符串。"""
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    session.verify = False

    # ---------- 1. 建立会话（GET 登录页拿 cookie）----------
    log(f"访问 {base_url}/auth/login 建立会话…")
    resp = session.get(f"{base_url}/auth/login", timeout=30)
    resp.raise_for_status()

    # ---------- 2. 登录 ----------
    log("正在登录…")
    login_data = {
        "email": email,
        "passwd": password,
        "code": "",
        "remember_me": "on",
    }
    resp = session.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={
            "Referer": f"{base_url}/auth/login",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30,
    )
    login_result = resp.json()
    login_ret = login_result.get("ret", -1)
    login_msg = login_result.get("msg", "")

    if login_ret != 1:
        raise RuntimeError(f"登录失败: {login_msg or resp.text}")

    log(f"登录成功: {login_msg or 'OK'}")

    # ---------- 3. 签到 ----------
    log("正在签到…")
    resp = session.post(
        f"{base_url}/user/checkin",
        headers={
            "Referer": f"{base_url}/user",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30,
    )
    checkin_result = resp.json()
    checkin_ret = checkin_result.get("ret", -1)
    checkin_msg = checkin_result.get("msg", "")

    if checkin_ret == 1:
        log(f"签到成功: {checkin_msg or 'OK'}")
    else:
        # ret != 1 常见于「今天已经签到过了」，视为非致命
        log(f"签到未成功（可能今日已签到）: {checkin_msg or resp.text}")

    return checkin_msg or "签到完成"


def send_serverchan(sckey, title, desp):
    """通过 Server酱 推送通知"""
    url = f"https://sctapi.ftqq.com/{sckey}.send"
    r = requests.get(url, params={"title": title, "desp": desp}, timeout=15)
    if r.status_code == 200:
        log("Server酱推送成功")
    else:
        log(f"Server酱推送失败: HTTP {r.status_code}")


def send_telegram(bot_token, user_id, text):
    """通过 Telegram Bot 推送通知"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    r = requests.get(
        url,
        params={
            "chat_id": user_id,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    if r.status_code == 200:
        log("Telegram 推送成功")
    else:
        log(f"Telegram 推送失败: HTTP {r.status_code}")


def main():
    email = os.environ.get("EMAIL", "")
    password = os.environ.get("PASSWORD", "")
    base_url = os.environ.get("BASE_URL", "")
    sckey = os.environ.get("SCKEY", "")
    tg_bot_token = os.environ.get("TGBOT", "")
    tg_user_id = os.environ.get("TGUSERID", "")

    if not email or not password or not base_url:
        log("错误: 缺少必须的环境变量 EMAIL / PASSWORD / BASE_URL")
        sys.exit(1)

    base_url = base_url.rstrip("/")

    try:
        result = checkin(email, password, base_url)
    except Exception as e:
        result = f"签到异常: {e}"
        log(result)
        if sckey:
            send_serverchan(sckey, "机场签到异常", result)
        if tg_bot_token and tg_user_id:
            send_telegram(tg_bot_token, tg_user_id, result)
        sys.exit(1)

    # ---------- 4. 推送通知 ----------
    if sckey:
        send_serverchan(sckey, "机场签到", result)
    if tg_bot_token and tg_user_id:
        send_telegram(tg_bot_token, tg_user_id, result)

    log("全部流程结束")


if __name__ == "__main__":
    main()
