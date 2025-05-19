import os

# --- 配置区域 ---
PDF_FOLDER_PATH = r"E:\nanoGraph\爬取强制性国家标准\downloads-4"
OUTPUT_TXT_FOLDER = r"downloads-4-extracted_txt_files"

# --- 函数定义 ---

def create_blank_txt_files(pdf_folder, output_folder):
    """为指定文件夹中的每个 PDF 文件创建一个对应的空白 .txt 文件"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")

    # 获取所有 PDF 文件
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"错误：在文件夹 '{pdf_folder}' 中未找到任何 PDF 文件。")
        return

    print(f"开始为 {len(pdf_files)} 个 PDF 文件创建空白 .txt 文件...")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
        txt_path = os.path.join(output_folder, txt_filename)

        try:
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                pass  # 创建空白文件
            print(f"成功创建空白文件: {txt_path}")
        except IOError as e:
            print(f"创建文件时发生错误 ({txt_path}): {e}")
        except Exception as e:
            print(f"创建文件时发生未知错误: {e}")

    print("\n所有空白 .txt 文件创建完成！")


# --- 主程序入口 ---
if __name__ == "__main__":
    create_blank_txt_files(PDF_FOLDER_PATH, OUTPUT_TXT_FOLDER)