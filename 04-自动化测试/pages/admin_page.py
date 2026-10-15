# -*- coding: utf-8 -*-
"""后台管理页 /admin

页面上有 4 个表单，里面的输入框都没有 id，所以这里统一用
form 的 action 属性来限定作用域 —— 比用位置或文字更稳。

⚠️ 安全提醒：页面上还有一个「修改密码」表单（action="/admin/password"），
   提交它会真实改写服务器上的密码。本项目**故意不测这个功能**，
   以免把用户的真实密码改掉。（这是有意识的风险规避，不是遗漏。）
"""

from playwright.sync_api import Page

from config import TEST_PREFIX, url
from pages.base_page import BasePage

# 在页面里并发发 N 个发布请求（用来复现「连点重复提交」，见 publish_concurrently）
_并发提交脚本 = """
async ([内容, 次数]) => {
    const body = new URLSearchParams({ content: 内容 });
    const 请求 = Array.from({ length: 次数 }, () =>
        fetch('/admin/post', { method: 'POST', body })
    );
    const 响应们 = await Promise.all(请求);
    return 响应们.map(r => r.status);
}
"""


class AdminPage(BasePage):
    PATH = "admin"

    def __init__(self, page: Page):
        super().__init__(page)

        # ---- 发布心理话 ----
        self.post_form = page.locator('form[action="/admin/post"]')
        self.post_textarea = self.post_form.locator('textarea[name="content"]')
        self.post_button = self.post_form.locator('button[type="submit"]')

        # ---- 上传照片 ----
        self.photo_form = page.locator('form[action="/admin/photo"]')
        self.photo_input = self.photo_form.locator('input[name="photo"]')
        self.caption_input = self.photo_form.locator('input[name="caption"]')
        self.upload_button = self.photo_form.locator('button[type="submit"]')

        # ---- 修改主页 ----
        self.profile_form = page.locator('form[action="/admin/profile"]')
        self.title_input = self.profile_form.locator('input[name="title"]')
        self.intro_input = self.profile_form.locator('textarea[name="intro"]')
        self.profile_button = self.profile_form.locator('button[type="submit"]')

        # ---- 管理列表（每条都有删除按钮）----
        self.manage_rows = page.locator("div.manage-row")       # 心理话
        self.manage_photos = page.locator("div.manage-photo")   # 照片

    # ==================================================================
    # 发布心理话
    # ==================================================================
    def publish_thought(self, content: str):
        """发布一条心理话"""
        self.post_textarea.fill(content)
        self.post_button.click()
        self.page.wait_for_load_state("networkidle")
        return self

    def publish_concurrently(self, content: str, times: int = 3):
        """
        并发提交 N 次「发布」，模拟用户快速连点按钮。

        为什么不直接用 Playwright 连点按钮？
        因为 Playwright 的点击太精确了 —— 第一次点击后页面立刻开始跳转，
        后面几次点击会被浏览器直接丢掉，根本复现不出来（实测连点 3 次只写入 1 条）。

        改成在页面里用 fetch 同时发 N 个请求：走的是同一个接口、同一个登录会话，
        正是「后端缺少防重复提交」这个缺陷的正确测法。
        """
        self.open()
        self.post_textarea.fill(content)
        return self.page.evaluate(_并发提交脚本, [content, times])

    def delete_thought(self, content: str):
        """删掉正文包含 content 的那条心理话（走界面点击）"""
        row = self.manage_rows.filter(has_text=content).first
        row.locator("button.btn-danger").click()
        self.page.wait_for_load_state("networkidle")
        return self

    # ==================================================================
    # 照片
    # ==================================================================
    def upload_photo(self, file_path: str, caption: str = ""):
        """上传一张照片"""
        self.photo_input.set_input_files(file_path)
        if caption:
            self.caption_input.fill(caption)
        self.upload_button.click()
        self.page.wait_for_load_state("networkidle")
        return self

    def delete_photo(self, caption: str):
        """
        删掉说明包含 caption 的那张照片。

        注意：后台的照片列表**不显示照片说明文字**（只有缩略图 + 身份标签 + 删除按钮），
        所以没法按文字定位。办法是：先到前台相册按说明找到图片地址，
        再回后台按图片地址精确定位要删的那一张。
        """
        from pages.photos_page import PhotosPage  # 延迟导入，避免模块循环依赖

        photos = PhotosPage(self.page).open()
        src = photos.find(caption).first.locator("img").get_attribute("src")

        self.open()
        self.page.locator(
            f'div.manage-photo:has(img[src="{src}"]) button.btn-danger'
        ).click()
        self.page.wait_for_load_state("networkidle")
        return self

    # ==================================================================
    # 主页资料
    # ==================================================================
    def update_profile(self, title: str, intro: str = ""):
        self.title_input.fill(title)
        if intro:
            self.intro_input.fill(intro)
        self.profile_button.click()
        self.page.wait_for_load_state("networkidle")
        return self

    def get_profile_title(self) -> str:
        """读当前主页标题（用于测试前保存、测试后恢复）"""
        return self.title_input.input_value()

    def get_profile_intro(self) -> str:
        return self.intro_input.input_value()

    # ==================================================================
    # 测试数据清理
    # ==================================================================
    def _collect_actions(self, row_locator, action_prefix: str) -> list:
        """从后台列表里找出所有「文字包含测试前缀」的条目，返回它们的删除地址"""
        actions = []
        for i in range(row_locator.count()):
            row = row_locator.nth(i)
            try:
                text = row.inner_text() or ""
            except Exception:
                continue
            if TEST_PREFIX in text:
                action = row.locator(
                    f'form[action^="{action_prefix}"]'
                ).get_attribute("action")
                if action:
                    actions.append(action)
        return actions

    def _collect_photo_actions(self) -> list:
        """
        收集测试照片的删除地址。

        后台照片列表不显示说明文字，按文字找不到 ——
        所以先去前台相册（那里有说明文字）拿到图片地址，再回后台按 img[src] 精确定位。
        """
        from pages.photos_page import PhotosPage  # 延迟导入，避免循环依赖

        photos = PhotosPage(self.page).open()
        srcs = photos.find(TEST_PREFIX).locator("img").evaluate_all(
            "imgs => imgs.map(img => img.getAttribute('src'))"
        )
        if not srcs:
            return []

        self.open()
        actions = []
        for src in srcs:
            action = self.page.locator(
                f'div.manage-photo:has(img[src="{src}"]) form'
            ).get_attribute("action")
            if action:
                actions.append(action)
        return actions

    def cleanup_test_data(self) -> int:
        """
        删掉所有带测试前缀的心理话和照片，返回删掉的总条数。

        这里刻意**绕过界面**，直接用已登录的会话发 POST 请求 ——
        清理不是被测功能，走 UI 会又慢又容易因为页面跳转失败。
        （删除接口本身就是 POST，和界面上点按钮走的是同一个路由。）
        """
        deleted = 0

        # 心理话：后台列表直接显示正文，按文字找即可
        self.open()
        for action in self._collect_actions(self.manage_rows, "/admin/post/"):
            if self.page.request.post(url(action.lstrip("/"))).ok:
                deleted += 1

        # 照片：后台不显示说明文字，得走前台相册绕一下
        for action in self._collect_photo_actions():
            if self.page.request.post(url(action.lstrip("/"))).ok:
                deleted += 1

        return deleted
