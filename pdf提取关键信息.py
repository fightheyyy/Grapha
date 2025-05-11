import base64

from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

def encode_pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

# Read and encode the PDF
pdf_path = "1号住宅楼_1_01_结构设计总说明一 第1版1703KB.pdf"
base64_pdf = encode_pdf_to_base64(pdf_path)
data_url = f"data:application/pdf;base64,{base64_pdf}"

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="google/gemini-2.5-pro-exp-03-25",
  messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "帮我提取出里面的关键施工文本信息"
                },
                {
                    "type": "file",
                    "file": {
                        "filename": "document.pdf",
                        "file_data": data_url
                    }
                },
            ]
        }
    ]
)
print(completion.choices[0].message.content)