# -*- coding: utf-8 -*-
"""登录功能 —— 对应手工测试用例 TC-LOGIN-01 / 05 / 06 / 09"""

from playwright.sync_api import expect

from config import SITE_PASSWORD, url
from pages import HomePage, LoginPage


def test_tc_login_01_wrong_password_cannot_login(page_anonymous):
    """TC-LOGIN-01：输入错误密码「1」，应被拒绝并提示「密码不对，再试一次。」"""
    login = LoginPage(page_anonymous).open()
    login.login("1", "男方")
    login.wait_for_login_failed()

    expect(page_anonymous).to_have_url(url("login"))
    expect(login.flash_error).to_have_text("密码不对，再试一次。")
    assert not login.has_navbar(), "登录失败时不应该出现顶部导航栏"


def test_tc_login_05_login_success_as_male(page_anonymous):
    """TC-LOGIN-05：正确密码 + 男方身份，应登录成功并显示「我是男方」"""
    login = LoginPage(page_anonymous).open()
    login.login_expect_success(SITE_PASSWORD, "男方")

    home = HomePage(page_anonymous)
    assert home.has_navbar(), "登录成功后应该出现顶部导航栏"
    expect(home.whoami).to_have_text("我是男方")


def test_tc_login_06_login_success_as_female(page_anonymous):
    """TC-LOGIN-06：正确密码 + 女方身份，应登录成功并显示「我是女方」"""
    login = LoginPage(page_anonymous).open()
    login.login_expect_success(SITE_PASSWORD, "女方")

    home = HomePage(page_anonymous)
    assert home.has_navbar(), "登录成功后应该出现顶部导航栏"
    expect(home.whoami).to_have_text("我是女方")


def test_tc_login_09_empty_password_blocked(page_anonymous):
    """TC-LOGIN-09：密码留空直接提交，应被必填校验拦下，停留登录页"""
    login = LoginPage(page_anonymous).open()
    login.submit_as("男方")
    page_anonymous.wait_for_timeout(800)

    expect(page_anonymous).to_have_url(url("login"))
    assert not login.has_navbar(), "没登录成功就不该出现导航栏"


def test_visiting_admin_without_login_redirects(page_anonymous):
    """未登录直接访问后台 /admin，应被重定向到登录页"""
    page_anonymous.goto(url("admin"))
    expect(page_anonymous).to_have_url(url("login"))


def test_logged_in_user_cannot_see_login_page(page_logged_in):
    """已登录时再访问 /login，应被自动跳回主页"""
    page_logged_in.goto(url("login"))
    expect(page_logged_in).to_have_url(url())


def test_logout_clears_session(page_logged_in):
    """点「退出」后应回到登录页，且导航栏消失（登录态已清除）"""
    home = HomePage(page_logged_in).open()
    home.click_nav("退出")

    expect(page_logged_in).to_have_url(url("login"))
    assert not home.has_navbar(), "退出后导航栏应该消失"
