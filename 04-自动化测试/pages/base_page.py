# -*- coding: utf-8 -*-
"""所有页面的父类 —— 放每个页面都有的公共部分（顶部导航栏、flash 提示等）。"""

from playwright.sync_api import Page

from config import url


class BasePage:
    """页面基类。子类只要定义 PATH，就能用这里的方法。"""

    # 子类覆盖：这个页面对应的相对路径，例如 "login"
    PATH = ""

    def __init__(self, page: Page):
        self.page = page

        # ---- 顶部导航栏（只有登录后才会渲染出来）----
        self.nav_home = page.locator('nav a:has-text("主页")')
        self.nav_thoughts = page.locator('nav a:has-text("心理话")')  # 注意：是「心理话」
        self.nav_photos = page.locator('nav a:has-text("照片")')
        self.nav_admin = page.locator('nav a:has-text("后台")')
        self.nav_logout = page.locator('nav a:has-text("退出")')
        self.nav_brand = page.locator("a.brand")

        # 导航栏右上角显示的身份：「我是男方」/「我是女方」
        self.whoami = page.locator("span.whoami")

        # ---- flash 提示消息（一次性，刷新就没了，断言要紧接着操作）----
        self.flash_success = page.locator("div.flash.flash-ok")
        self.flash_error = page.locator("div.flash.flash-error")

    # ------------------------------------------------------------------
    # 基础操作
    # ------------------------------------------------------------------
    def open(self):
        """打开这个页面"""
        self.page.goto(url(self.PATH))
        return self

    def click_nav(self, name: str):
        """点击顶部导航。name 可选：主页 / 心理话 / 照片 / 后台 / 退出"""
        self.page.click(f'nav a:has-text("{name}")')

    def has_navbar(self) -> bool:
        """当前页面有没有顶部导航栏（用来判断是否已登录）"""
        return self.nav_brand.count() > 0

    def has_horizontal_overflow(self) -> bool:
        """
        页面是否横向溢出（有横向滚动条）。

        这是把「排版对不对」这种主观判断，变成可断言的客观指标 ——
        用来复现 BUG-001（超长字符撑破排版）。
        """
        return self.page.evaluate(
            "() => document.documentElement.scrollWidth > "
            "document.documentElement.clientWidth"
        )
