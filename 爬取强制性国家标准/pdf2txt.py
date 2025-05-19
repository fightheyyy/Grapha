import base64
import os
import time
from openai import OpenAI

# --- 配置区域 ---
OPENROUTER_API_KEY = "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"

# 输入 PDF 文件夹路径
PDF_FOLDER_PATH = r"E:\nanoGraph\爬取强制性国家标准\downloads-4"
# 输出 TXT 文件夹路径（自动创建）
OUTPUT_TXT_FOLDER = os.path.join(PDF_FOLDER_PATH, "extracted")

# OpenRouter API 配置
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "google/gemini-2.5-pro-preview"

# 可选的请求头
EXTRA_HEADERS = {}

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
    if not os.path.exists(PDF_FOLDER_PATH):
        print(f"错误：无法找到指定的 PDF 文件夹 '{PDF_FOLDER_PATH}'。请检查路径是否正确。")
    else:
        # 创建输出文件夹
        if not os.path.exists(OUTPUT_TXT_FOLDER):
            os.makedirs(OUTPUT_TXT_FOLDER)

        # 获取所有 PDF 文件
        pdf_files = [f for f in os.listdir(PDF_FOLDER_PATH) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"错误：在文件夹 '{PDF_FOLDER_PATH}' 中未找到任何 PDF 文件。")
        else:
            print(f"开始批量处理 {len(pdf_files)} 个 PDF 文件...\n")

            for pdf_file in pdf_files:
                PDF_FILE_PATH = os.path.join(PDF_FOLDER_PATH, pdf_file)
                OUTPUT_TXT_FILENAME = os.path.join(OUTPUT_TXT_FOLDER, f"{pdf_file}.txt")

                print(f"正在处理文件: {PDF_FILE_PATH}")

                base64_pdf_content = encode_pdf_to_base64(PDF_FILE_PATH)

                if base64_pdf_content:
                    data_url_for_api = f"data:application/pdf;base64,{base64_pdf_content}"

                    print("PDF 编码完成。正在准备调用 API...")

                    try:
                        client = OpenAI(
                            base_url=BASE_URL,
                            api_key=OPENROUTER_API_KEY,
                        )

                        print(f"向模型 '{MODEL_NAME}' 发送请求以提取信息...")
                        completion = client.chat.completions.create(
                            extra_headers=EXTRA_HEADERS,
                            model=MODEL_NAME,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "帮我从这份PDF文档中详细提取出所有文本信息，一些没用的东西如目录、封面不需要提取，并且把pdf中的表格信息转为文字表述，返回的答案只需要整理后的纯文本，不需要那么多*。"
                                        },
                                        {
                                            "type": "file",
                                            "file": {
                                                "filename": pdf_file,
                                                "file_data": data_url_for_api
                                            }
                                        },
                                    ]
                                }
                            ],
                        )

                        if completion.choices and completion.choices[0].message and completion.choices[0].message.content:
                            extracted_info = completion.choices[0].message.content
                            print("\n--- API 返回的提取信息 ---")
                            print(extracted_info)
                            print("---------------------------\n")

                            save_text_to_file(extracted_info, OUTPUT_TXT_FILENAME)
                        else:
                            print("API 调用成功，但未能获取有效的提取内容。")
                            if completion:
                                print("API 原始响应 (部分):")
                                try:
                                    print(str(completion)[:1000])
                                except Exception as e_print:
                                    print(f"打印原始响应时出错: {e_print}")
                    except Exception as e:
                        print(f"调用 OpenRouter API 时发生错误: {e}")
                        print("继续处理下一个文件...")
                    finally:
                        time.sleep(2)  # 防止限速
                else:
                    print(f"未能对 PDF 文件进行编码，跳过文件: {PDF_FILE_PATH}\n")

    print("\n脚本执行完毕。")