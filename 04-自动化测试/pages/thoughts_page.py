# -*- coding: utf-8 -*-
"""心理话列表页 /thoughts

注意：网站代码里写的是「心**理**话」，不是「心里话」。用错字会永远匹配不到元素。
"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class ThoughtsPage(BasePage):
    PATH = "thoughts"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_title = page.locator("h1.page-title")
        self.post_cards = page.locator("div.posts article.post-card")
        self.contents = page.locator(".post-card .post-content")
        self.empty_hint = page.locator("p.empty")

    def count(self) -> int:
        """当前列表上有多少条心理话"""
        return self.post_cards.count()

    def all_contents(self) -> list:
        """按页面显示顺序，取出所有心理话的正文"""
        return [t.strip() for t in self.contents.all_inner_texts()]

    def find(self, text: str):
        """找到正文包含 text 的那一条（返回 Locator，找不到时 count() 为 0）"""
        return self.post_cards.filter(has_text=text)

    def has_text(self, text: str) -> bool:
        return self.find(text).count() > 0
