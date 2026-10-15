# -*- coding: utf-8 -*-
"""前后台数据同步与状态一致性 —— 对应手工用例 TC-SYNC-*"""

import pytest
from playwright.sync_api import expect

from pages import HomePage, ThoughtsPage


def test_tc_sync_01_profile_title_syncs_to_home(admin, page_logged_in, test_mark,
                                                restore_profile):
    """TC-SYNC-01：后台修改主页标题，前台刷新后应显示新标题"""
    new_title = f"{test_mark} 新标题"

    admin.update_profile(new_title)
    expect(admin.flash_success).to_have_text("个人主页已更新。")

    home = HomePage(page_logged_in).open()
    assert home.get_title() == new_title, "前台主页应该显示后台刚改的标题"


def test_tc_sync_03_deleted_post_disappears_from_frontend(admin, page_logged_in,
                                                          test_mark):
    """TC-SYNC-03：后台删除一条心理话，前台列表里也应该消失"""
    content = f"{test_mark} 前后台同步验证"

    admin.publish_thought(content)
    assert ThoughtsPage(page_logged_in).open().has_text(content)

    admin.open().delete_thought(content)
    assert not ThoughtsPage(page_logged_in).open().has_text(content), (
        "后台删掉的内容，前台不应该还看得到"
    )


@pytest.mark.xfail(
    reason="BUG-003 未修复：重复提交「发布」会写入重复记录（见缺陷报告 BUG-003）",
    strict=True,
)
def test_tc_sync_05_double_click_should_not_duplicate(admin, page_logged_in, test_mark):
    """
    TC-SYNC-05：快速连点「发布」3 次，应该只生成 1 条记录。

    这是数据一致性缺陷 —— 后端没有防重复提交，前端按钮也没禁用，
    连点几次就写几条。对一个记录双方心里话的小站来说，脏数据比排版错乱严重得多。

    实现说明：用「页面内并发发 3 个请求」来模拟连点。
    直接让 Playwright 连点按钮复现不出来 —— 第一次点击后页面立刻开始跳转，
    后两次会被浏览器丢掉。并发请求走的是同一个接口、同一个会话，才是这个缺陷的正确测法。
    """
    content = f"{test_mark} 连点测试"
    before = ThoughtsPage(page_logged_in).open().count()

    admin.publish_concurrently(content, times=3)

    added = ThoughtsPage(page_logged_in).open().count() - before
    assert added == 1, f"连点 3 次应只新增 1 条，实际新增 {added} 条"


def test_tc_sync_06_publish_then_refresh_keeps_single_record(admin, page_logged_in,
                                                             test_mark):
    """TC-SYNC-06：发布后立即刷新页面，数据不应重复、也不应丢失"""
    content = f"{test_mark} 发布后刷新"
    before = ThoughtsPage(page_logged_in).open().count()

    admin.open().publish_thought(content)
    page_logged_in.reload()
    page_logged_in.wait_for_load_state("networkidle")

    thoughts = ThoughtsPage(page_logged_in).open()
    assert thoughts.find(content).count() == 1, "刷新后应该正好只有 1 条"
    assert thoughts.count() == before + 1, "总数应该只增加 1 条"


def test_tc_func_07_count_is_conserved(admin, page_logged_in, test_mark):
    """TC-FUNC-07：发布一条再删掉，列表数量应回到操作前（数量守恒）"""
    before = ThoughtsPage(page_logged_in).open().count()
    content = f"{test_mark} 数量守恒验证"

    admin.open().publish_thought(content)
    assert ThoughtsPage(page_logged_in).open().count() == before + 1

    admin.open().delete_thought(content)
    assert ThoughtsPage(page_logged_in).open().count() == before
