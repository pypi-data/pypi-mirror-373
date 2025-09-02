from noteparse.ossHelper import upload_file_to_minio, generate_snowflake_id
from playwright.sync_api import sync_playwright
import os
from datetime import datetime
# url--网页路径，selector--加载完成的元素选择器
def screenShotByPlaywright(url,selector,prefix='DXYG'):
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(args=['--font-render-hinting=medium'],chromium_sandbox=False)
            page = browser.new_page()
            page.goto(url)
            
            # scroll_height = page.evaluate('document.body.scrollHeight')
            # page.set_viewport_size({"with":1920,"height":scroll_height})
            # 等待元素加载完成
            content = page.wait_for_selector(selector)
            html = page.content()
            screenshot_name = f'{prefix}-screenshot-' + generate_snowflake_id() + ".png"
            page.screenshot(path=screenshot_name,full_page=True)
            imgurl = upload_file_to_minio(screenshot_name, 'screenshot/' + screenshot_name)
            browser.close()
            # 截图完毕后删除截图
            os.remove(screenshot_name)
            return imgurl
        except Exception as screen_img_err:
            print(datetime.now(),f'网页截图失败，网址：{url}',screen_img_err)
            return ''
# 设定main函数,程序起点
if __name__ == '__main__':
    screenShotByPlaywright('https://caigou.chinatelecom.com.cn/DeclareDetails?id=7196160872105676&type=1&docTypeCode=TenderAnnouncement','.mbg')