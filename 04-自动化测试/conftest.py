# -*- coding: utf-8 -*-
"""
pytest 全局配置与夹具（fixture）。

夹具就是「用例开跑前先准备好的东西」和「用例跑完要收尾的事」。
这里准备了 4 样：

  1. browser         —— 浏览器（pytest-playwright 插件自带，session 级，全程只开一次）
  2. auth_state      —— 登录状态。真登录一次就存下来，所有用例复用，不用每条都登录
  3. page_logged_in  —— 一个「已经登录好」的浏览器页面，用例直接拿来用
  4. admin           —— 后台页面对象，用完自动清理测试数据

另外还做了两件事：
  * 每条用例开始前检查网站是否可访问，连不上就给中文提示（而不是一堆看不懂的报错）
  * 用例失败时自动截图
"""

import sys
import urllib.request
from pathlib import Path
from uuid import uuid4

import pytest

# 让 pytest 能找到同目录下的 config / pages
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config import (  # noqa: E402
    BASE_URL,
    SCREENSHOT_DIR,
    SITE_PASSWORD,
    TEST_PREFIX,
    url,
)
from pages import AdminPage  # noqa: E402


# ===========================================================================
# 钩子：把每条用例的执行结果挂到用例对象上，供「失败截图」使用
# ===========================================================================
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report


# ===========================================================================
# 夹具：开跑前检查网站通不通
# ===========================================================================
@pytest.fixture(scope="session", autouse=True)
def check_site_available():
    """连不上网站就直接停下，并告诉用户该怎么办 —— 比抛一堆英文报错友好得多。"""
    try:
        urllib.request.urlopen(BASE_URL, timeout=10)
    except Exception as exc:
        pytest.exit(
            f"\n\n❌ 连不上被测网站：{BASE_URL}\n"
            f"   原因：{exc}\n\n"
            f"   如果测的是本地网站，请先启动它：\n"
            f"     双击运行  C:\\AI文件夹\\my-website\\启动网站.bat\n"
            f"     或者在  my-website  目录下执行  python flask_app.py\n\n"
            f"   如果测的是线上网站，请检查 .env 里的 BASE_URL 和网络连接。\n",
            returncode=1,
        )


# ===========================================================================
# 夹具：登录状态（session 级 —— 整个测试只登录一次）
# ===========================================================================
@pytest.fixture(scope="session")
def auth_state(browser):
    """
    真登录一次，把浏览器的登录状态（cookie）保存下来给所有用例复用。

    为什么要先真登录一次？因为 Flask 的 session cookie 是签名过的，
    没法手写伪造，只能老老实实登录一次再存下来。
    """
    if not SITE_PASSWORD:
        pytest.exit(
            "\n\n❌ 没有读到网站密码。\n"
            "   请把 .env.example 复制成 .env，并填上 SITE_PASSWORD。\n",
            returncode=1,
        )

    context = browser.new_context()
    page = context.new_page()
    page.goto(url("login"), wait_until="domcontentloaded", timeout=60000)
    page.fill('input[name="password"]', SITE_PASSWORD)
    page.click("button.btn-male")
    page.wait_for_url(url(), timeout=30000)

    state = context.storage_state()
    context.close()
    return state


# ===========================================================================
# 夹具：已登录的页面 / 未登录的页面
# ===========================================================================
def _new_page(browser, storage_state=None):
    context = browser.new_context(storage_state=storage_state)
    page = context.new_page()
    page.set_default_timeout(15000)
    # 后台的删除操作会弹 confirm 确认框。Playwright 默认会自动点「取消」，
    # 那样表单根本不会提交，而且不报错 —— 必须显式改成自动点「确定」。
    page.on("dialog", lambda dialog: dialog.accept())
    return context, page


@pytest.fixture
def page_logged_in(browser, auth_state, request):
    """一个已登录的页面。每条用例一个独立的浏览器上下文，互不干扰。"""
    context, page = _new_page(browser, auth_state)
    yield page

    # 用例失败时自动截图，方便排查
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        try:
            page.screenshot(
                path=str(SCREENSHOT_DIR / f"{request.node.name}.png"),
                full_page=True,
            )
        except Exception:
            pass

    context.close()


@pytest.fixture
def page_anonymous(browser):
    """一个未登录的页面（用来测「没登录会怎样」）。"""
    context, page = _new_page(browser)
    yield page
    context.close()


# ===========================================================================
# 夹具：测试数据标记 + 后台页面对象（用完自动清理）
# ===========================================================================
@pytest.fixture
def test_mark():
    """
    每条用例一个唯一的数据标记。

    测试造的内容都带上它，好处：
      1. 断言只依赖自己造的数据，不受网站已有真实内容影响
      2. 跑完能精确地只删掉自己造的，不误伤真实数据
    """
    return f"{TEST_PREFIX}{uuid4().hex[:6]}"


@pytest.fixture
def admin(page_logged_in):
    """
    后台页面对象。

    用完自动清理 —— 这个 yield 之后的代码**即使用例失败也会执行**，
    所以不会在网站上留下测试垃圾。
    """
    page = AdminPage(page_logged_in)
    page.open()
    yield page

    try:
        deleted = page.cleanup_test_data()
        if deleted:
            print(f"\n🧹 已自动清理 {deleted} 条测试数据")
    except Exception as exc:  # noqa: BLE001
        print(
            f"\n⚠️ 自动清理失败：{exc}\n"
            f"   可手动运行 tools/清理测试数据.py 兜底清理"
        )


@pytest.fixture(scope="session")
def test_image(tmp_path_factory):
    """
    生成一张测试用的小图片。

    刻意不把二进制图片放进仓库 —— 用代码现场生成，谁 clone 下来都能跑，
    也不会因为在不同系统上传二进制文件产生差异。
    """
    path = tmp_path_factory.mktemp("素材") / "测试图片.png"
    _write_png(path, width=240, height=160, rgb=(90, 140, 200))
    return path


def _write_png(path: Path, width: int = 240, height: int = 160, rgb=(90, 140, 200)):
    """用纯 Python 写一张纯色 PNG（只用标准库 zlib / struct）"""
    import struct
    import zlib

    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


@pytest.fixture
def restore_profile(admin):
    """
    保存当前主页标题/介绍，用例跑完自动恢复。

    避免「测数据同步」时把用户真实的主页内容改掉还回不去。
    """
    original_title = admin.get_profile_title()
    original_intro = admin.get_profile_intro()
    yield
    # 用例跑完时页面可能已经被导航到别处了，先回后台再改回去
    admin.open()
    admin.update_profile(original_title, original_intro)
