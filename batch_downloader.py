from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

# 设置 Edge 浏览器选项
edge_options = webdriver.EdgeOptions()
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--no-sandbox')
edge_options.add_argument('--headless')  # 可选：无头模式后台运行

# 自动下载适配版本的 EdgeDriver（推荐）
try:
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    service = EdgeService(EdgeChromiumDriverManager().install())
except Exception as e:
    print("⚠️ webdriver-manager 加载失败，尝试手动指定路径...")
    service = EdgeService(executable_path='msedgedriver')

# 创建 Edge 浏览器驱动
driver = webdriver.Edge(service=service, options=edge_options)

# 基础网址
base_url = "https://www.mohurd.gov.cn/gongkai/zhengce/gzk/index.html"

# 创建输出文件目录
output_dir = "mohurd_policy_details2"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'policy_detail_urls.txt')


def get_titles_and_detail_links():
    """从当前页面中提取政策标题和对应的详情页链接"""
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    titles = []
    links = []

    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'])

        # 只保留符合详情页格式的 URL
        if "/gongkai/zhengce/gzk/art/" in href:
            title = a.get_text(strip=True)
            titles.append(title)
            links.append(href)

    return titles, links


def save_to_file(titles, links):
    """将标题与链接写入文件"""
    with open(output_file, 'a', encoding='utf-8') as f:
        for title, link in zip(titles, links):
            line = f"{title} - {link}\n"
            f.write(line)
            print(f"📌 已保存：{line.strip()}")
    print(f"✅ 当前页共保存了 {len(titles)} 条记录。")


def click_next_page_button():
    """尝试点击“下一页”按钮"""
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "下一页")]'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        time.sleep(3)  # 等待新内容加载
        return True
    except Exception as e:
        print("⛔ 无法找到‘下一页’按钮，可能已是最后一页。")
        return False


def crawl_pages(max_pages=10):
    current_page = 1
    total_count = 0

    while current_page <= max_pages:
        print(f"\n📘 正在处理第 {current_page} 页...")

        titles, detail_links = get_titles_and_detail_links()

        if not titles:
            print("❌ 当前页没有找到任何有效的政策信息。")
            break

        save_to_file(titles, detail_links)
        total_count += len(titles)

        # 尝试翻页
        success = click_next_page_button()
        if not success:
            print("🔚 已到最后一页，停止翻页。")
            break

        current_page += 1

    print(f"\n🎉 共提取并保存 {total_count} 条政策信息。")


def main():
    print("📘 开始批量提取住建部规章库的政策标题及详情页链接...")
    driver.get(base_url)
    time.sleep(5)  # 初始等待加载

    crawl_pages(max_pages=10)

    print(f"🏁 所有数据已保存至：{output_file}")
    driver.quit()


if __name__ == "__main__":
    main()