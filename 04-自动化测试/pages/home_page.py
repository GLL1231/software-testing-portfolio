# -*- coding: utf-8 -*-
"""主页 /"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = ""

    def __init__(self, page: Page):
        super().__init__(page)
        # 大标题没有单独的 class，用 .hero 容器限定
        self.title = page.locator(".hero h1")
        self.intro = page.locator("p.intro")

    def get_title(self) -> str:
        return (self.title.inner_text() or "").strip()

    def get_intro(self) -> str:
        return (self.intro.inner_text() or "").strip()
