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
    'browser.download.manager.showWhenStarting':False
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

for i, btn in enumerate(detail_buttons):
    try:
        print(f"\n\n🟠 正在处理第 {i + 1} 个标准详情...")

        # 点击“查看详细”
        btn.click()
        time.sleep(2)

        # 切换到详情页窗口
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            print("✅ 成功切换到详情页窗口")
        else:
            print("❌ 未打开新窗口，跳过该条目")
            continue

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
            driver.switch_to.window(driver.window_handles[0])
            continue

        # 点击“下载标准”，进入验证码页面
        download_button = driver.find_element(By.XPATH, '//button[contains(text(), "下载标准")]')
        download_button.click()
        time.sleep(2)

        # 切换到验证码页面（再次切换窗口）
        if len(driver.window_handles) > 2:
            driver.switch_to.window(driver.window_handles[2])
            print("✅ 成功切换到验证码页面")
        elif len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            print("✅ 成功切换到验证码页面")
        else:
            print("❌ 未打开验证码页面，可能没有权限或页面结构变化")
            driver.save_screenshot(f"no_captcha_page_{i}.png")
            continue

        # 等待验证码输入框出现
        try:
            captcha_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'verifyCode'))
            )
            print("✅ 验证码输入框已找到")

            # 截图整个页面
            screenshot = driver.get_screenshot_as_png()
            screenshot = Image.open(BytesIO(screenshot))

            screenshot.save("captcha.png")
            print("✅ 验证码图片已裁剪并保存为 captcha.png")

            # 图像预处理
            image = cv2.imread("captcha.png")
            # 将图片转换为numpy数组
            array = np.array(image)

            # 验证码的坐标范围（根据计算结果调整）
            x_start, y_start, x_end, y_end = 344, 465, 491, 524

            # 裁剪验证码
            captcha = array[y_start:y_end + 1, x_start:x_end + 1]  # +1确保包含右下角像素

            # 保存裁剪后的验证码
            cropped_image = Image.fromarray(captcha)
            cropped_image.save("captcha_processed.png")
            print("✅ 验证码已完成预处理")

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
            print(f"✅ 识别到的验证码为: {captcha_text}")

            # 输入验证码
            captcha_input.send_keys(captcha_text)
            print("✅ 验证码已输入")

            # 点击验证按钮
            verify_button = driver.find_element(By.XPATH, '//button[text()="验证"]')
            verify_button.click()
            print("✅ 点击了【验证】按钮")

            # 等待下载开始
            time.sleep(5)

        except Exception as captcha_err:
            print(f"❌ 验证码页面加载失败: {captcha_err}")
            driver.save_screenshot(f"captcha_error_{i}.png")
            continue

        # 关闭当前窗口并切回主窗口
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"🔴 处理过程中发生错误: {e}")
        driver.save_screenshot(f"error_{i}.png")
        continue

# 结束后关闭浏览器
print("\n🔚 程序执行完毕，关闭浏览器")
driver.quit()