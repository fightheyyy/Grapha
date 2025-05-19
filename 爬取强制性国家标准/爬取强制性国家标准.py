import base64
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import requests

# 设置下载目录
download_dir = r"E:\nanoGraph\爬取强制性国家标准\downloads"
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

# 打开目标网址
url = "https://openstd.samr.gov.cn/bzgk/gb/std_list_type?r=0.41751660996824924&p.p1=1&p.p5=PUBLISHED&p.p6=91&p.p90=circulation_date&p.p91=desc "
print("🌐 正在打开目标网址...")
driver.get(url)

# 等待主页面加载完成
try:
    print("⏳ 正在等待页面加载...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "查看详细")]'))
    )
except Exception as e:
    print("❌ 主页面加载失败，请检查网络或网页结构是否改变。")
    driver.quit()
    exit()

# 获取所有“查看详细”按钮
detail_buttons = driver.find_elements(By.XPATH, '//*[contains(text(), "查看详细")]')
print(f"✅ 共找到 {len(detail_buttons)} 个【查看详细】按钮")

main_window = driver.current_window_handle  # 记录主窗口

for i, btn in enumerate(detail_buttons):
    try:
        print(f"\n\n🟠 正在处理第 {i + 1} 个标准详情...")

        # 点击“查看详细”，等待新窗口出现
        btn.click()
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

        # 等待详情页加载完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "下载标准")]'))
            )
            print("✅ 页面加载完成，找到【下载标准】按钮")
        except Exception as e:
            print("❌ 页面加载失败或找不到【下载标准】按钮")
            driver.save_screenshot(f"error_page_{i}.png")
            driver.close()
            driver.switch_to.window(main_window)
            continue

        # 点击“下载标准”，进入验证码页面
        download_button = driver.find_element(By.XPATH, '//button[contains(text(), "下载标准")]')
        download_button.click()
        WebDriverWait(driver, 10).until(EC.new_window_is_opened([main_window, detail_window]))

        # 获取验证码页面句柄
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

        # 显式等待验证码输入框出现
        captcha_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'verifyCode'))
        )
        print("✅ 验证码输入框已找到")

        # 备用方案：全屏截图+固定坐标裁剪（根据实际验证码位置调整）
        driver.save_screenshot("full_screenshot.png")
        img = Image.open("full_screenshot.png")
        # 示例坐标范围（需根据实际屏幕分辨率调整）
        captcha = img.crop((344, 465, 491, 524))
        captcha.save("captcha_processed.png")
        print("✅ 使用备用方案裁剪验证码完成")

        # 使用 jfbym.com API 进行验证码识别
        with open('captcha_processed.png', 'rb') as f:
            b = base64.b64encode(f.read()).decode()  # 将图片转为 Base64 字符串

        url = "http://api.jfbym.com/api/YmServer/customApi"
        data = {
            "token": "MlGR4NhGZrep5kQM88ZkbfmMB5aDIUgbdQzxVY7nLqY",  # 替换为您自己的 token
            "type": "10110",  # 根据验证码类型调整（参考官方文档）
            "image": b,
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data).json()
        print(f"✅ jfbym.com API 返回: {response}")

        # 提取识别结果
        captcha_text = response.get("data", {}).get("data", "")
        if not captcha_text:
            print("❌ API 未返回有效验证码，请检查 token 或验证码类型。")
        else:
            print(f"✅ 识别到的验证码为: {captcha_text}")

        # 输入验证码
        captcha_input.send_keys(captcha_text)
        print("✅ 验证码已输入")

        # 点击验证按钮
        verify_button = driver.find_element(By.XPATH, '//button[text()="验证"]')
        verify_button.click()
        print("✅ 点击了【验证】按钮")


        # 下载等待逻辑
        def wait_for_download(download_dir, timeout=30):
            seconds = 0
            while seconds < timeout:
                files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
                if files:
                    return True
                time.sleep(1)
                seconds += 1
            return False


        if wait_for_download(download_dir):
            print("✅ 文件下载成功")
        else:
            print("❌ 文件下载超时")

    except Exception as e:
        print(f"🔴 处理过程中发生错误: {e}")
        # 强制关闭所有非主窗口
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
        # 安全关闭所有非主窗口
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