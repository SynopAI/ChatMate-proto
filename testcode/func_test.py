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

def load_config():
    # 加载环境变量
    load_dotenv()

    # 读取选择器配置
    with open('selectors.json', 'r') as file:
        selector_config = json.load(file)

    # 获取环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    web_summary_model = os.getenv("WEB_SUMMARY_MODEL")
    web_summary_prompts = os.getenv("WEB_SUMMARY_PROMPTS")

    # 检查环境变量
    if not api_key or not web_summary_model or not web_summary_prompts:
        raise ValueError("Please set all required environment variables (OPENAI_API_KEY, WEB_SUMMARY_MODEL, WEB_SUMMARY_PROMPTS)")

    return api_key, web_summary_model, web_summary_prompts, selector_config

api_key, web_summary_model, web_summary_prompts, selector_config = load_config()

client = OpenAI(api_key=api_key)

# 指定想要抓取的网页
# url = "   "
# url = "https://uniapp.dcloud.net.cn/"
# url = "https://ollama.com/library?sort=popular"
url = "https://github.com/DIYgod/RSSHub"

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