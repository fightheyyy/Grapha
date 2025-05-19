import base64

import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
from PIL import Image

# 设置下载目录
download_dir = r"E:\nanoGraph\爬取强制性国家标准\downloads-3"
os.makedirs(download_dir, exist_ok=True)

# 配置 Edge 选项
edge_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
    "download.show_download_in_toolbar": False,
    "profile.default_content_settings.popups": 0,
    'browser.download.manager.showWhenStarting': False,
    "browser.download.alwaysOpenPanel": False,
    "browser.download.animateNotifications":False,
    "download.manager.showAlertOnComplete":False,
}
edge_options.add_experimental_option("prefs", prefs)
edge_options.add_argument("--disable-blink-features=AutomationControlled")

# 初始化 WebDriver
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)

# 基础 URL
base_url = "https://openstd.samr.gov.cn/bzgk/gb/std_list_type?r=0.41751660996824924&p.p1=1&p.p5=PUBLISHED&p.p6=91&p.p90=circulation_date&p.p91=desc "

# 设置要爬取的最大页数
max_pages = 5

main_window = driver.current_window_handle

for page_num in range(1, max_pages + 1):
    if page_num == 1:
        url = base_url
    else:
        url = f"https://openstd.samr.gov.cn/bzgk/gb/std_list_type?r=0.621924287259578&page= {page_num}&pageSize=10&p.p1=1&p.p5=PUBLISHED&p.p6=91&p.p90=circulation_date&p.p91=desc"

    print(f"\n\n🟠 正在爬取第 {page_num} 页：{url}")
    driver.get(url)
    time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "查看详细")]'))
        )
        time.sleep(1)
    except Exception:
        print("❌ 页面加载失败，请检查网络或网页结构是否改变。")
        continue

    detail_buttons = driver.find_elements(By.XPATH, '//*[contains(text(), "查看详细")]')
    print(f"✅ 共找到 {len(detail_buttons)} 个【查看详细】按钮")

    for i, btn in enumerate(detail_buttons):
        try:
            print(f"\n\n🟡 正在处理第 {i + 1} 个标准详情...")

            # 点击查看详细
            btn.click()
            time.sleep(1)
            WebDriverWait(driver, 10).until(EC.new_window_is_opened([main_window]))

            # 获取详情页窗口句柄
            detail_window = None
            for handle in driver.window_handles:
                if handle != main_window:
                    detail_window = handle
                    break
            if not detail_window:
                print("❌ 未找到详情页窗口，跳过该条目")
                continue

            driver.switch_to.window(detail_window)
            print("✅ 成功切换到详情页窗口")
            time.sleep(1)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "下载标准")]'))
                )
                print("✅ 页面加载完成，找到【下载标准】按钮")
            except Exception:
                print("❌ 页面加载失败或找不到【下载标准】按钮")
                driver.save_screenshot(f"error_page_{i}.png")
                driver.close()
                driver.switch_to.window(main_window)
                continue

            # 点击“下载标准”，进入验证码页面
            download_button = driver.find_element(By.XPATH, '//button[contains(text(), "下载标准")]')
            download_button.click()
            time.sleep(1)
            WebDriverWait(driver, 10).until(EC.new_window_is_opened([main_window, detail_window]))

            captcha_window = None
            for handle in driver.window_handles:
                if handle not in [main_window, detail_window]:
                    captcha_window = handle
                    break
            if not captcha_window:
                print("❌ 未找到验证码页面")
                driver.close()
                driver.switch_to.window(detail_window)
                driver.close()
                driver.switch_to.window(main_window)
                continue

            driver.switch_to.window(captcha_window)
            print("✅ 成功切换到验证码页面")
            time.sleep(1)

            # 显式等待验证码输入框出现
            captcha_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'verifyCode'))
            )

            downloaded = False
            max_retries = 5

            for retry in range(max_retries):
                print(f"\n🔄 第 {retry + 1} 次尝试识别验证码...")

                # 截图并裁剪验证码区域
                driver.save_screenshot("full_screenshot.png")
                img = Image.open("full_screenshot.png")
                captcha = img.crop((344, 465, 491, 524))  # 根据实际位置修改坐标
                captcha.save("captcha_processed.png")

                # 使用 jfbym.com API 进行验证码识别
                with open('captcha_processed.png', 'rb') as f:
                    b = base64.b64encode(f.read()).decode()

                url_api = "http://api.jfbym.com/api/YmServer/customApi"
                data = {
                    "token": "MlGR4NhGZrep5kQM88ZkbfmMB5aDIUgbdQzxVY7nLqY",
                    "type": "10110",
                    "image": b,
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(url_api, headers=headers, json=data).json()
                captcha_text = response.get("data", {}).get("data", "")

                print(f"✅ 识别到的验证码为: {captcha_text}")

                # 清空输入框
                captcha_input.clear()
                time.sleep(0.5)

                # 输入验证码
                captcha_input.send_keys(captcha_text)
                print("✅ 验证码已输入")

                # 点击验证按钮
                verify_button = driver.find_element(By.XPATH, '//button[text()="验证"]')
                verify_button.click()
                print("✅ 点击了【验证】按钮")
                time.sleep(2)

                # 判断是否下载成功
                def wait_for_download(download_dir, timeout=30):
                    seconds = 0
                    while seconds < timeout:
                        files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
                        if files:
                            return True
                        time.sleep(1)
                        seconds += 1
                    return False

                downloaded = wait_for_download(download_dir)
                if downloaded:
                    print("🎉 文件下载成功！")
                    break
                else:
                    print("⚠️ 验证码可能错误，准备重新识别...")
                    time.sleep(2)  # 等待页面刷新验证码

            if not downloaded:
                print("❌ 多次尝试后仍未成功下载文件，跳过该条目")

        except Exception as e:
            print(f"🔴 处理过程中发生错误: {e}")
            current_handles = driver.window_handles
            for handle in current_handles:
                if handle != main_window:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except:
                        pass
            driver.switch_to.window(main_window)
            continue

        finally:
            # 关闭所有非主窗口
            current_handles = driver.window_handles
            for handle in current_handles:
                if handle != main_window:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except:
                        pass
            driver.switch_to.window(main_window)

# 结束后关闭浏览器
print("\n🔚 程序执行完毕，关闭浏览器")
driver.quit()