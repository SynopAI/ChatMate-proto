import os
from dotenv import load_dotenv
from openai import OpenAI

import base64
from PIL import Image
import io

load_dotenv()  
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_message(model: str, user_content):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user","content": user_content}
            ],
            model=model
        )
        response_content = chat_completion.choices[0].message.content
        
        print(response_content)

    except Exception as e:
        print(f"发生错误: {e}")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

if __name__ == "__main__":
    model_name = "gpt-4o"

    file_path = './static/food.jpeg'
    base64_image = encode_image(file_path)
    # file_path = 'http://ai.yucheng.life/upload/07002-e4a30e4607.webp'
    # file_path = 'https://cdn1.mre.red/piclist/2024-04-1712502688.webp'

    user_content = [
            {"type": "text", "text": "给我描述一下图片的内容"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpg;base64,{base64_image}"}
            }
        ]

    get_message(model_name, user_content)