# -*- coding: utf-8 -*-
"""照片相册页 /photos"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class PhotosPage(BasePage):
    PATH = "photos"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_title = page.locator("h1.page-title")
        self.photo_cards = page.locator(".gallery .photo-card")
        self.images = page.locator(".photo-card img")
        self.empty_hint = page.locator("p.empty")

    def count(self) -> int:
        return self.photo_cards.count()

    def find(self, caption: str):
        """找到说明文字包含 caption 的那张照片"""
        return self.photo_cards.filter(has_text=caption)

    def has_caption(self, caption: str) -> bool:
        return self.find(caption).count() > 0

    def all_broken_images(self) -> list:
        """检查相册里有没有「加载失败」的图片（naturalWidth 为 0 就是没加载出来）"""
        return self.page.evaluate(
            """() => Array.from(document.querySelectorAll('.photo-card img'))
                     .filter(img => img.naturalWidth === 0)
                     .map(img => img.getAttribute('src'))"""
        )
