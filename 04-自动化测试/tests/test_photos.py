# -*- coding: utf-8 -*-
"""照片上传与删除 —— 对应手工用例 TC-PHOTO-* / TC-FUNC-05"""

from playwright.sync_api import expect

from pages import PhotosPage


def test_tc_photo_02_upload_photo(admin, page_logged_in, test_mark, test_image):
    """TC-PHOTO-02：上传一张照片，应提示「照片已上传。」并出现在相册里"""
    caption = f"{test_mark} 测试照片"

    admin.upload_photo(str(test_image), caption)
    expect(admin.flash_success).to_have_text("照片已上传。")

    photos = PhotosPage(page_logged_in).open()
    assert photos.has_caption(caption), "刚上传的照片应该出现在相册里"


def test_tc_photo_upload_image_loads_ok(admin, page_logged_in, test_mark, test_image):
    """TC-FUNC-06 补充：上传后相册里的图片应能正常加载（不是坏图）"""
    caption = f"{test_mark} 加载检查"

    admin.upload_photo(str(test_image), caption)
    photos = PhotosPage(page_logged_in).open()
    photos.find(caption).wait_for()

    broken = photos.all_broken_images()
    assert not broken, f"相册里有加载失败的图片：{broken}"


def test_tc_func_05_delete_photo(admin, page_logged_in, test_mark, test_image):
    """TC-FUNC-05：删除一张照片，应提示「照片已删除。」且该照片消失"""
    caption = f"{test_mark} 待删除照片"

    admin.upload_photo(str(test_image), caption)
    assert PhotosPage(page_logged_in).open().has_caption(caption)

    admin.open().delete_photo(caption)
    expect(admin.flash_success).to_have_text("照片已删除。")

    assert not PhotosPage(page_logged_in).open().has_caption(caption)


def test_tc_photo_03_no_file_selected_blocked(admin, page_logged_in, test_mark):
    """TC-PHOTO-03：不选文件直接点上传，应被必填校验拦下，不会新增照片"""
    before = PhotosPage(page_logged_in).open().count()

    admin.open()
    admin.upload_button.click()
    page_logged_in.wait_for_timeout(800)

    after = PhotosPage(page_logged_in).open().count()
    assert after == before, "没选文件不应该上传成功"
