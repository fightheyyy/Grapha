import win32com.client as win32
import os

def convert_docx_to_txt_directly_with_word(docx_path, txt_path):
    """
    使用 Word COM 接口将 DOCX 文件直接另存为 TXT 文件。
    这应该与在 Word 中手动 "另存为 -> 纯文本" 的结果最接近。
    仅限 Windows，且需要安装 Microsoft Word。

    参数:
        docx_path (str): 输入的 DOCX 文件路径 (绝对路径)。
        txt_path (str): 输出的 TXT 文件路径 (绝对路径)。
    """
    word_app = None
    doc = None
    success = False
    try:
        abs_docx_path = os.path.abspath(docx_path)
        abs_txt_path = os.path.abspath(txt_path)

        print(f"INFO: 正在使用 Word COM 尝试将 '{abs_docx_path}' 另存为 '{abs_txt_path}'...")

        # 尝试 EnsureDispatch，它可能有助于加载类型库
        try:
            word_app = win32.gencache.EnsureDispatch("Word.Application")
        except AttributeError:  # 如果 gencache 或 EnsureDispatch 有问题，回退到 Dispatch
            print("WARN: win32.gencache.EnsureDispatch 失败，尝试 win32.Dispatch...")
            word_app = win32.Dispatch("Word.Application")

        word_app.Visible = False  # 不显示 Word 界面
        doc = word_app.Documents.Open(abs_docx_path)

        # FileFormat 参数:
        # wdFormatEncodedText 的数值是 7
        # Encoding 参数: 65001 代表 UTF-8
        doc.SaveAs2(abs_txt_path, FileFormat=7, Encoding=65001)  # <--- 修改在这里

        print(f"成功：文件已通过 Word COM 另存为 '{abs_txt_path}'")
        success = True
    except Exception as e:
        # 打印更详细的错误信息，包括错误类型
        print(f"错误类型: {type(e).__name__}")
        print(f"错误：使用 Word COM 另存为 TXT 失败 - {e}")
        if hasattr(e, 'com_error'):  # 专门处理 COM 错误
            print(f"COM Error Details: Code: {e.com_error.hresult}, Message: {e.com_error.description}")
        elif hasattr(e, 'args'):
            print(f"Error args: {e.args}")
    finally:
        if doc:
            doc.Close(False)  # False 表示不保存更改
        if word_app:
            word_app.Quit()
    return success

def batch_convert_docx_to_txt(input_folder, output_folder):
    """
    批量将一个文件夹中的所有 DOCX 文件转换为 TXT 文件，并保存到另一个文件夹中。

    参数:
        input_folder (str): 包含 DOCX 文件的输入文件夹路径。
        output_folder (str): 输出 TXT 文件的目标文件夹路径。
    """
    if not os.path.isdir(input_folder):
        print(f"错误：输入文件夹 '{input_folder}' 不存在！")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    docx_files = [f for f in os.listdir(input_folder) if f.endswith('.docx')]

    if not docx_files:
        print(f"警告：在 '{input_folder}' 中没有找到任何 DOCX 文件。")
        return

    total_files = len(docx_files)
    success_count = 0

    for index, docx_filename in enumerate(docx_files, start=1):
        docx_path = os.path.join(input_folder, docx_filename)
        txt_filename = os.path.splitext(docx_filename)[0] + "_word_saved.txt"
        txt_path = os.path.join(output_folder, txt_filename)

        print(f"\n处理文件 {index}/{total_files}: {docx_filename}")
        if convert_docx_to_txt_directly_with_word(docx_path, txt_path):
            success_count += 1

    print(f"\n批量转换完成，成功转换 {success_count} 个文件，共 {total_files} 个文件。")

# --- 使用示例 ---
if __name__ == "__main__":
    if os.name == 'nt':  # 检查是否为 Windows 系统
        # 修改为您的源文件夹和目标文件夹
        source_folder = r"mohurd_word_documentsBeifen"  # 例如：r"C:\path\to\docx\files"
        output_folder = r"法规txt"  # 例如：r"C:\path\to\output\txt\files"

        if os.path.exists(source_folder):
            batch_convert_docx_to_txt(source_folder, output_folder)
        else:
            print(f"错误：源文件夹 '{source_folder}' 不存在！")
    else:
        print("此 `win32com` 方法仅适用于 Windows 系统。")