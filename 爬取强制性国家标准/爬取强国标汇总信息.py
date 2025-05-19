import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
}

def fetch_page(page_num):
    url = f'https://openstd.samr.gov.cn/bzgk/gb/std_list_type?page= {page_num}&pageSize=10&p.p1=1&p.p5=PUBLISHED&p.p6=91&p.p90=circulation_date&p.p91=desc'
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自动识别编码
        return response.text
    except Exception as e:
        print(f"第 {page_num} 页请求失败：{e}")
        return None


def parse_page(html):
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')

    # 查找带有 border 样式的 tbody
    tbody = None
    for t in soup.find_all('tbody'):
        if t.has_attr('style') and 'border' in t.get('style', ''):
            tbody = t
            break

    if not tbody:
        print("未找到目标 tbody，请检查网页结构")
        return []

    rows = tbody.find_all('tr')
    data = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 8:
            continue  # 跳过不完整的行

        item = {
            '序号': cols[0].get_text(strip=True),
            '标准号': cols[1].find('a').get_text(strip=True) if cols[1].find('a') else '',
            '是否采标': cols[2].get_text(strip=True),
            '标准名称': cols[3].find('a').get_text(strip=True) if cols[3].find('a') else '',
            '状态': cols[4].get_text(strip=True),
            '发布日期': cols[5].get_text(strip=True),
            '实施日期': cols[6].get_text(strip=True)
        }

        data.append(item)

    return data


def crawl_pages(total_pages):
    all_data = []
    for page in range(1, total_pages + 1):
        print(f"正在爬取第 {page} 页...")
        html = fetch_page(page)
        items = parse_page(html)
        all_data.extend(items)
        time.sleep(1.5)

    return all_data


if __name__ == '__main__':
    total_pages = 7
    data = crawl_pages(total_pages)

    df = pd.DataFrame(data)
    output_file = f'national_standards_{total_pages}_pages.csv'
    df.to_csv(output_file, index=False, encoding='utf_8_sig')

    print(f"共爬取 {len(data)} 条记录，已保存为 {output_file}")