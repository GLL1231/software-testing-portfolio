# -*- coding: utf-8 -*-
"""界面与兼容性 —— 对应手工用例 TC-UI-*"""

from playwright.sync_api import expect

from config import url
from pages import HomePage, PhotosPage, ThoughtsPage


def test_tc_ui_02_mobile_viewport_no_horizontal_scroll(page_logged_in):
    """TC-UI-02：用手机尺寸（375×667）打开，应自适应屏宽，无横向滚动"""
    page_logged_in.set_viewport_size({"width": 375, "height": 667})

    for 页面 in (HomePage(page_logged_in), ThoughtsPage(page_logged_in),
                 PhotosPage(page_logged_in)):
        页面.open()
        assert not 页面.has_horizontal_overflow(), (
            f"{页面.__class__.__name__} 在手机尺寸下出现了横向滚动"
        )


def test_tc_ui_03_zoom_80_percent(page_logged_in):
    """TC-UI-03：浏览器缩放到 80%，排版应正常、无横向溢出"""
    page_logged_in.set_viewport_size({"width": 1280, "height": 800})
    HomePage(page_logged_in).open()
    page_logged_in.evaluate("document.body.style.zoom = '80%'")

    assert not HomePage(page_logged_in).has_horizontal_overflow()


def test_tc_ui_04_zoom_150_percent(page_logged_in):
    """TC-UI-04：浏览器缩放到 150%，排版应正常、无横向溢出"""
    page_logged_in.set_viewport_size({"width": 1280, "height": 800})
    HomePage(page_logged_in).open()
    page_logged_in.evaluate("document.body.style.zoom = '150%'")

    assert not HomePage(page_logged_in).has_horizontal_overflow()


def test_tc_ui_05_narrow_window(page_logged_in):
    """TC-UI-05：把窗口缩到最窄（320px），排版不应错位或横向溢出"""
    page_logged_in.set_viewport_size({"width": 320, "height": 800})

    for 页面 in (HomePage(page_logged_in), ThoughtsPage(page_logged_in)):
        页面.open()
        assert not 页面.has_horizontal_overflow(), "窗口最窄时出现了横向溢出"


def test_tc_ui_06_nav_menu_switches_pages(page_logged_in):
    """TC-UI-06：依次点击顶部导航各菜单，都应跳转到正确的页面"""
    home = HomePage(page_logged_in).open()

    home.click_nav("心理话")
    expect(page_logged_in).to_have_url(url("thoughts"))
    expect(page_logged_in.locator("h1.page-title")).to_have_text("心理话")

    home.click_nav("照片")
    expect(page_logged_in).to_have_url(url("photos"))
    expect(page_logged_in.locator("h1.page-title")).to_have_text("照片")

    home.click_nav("后台")
    expect(page_logged_in).to_have_url(url("admin"))

    home.click_nav("主页")
    expect(page_logged_in).to_have_url(url())
