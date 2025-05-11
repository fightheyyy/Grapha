import docx2txt

# 提取 Word 文档中的文本
text = docx2txt.process("住宅专项维修资金管理办法-文字版.docx")

# 以 UTF-8 编码写入到 output2.txt 文件中
with open("output2.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("已提取全文并保存到 output2.txt")