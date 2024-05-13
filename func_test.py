import os
import requests
from flask import Flask, Response
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 获取API密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key is not set in the environment variables")

# 获取API密钥
web_summary_prompts = os.getenv("WEB_SUMMARY_PROMPTS")
if not web_summary_prompts:
    raise ValueError("WEB_SUMMARY_PROMPTS is not set in the environment variables")

client = OpenAI(api_key=api_key)

# 指定想要抓取的网页
# url = "https://github.com/trending"
url = "https://uniapp.dcloud.net.cn/"

# 使用requests获取网页内容
response = requests.get(url)
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取所有项目的标题和描述
    projects = soup.find_all('article', class_='Box-row')
    summaries = []
    for project in projects:
        title_tag = project.find('h1', class_='h3 lh-condensed')
        description_tag = project.find('p', class_='col-9 color-fg-muted my-1 pr-4')
        
        title = title_tag.text.strip() if title_tag else 'No title'
        description = description_tag.text.strip() if description_tag else 'No description'
        
        summaries.append(f"Title: {title}, Description: {description}")
    
    web_content = " ".join(summaries)
    # print(web_content)
else:
    print("Failed to retrieve the web page")
    web_content = "Failed to retrieve content"

try:
    # 使用获取的网页内容作为请求内容
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": web_summary_prompts + web_content,
            }
        ],
        model="gpt-4-turbo",
        max_tokens=1024,
    )

    # 提取并打印出返回的聊天内容
    response_content = chat_completion.choices[0].message.content
    print(response_content)

except Exception as e:
    print(f"An error occurred: {e}")