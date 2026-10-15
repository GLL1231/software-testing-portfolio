# -*- coding: utf-8 -*-
"""
手动兜底清理脚本。

正常情况下，每条用例跑完都会自动清理自己造的测试数据
（见 conftest.py 里的 admin fixture）。

但如果测试被强行中断（Ctrl+C）、电脑突然关机，或者自动清理本身报错，
网站上可能残留带「【自动化测试】」前缀的垃圾内容。
这时运行这个脚本，一键清干净。

用法：
    cd C:\\AI文件夹\\自动化测试
    python tools/清理测试数据.py
"""

import sys
from pathlib import Path

# 让脚本能找到上层的 config / pages
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright  # noqa: E402

from config import BASE_URL, SITE_PASSWORD, TEST_PREFIX, url  # noqa: E402
from pages import AdminPage, LoginPage  # noqa: E402


def main() -> int:
    if not SITE_PASSWORD:
        print("❌ 没读到网站密码，请检查 .env 文件里的 SITE_PASSWORD。")
        return 1

    print(f"🧹 开始清理 {BASE_URL} 上的测试数据（前缀：{TEST_PREFIX}）")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.on("dialog", lambda dialog: dialog.accept())

        # 登录
        LoginPage(page).open().login_expect_success(SITE_PASSWORD, "男方")

        # 清理
        deleted = AdminPage(page).cleanup_test_data()

        context.close()
        browser.close()

    if deleted:
        print(f"✅ 清理完成，共删除 {deleted} 条测试数据。")
    else:
        print("✅ 没有发现残留的测试数据，网站是干净的。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
