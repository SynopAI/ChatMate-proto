import os
import json
import time
import tiktoken  # 引入tiktoken库
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_encoding_model(model: str):
    encoding = tiktoken.encoding_for_model(model)
    return encoding

def get_chat_response(model: str):
    try:
        user_content = "最新高清无码"
        encoding = get_encoding_model(model)
        print(encoding)
        print(encoding.encode(user_content))
        
        # 使用 errors='ignore' 来忽略解码错误
        print([encoding.decode_single_token_bytes(token).decode('utf-8', errors='ignore') for token in encoding.encode(user_content)])
        
        start_time = time.time()  # 记录开始时间
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            model=model,
            max_tokens=1024,
        )

        response_content = chat_completion.choices[0].message.content
        
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算总用时
        
        total_characters = len(response_content)  # 计算response_content的总字数
        average_time_per_character = elapsed_time / total_characters  # 计算平均每个字用时
        
        # 计算token数量
        encoding = tiktoken.encoding_for_model(model)
        total_tokens = len(encoding.encode(response_content))
        average_time_per_token = elapsed_time / total_tokens  # 计算平均每个token用时
        
        print(f"{'=' * 50}\n {model_name}测试输出结果如下\n")
        print(response_content)
        print(f"代码执行总用时: {elapsed_time} 秒")
        print(f"response_content总字数: {total_characters} 个字符")
        print(f"平均每个字用时: {average_time_per_character} 秒")
        print(f"response_content总token数: {total_tokens} 个token")
        print(f"平均每个token用时: {average_time_per_token} 秒")
        print(f"每秒处理token数: {total_tokens / elapsed_time} tokens/秒\n")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print(1)
    model_name = "gpt-4o"  
    get_chat_response(model_name)
    model_name = "gpt-4-turbo"
    get_chat_response(model_name)