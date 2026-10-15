# -*- coding: utf-8 -*-
"""
Page Object Model（POM）—— 每个页面一个类，把「页面上有哪些元素、能做哪些操作」封装起来。

好处：测试用例里写的是「登录页.登录(密码)」这种人话，
      而不是一堆 CSS 选择器。页面改版时只需要改这里，测试用例不用动。
"""

from pages.admin_page import AdminPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.photos_page import PhotosPage
from pages.thoughts_page import ThoughtsPage

__all__ = ["AdminPage", "HomePage", "LoginPage", "PhotosPage", "ThoughtsPage"]
