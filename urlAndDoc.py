from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlparse, parse_qs
import os
import time
import requests

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

# 创建下载目录
output_dir = "mohurd_word_documents2"
os.makedirs(output_dir, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_text_version_links():
    """提取当前页面中的‘文字版’链接"""
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    text_version_links = []
    for a in soup.find_all('a', href=True):
        if '文字版' in a.get_text(strip=True):
            full_url = urljoin(base_url, a['href'])
            text_version_links.append(full_url)
    return text_version_links


def get_detail_page_links():
    """精确提取当前页面中每个政策的详情页链接"""
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    detail_links = []
    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'])

        # 排除 javascript 链接
        if href.startswith("javascript:"):
            continue

        # 排除下载链接和图片版链接
        if "/downloadWord" in href or "fileUrl=" in href or "viewType=1" in href:
            continue

        # 只保留符合详情页格式的链接
        if "/gongkai/zhengce/gzk/art/" in href:
            detail_links.append(href)

    return detail_links

def get_filename_from_url(url):
    """从 URL 中提取并解码文件名"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    file_name = query_params.get('fileName', ['未命名文档'])[0]
    return unquote(file_name)


def download_word_document(doc_url):
    """下载 Word 文档"""
    try:
        response = requests.get(doc_url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()

        # 提取文件名并添加 .doc 后缀
        filename = get_filename_from_url(doc_url)
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        file_path = os.path.join(output_dir, f"{safe_filename}.docx")

        print(f"正在下载：{safe_filename}.docx 来源：{doc_url}")
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 每次读取 1MB
                f.write(chunk)
        print(f"已保存：{file_path}")

    except Exception as e:
        print(f"❌ 下载失败：{doc_url}, 错误：{e}")


def get_title_from_detail_page(url):
    """访问详情页并提取网页标题作为文档名"""
    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        title = driver.title.strip()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return title
    except Exception as e:
        print(f"❌ 获取详情页标题失败：{url}, 错误：{e}")
        return "未命名文档"


def save_detail_urls_to_file(urls, filename='policy_detail_urls.txt'):
    """将详情页链接和对应文档名写入文件"""
    with open(filename, 'a', encoding='utf-8') as f:
        for url in urls:
            title = get_title_from_detail_page(url)
            line = f"{title} - {url}\n"
            f.write(line)
            print(f"📌 已保存：{line.strip()}")
    print(f"✅ 已将 {len(urls)} 条记录写入 {filename}")


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


def crawl_pages_with_selenium(max_pages=10):
    current_page = 1
    downloaded_count = 0

    while current_page <= max_pages:
        print(f"\n📘 正在处理第 {current_page} 页...")

        # 获取“文字版”链接（用于下载）
        doc_links = get_text_version_links()

        # 获取“标题”链接（用于详情页）
        detail_links = get_detail_page_links()

        if not doc_links:
            print("❌ 当前页没有找到任何‘文字版’链接。")
            break

        print(f"✅ 第 {current_page} 页共找到 {len(doc_links)} 个‘文字版’链接，{len(detail_links)} 个详情页链接。")

        # 打印详情页链接，并下载 Word 文档
        for idx, (doc_url, detail_url) in enumerate(zip(doc_links, detail_links)):
            print(f"📌 第 {idx + 1} 条政策详情页链接：{detail_url}")
            download_word_document(doc_url)
            downloaded_count += 1

        # 保存详情页链接到文件
        save_detail_urls_to_file(detail_links)

        # 尝试翻页
        success = click_next_page_button()
        if not success:
            print("🔚 已到最后一页，停止翻页。")
            break

        current_page += 1

    print(f"\n🎉 共下载 {downloaded_count} 个文档。")


def main():
    print("📘 开始批量下载住建部规章库‘文字版’Word文档及提取详情页URL...")
    driver.get(base_url)
    time.sleep(5)  # 初始等待加载

    crawl_pages_with_selenium(max_pages=10)

    print("🏁 所有文档已保存在 mohurd_word_documents 文件夹中。")
    print("📄 所有详情页链接已写入 policy_detail_urls.txt 文件中。")
    driver.quit()


if __name__ == "__main__":
    main()