import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 确保调用此函数以加载环境变量
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 加载JSON文件
def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 获取特定提示信息
def get_prompt_info(config, prompt_name):
    # 从配置中获取提示信息
    prompt_info = config['prompts'].get(prompt_name, {})
    return prompt_info['content'] if 'content' in prompt_info else ""

# 使用示例
if __name__ == "__main__":
    # 加载配置文件
    config = load_json_file('config.json')
    
    # 获取特定的提示信息
    prompt_name = 'get_web_url_prompt'
    prompt_info = get_prompt_info(config, prompt_name)

    user_input = "请查看并总结一下这个网站的内容：https://github.com/trending"

    try:
        # 使用获取的网页内容作为请求内容
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "assistant",
                    "content": "你需要严格执行以下步骤进行回答" + prompt_info,
                },
                {
                    "role": "user",
                    "content": user_input + "你需要严格执行以下步骤进行回答" + prompt_info,
                }
            ],
            model="gpt-3.5-turbo",
            max_tokens=1024,
        )

        # 提取并打印出返回的聊天内容
        response_content = chat_completion.choices[0].message.content
        print(response_content)
    except Exception as e:
        print(f"发生错误: {e}")