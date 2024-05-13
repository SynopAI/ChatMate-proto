import os
import requests
import json
from flask import Flask, Response
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 读取选择器配置
with open('selectors.json', 'r') as file:
    selector_config = json.load(file)

# 获取API密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key is not set in the environment variables")

# 获取网页总结使用模型
web_summary_model = os.getenv("WEB_SUMMARY_MODEL")
if not web_summary_model:
    raise ValueError("WEB_SUMMARY_MODEL is not set in the environment variables")

# 总结网页Prompt
web_summary_prompts = os.getenv("WEB_SUMMARY_PROMPTS")
if not web_summary_prompts:
    raise ValueError("WEB_SUMMARY_PROMPTS is not set in the environment variables")

client = OpenAI(api_key=api_key)

# 指定想要抓取的网页
# url = "https://github.com/trending"
# url = "https://uniapp.dcloud.net.cn/"
url = "https://ollama.com/library?sort=popular"

def fetch_web_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        site_selectors = selector_config['specific_sites'].get(url, selector_config['default'])
        
        titles = []
        for sel in site_selectors['title']:
            titles.extend(soup.select(sel))
        
        descriptions = []
        for sel in site_selectors['description']:
            descriptions.extend(soup.select(sel))
        
        summaries = []
        for title, desc in zip(titles, descriptions):
            summaries.append(f"Title: {title.text.strip()}, Description: {desc.text.strip()}")
        
        return " ".join(summaries)
    else:
        return "Failed to retrieve the web page"

# 示例URL
web_content = fetch_web_content(url)

try:
    # 使用获取的网页内容作为请求内容
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": web_summary_prompts + web_content,
            }
        ],
        model=web_summary_model,
        max_tokens=1024,
    )

    # 提取并打印出返回的聊天内容
    response_content = chat_completion.choices[0].message.content
    print(response_content)

except Exception as e:
    print(f"An error occurred: {e}")