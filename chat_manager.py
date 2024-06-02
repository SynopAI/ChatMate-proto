# chat_manager.py
import logging
from openai import OpenAI
from config import Config
from audio_player import tts, play_audio
from logging_config import setup_logging

setup_logging()

client = OpenAI(api_key=Config.API_KEY)

def get_message(model: str, user_content):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": Config.SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            model=model,
            stream=True
        )

        response_content = []
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
                response_content.append(content)
        
        # 在独立线程中播放音频
        # full_response = ''.join(response_content)
        # response_path = tts(full_response)
        # if response_path:
        #     play_audio(response_path)
    except Exception as e:
        logging.error(f"Chat message error: {e}")