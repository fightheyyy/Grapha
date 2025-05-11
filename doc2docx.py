import os

# 获取当前工作目录
current_directory = "mohurd_word_documents"

# 遍历当前目录中的所有文件
for filename in os.listdir(current_directory):
    # 检查文件是否以 .doc 结尾
    if filename.endswith(".doc"):
        # 获取文件名和扩展名
        base_name, extension = os.path.splitext(filename)

        # 构造新的文件名，将 .doc 替换为 .docx
        new_filename = f"{base_name}.docx"

        # 重命名文件
        old_path = os.path.join(current_directory, filename)
        new_path = os.path.join(current_directory, new_filename)
        os.rename(old_path, new_path)

        print(f"已重命名: {filename} -> {new_filename}")

print("✅ 所有 .doc 文件已成功更改为 .docx 后缀。")