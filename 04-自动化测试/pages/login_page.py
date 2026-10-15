# -*- coding: utf-8 -*-
"""登录页 /login"""

from playwright.sync_api import Page

from config import url
from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "login"

    def __init__(self, page: Page):
        super().__init__(page)
        # 页面上只有一个输入框，没有用户名 —— 唯一的 input 就是密码框
        self.password_input = page.locator('input[name="password"]')
        # 「身份」不是单选框，而是两个提交按钮的 value
        self.male_button = page.locator("button.btn-male")
        self.female_button = page.locator("button.btn-female")

    def fill_password(self, password: str):
        self.password_input.fill(password)
        return self

    def submit_as(self, role: str = "男方"):
        """点对应身份的按钮提交"""
        if role == "男方":
            self.male_button.click()
        else:
            self.female_button.click()
        return self

    def login(self, password: str, role: str = "男方"):
        """填密码 + 选身份 + 提交（不校验结果）"""
        self.fill_password(password)
        self.submit_as(role)
        return self

    def login_expect_success(self, password: str, role: str = "男方"):
        """登录并等待跳转到主页（登录成功时的用法）"""
        self.login(password, role)
        self.page.wait_for_url(url())
        return self

    def wait_for_login_failed(self):
        """登录失败时的等待：页面不跳转，停在 /login"""
        self.page.wait_for_load_state("networkidle")
        return self
