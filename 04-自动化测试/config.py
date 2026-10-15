# -*- coding: utf-8 -*-
"""
项目配置。

敏感信息（网站密码）不写死在代码里 —— 从同目录的 .env 文件读取。
.env 已被 .gitignore 忽略，不会上传到 GitHub。
新人拿到这个项目，照着 .env.example 建一个 .env 填上自己的密码就能跑。
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录
ROOT = Path(__file__).parent

# 读取 .env（不存在也不报错，用下面的默认值）
load_dotenv(ROOT / ".env")

# ---------------------------------------------------------------------------
# 被测网站地址
#   本地：http://127.0.0.1:5000        （默认，跑得快、可反复跑）
#   线上：https://gll.pythonanywhere.com
# 改 .env 里的 BASE_URL 即可切换
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/") + "/"

# 网站登录密码（必填，从 .env 读）
SITE_PASSWORD = os.getenv("SITE_PASSWORD", "")

# ---------------------------------------------------------------------------
# 测试数据统一前缀
#   所有自动化测试创建的内容都带这个前缀，跑完自动删掉，
#   保证不污染网站的真实内容。详见 conftest.py 的 cleanup fixture。
# ---------------------------------------------------------------------------
TEST_PREFIX = "【自动化测试】"

# 失败截图存放目录
SCREENSHOT_DIR = ROOT / "截图"


def url(path=""):
    """拼完整网址。url('login') -> http://127.0.0.1:5000/login"""
    return BASE_URL + path.lstrip("/")
