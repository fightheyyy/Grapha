import base64
from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any

# 初始化 OpenAI 异步客户端
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1 ",
    api_key="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",
)

async def gemini_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: List[Dict[str, str]] = [],
    temperature=0.1,
    max_tokens=2048,
) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://example.com ",
            "X-Title": "MyApp",
        },
        model="meta-llama/llama-3-8b-instruct:free",  # 先用这个模型测试
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


# 使用 GraphRAG
from nano_graphrag import GraphRAG, QueryParam

graph_func = GraphRAG(working_dir="./dickens", llm_model_func=gemini_complete)

with open("./book.txt", encoding="utf-8") as f:
    graph_func.insert(f.read())

# Perform global graphrag search
print(graph_func.query("What are the top themes in this story?"))

# Perform local graphrag search (可选)
# print(graph_func.query("What are the top themes in this story?", param=QueryParam(mode="local")))