# -*- coding: utf-8 -*-
"""心理话的发布、持久化、排序、删除 —— 对应手工用例 TC-WORDS-* / TC-FUNC-* / TC-HOME-01"""

import pytest
from playwright.sync_api import expect

from pages import ThoughtsPage


def test_tc_words_01_publish_thought(admin, page_logged_in, test_mark):
    """TC-WORDS-01：发布一条心理话，应提示「已发布。」并出现在列表里"""
    content = f"{test_mark} 今天心情不错"

    admin.publish_thought(content)
    expect(admin.flash_success).to_have_text("已发布。")

    thoughts = ThoughtsPage(page_logged_in).open()
    assert thoughts.has_text(content), "刚发布的内容应该出现在列表里"


def test_tc_func_01_content_persists_after_refresh(admin, page_logged_in, test_mark):
    """TC-FUNC-01：发布后刷新页面，内容应仍然存在（数据已持久化）"""
    content = f"{test_mark} 持久化验证"

    admin.publish_thought(content)
    thoughts = ThoughtsPage(page_logged_in).open()
    assert thoughts.has_text(content)

    page_logged_in.reload()
    assert ThoughtsPage(page_logged_in).has_text(content), "刷新后内容不应该消失"


def test_tc_func_02_three_posts_sorted_newest_first(admin, page_logged_in, test_mark):
    """TC-FUNC-02：连续发布 3 条，应都在，且按时间倒序（最新的在最上面）"""
    first = f"{test_mark} 第一条"
    second = f"{test_mark} 第二条"
    third = f"{test_mark} 第三条"

    for text in (first, second, third):
        admin.publish_thought(text)

    contents = ThoughtsPage(page_logged_in).open().all_contents()
    mine = [c for c in contents if test_mark in c]

    assert mine == [third, second, first], (
        f"应按「最新在最上」排序，实际顺序：{mine}"
    )


def test_tc_words_02_empty_content_blocked(admin, page_logged_in, test_mark):
    """TC-WORDS-02：内容留空直接提交，应被必填校验拦下，不会写入空记录"""
    before = ThoughtsPage(page_logged_in).open().count()

    admin.open()
    admin.post_button.click()
    page_logged_in.wait_for_timeout(800)

    after = ThoughtsPage(page_logged_in).open().count()
    assert after == before, "空内容不应该被写入"


@pytest.mark.xfail(
    reason="BUG-001 未修复：超长连续字符会撑破页面排版（见缺陷报告 BUG-001）",
    strict=True,
)
def test_tc_home_01_long_text_no_horizontal_overflow(admin, page_logged_in, test_mark):
    """
    TC-HOME-01：发布超长连续字符后，页面不应出现横向溢出。

    这一条把「排版好不好看」这种只能靠眼睛判断的事，
    量化成了 scrollWidth > clientWidth 这个可断言的客观指标。
    """
    long_text = test_mark + "8" * 200

    admin.publish_thought(long_text)
    thoughts = ThoughtsPage(page_logged_in).open()

    assert thoughts.has_text(long_text[:40]), "超长内容应该发布成功"
    assert not thoughts.has_horizontal_overflow(), (
        "页面出现横向溢出 —— BUG-001 复现（超长连续字符撑破排版）"
    )


def test_tc_func_03_delete_thought(admin, page_logged_in, test_mark):
    """TC-FUNC-03：删除一条心理话，应提示「已删除。」，该条消失、其余保留"""
    doomed = f"{test_mark} 这条要删掉"
    keeper = f"{test_mark} 这条要保留"

    admin.publish_thought(doomed)
    admin.publish_thought(keeper)

    admin.delete_thought(doomed)
    expect(admin.flash_success).to_have_text("已删除。")

    thoughts = ThoughtsPage(page_logged_in).open()
    assert not thoughts.has_text(doomed), "被删除的那条应该消失"
    assert thoughts.has_text(keeper), "其他内容应该完好保留"


def test_tc_func_04_ordered_by_id_desc(admin, page_logged_in, test_mark):
    """TC-WORDS-01 补充：列表顺序应按 id 倒序，最新的永远在最前"""
    old = f"{test_mark} 先发的"
    new = f"{test_mark} 后发的"

    admin.publish_thought(old)
    admin.publish_thought(new)

    mine = [c for c in ThoughtsPage(page_logged_in).open().all_contents()
            if test_mark in c]
    assert mine.index(new) < mine.index(old), "后发布的应该排在前面"
