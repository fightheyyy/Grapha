import base64
import os
from openai import OpenAI

# --- 配置区域 ---
# 强烈建议使用环境变量来管理 API 密钥
# OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
# if not OPENROUTER_API_KEY:
#     raise ValueError("请设置 OPENROUTER_API_KEY 环境变量")

# 为了直接运行您的代码，这里暂时保留了硬编码的密钥，但请注意安全风险
OPENROUTER_API_KEY = "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"

# PDF 文件路径 (请确保此文件与脚本在同一目录或提供完整路径)
PDF_FILE_PATH = "1号住宅楼_1_01_结构设计总说明一 第1版1703KB.pdf"
# 输出 TXT 文件的名称
OUTPUT_TXT_FILENAME = "extracted_construction_info.txt"

# OpenRouter API 配置
BASE_URL = "https://openrouter.ai/api/v1"
# 您选择的模型，请确保 OpenRouter 支持此模型以及您使用的文件传递方式
MODEL_NAME = "google/gemini-2.5-pro-exp-03-25" # 更新为更可能支持此格式的稳定模型，原 "google/gemini-2.5-pro-exp-03-25" 实验性较强

# 可选的请求头
EXTRA_HEADERS = {
    # "HTTP-Referer": "<YOUR_SITE_URL>", # 替换为您的站点 URL
    # "X-Title": "<YOUR_SITE_NAME>",    # 替换为您的站点名称
}

# --- 函数定义 ---
def encode_pdf_to_base64(pdf_path):
    """将 PDF 文件内容编码为 Base64 字符串。"""
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"错误：PDF 文件未找到 - {pdf_path}")
        return None
    except Exception as e:
        print(f"读取或编码 PDF 时出错: {e}")
        return None

def save_text_to_file(text_content, filename):
    """将文本内容保存到指定的文件中。"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"信息已成功保存到文件: {filename}")
    except IOError as e:
        print(f"写入文件时发生错误 ({filename}): {e}")
    except Exception as e:
        print(f"保存文件时发生未知错误: {e}")

# --- 主逻辑 ---
if __name__ == "__main__":
    if not os.path.exists(PDF_FILE_PATH):
        print(f"错误：无法找到指定的 PDF 文件 '{PDF_FILE_PATH}'。请检查文件路径是否正确。")
    else:
        print(f"正在读取并编码 PDF 文件: {PDF_FILE_PATH}...")
        base64_pdf_content = encode_pdf_to_base64(PDF_FILE_PATH)

        if base64_pdf_content:
            # 构建 data URL (如果 OpenRouter 的 "file_data" 字段需要完整的 data URL)
            # 如果 "file_data" 字段只需要纯 base64 字符串，则直接使用 base64_pdf_content
            data_url_for_api = f"data:application/pdf;base64,{base64_pdf_content}"
            # 或者，如果 API 只需要纯 base64:
            # file_data_for_api = base64_pdf_content

            print("PDF 编码完成。正在准备调用 API...")

            try:
                client = OpenAI(
                    base_url=BASE_URL,
                    api_key=OPENROUTER_API_KEY,
                )

                print(f"向模型 '{MODEL_NAME}' 发送请求以提取信息...")
                completion = client.chat.completions.create(
                    extra_headers=EXTRA_HEADERS,
                    # extra_body={}, # 通常不需要，除非 OpenRouter 文档特别说明
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "帮我从这份PDF文档中详细提取出所有与“施工”、“安装”、“规范”、“要求”、“标准”、“验收”、“材料”、“检验”、“试验”、“安全”、“措施”相关的关键文本信息、条款和具体数值。请确保提取内容的全面性和准确性。"
                                },
                                {
                                    # 注意：这个 "file" 类型和其结构是您提供的，
                                    # 请确保它符合 OpenRouter 对 Gemini 模型传递文件的方式。
                                    # 如果 OpenRouter 期望的是类似 OpenAI 的 image_url 格式（但用于文件），
                                    # 结构可能会是 {"type": "image_url", "image_url": {"url": data_url_for_api}}
                                    "type": "file",
                                    "file": {
                                        "filename": os.path.basename(PDF_FILE_PATH), # 使用实际文件名
                                        "file_data": data_url_for_api # 或者 file_data_for_api (纯base64)
                                                                    # 具体取决于 OpenRouter 的要求
                                    }
                                },
                            ]
                        }
                    ],
                    # max_tokens=4000, # 根据需要调整，以确保能接收到完整的提取内容
                    # temperature=0.2 # 较低的 temperature 可能更适合信息提取
                )

                if completion.choices and completion.choices[0].message and completion.choices[0].message.content:
                    extracted_info = completion.choices[0].message.content
                    print("\n--- API 返回的提取信息 ---")
                    print(extracted_info)
                    print("---------------------------\n")

                    # 将提取的信息保存到 TXT 文件
                    save_text_to_file(extracted_info, OUTPUT_TXT_FILENAME)
                else:
                    print("API 调用成功，但未能获取有效的提取内容。")
                    if completion:
                        print("API 原始响应 (部分):")
                        try:
                            print(str(completion)[:1000]) # 打印部分原始响应以供调试
                        except Exception as e_print:
                            print(f"打印原始响应时出错: {e_print}")


            except ImportError:
                print("错误：OpenAI Python 库未安装或无法导入。请运行 'pip install openai'")
            except Exception as e:
                print(f"调用 OpenRouter API 时发生错误: {e}")
                print("请检查以下几点：")
                print("1. 您的 OpenRouter API 密钥是否正确且有效。")
                print(f"2. 模型名称 '{MODEL_NAME}' 是否受 OpenRouter 支持，并且支持您提供的文件格式。")
                print("3. 您提供的 'content' 结构（特别是 'type': 'file' 部分）是否符合 OpenRouter 的要求。")
                print("4. 网络连接是否正常。")
                print("5. PDF 文件是否过大或格式不受支持。")
        else:
            print("未能对 PDF 文件进行编码，无法继续。")

    print("\n脚本执行完毕。")
