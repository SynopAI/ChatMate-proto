# chat_manager.py
import logging
from openai import OpenAI
from config import Config
from audio_player import tts, play_audio
from logging_config import setup_logging

setup_logging()

client = OpenAI(api_key=Config.API_KEY)

def get_message(model: str, user_content, history: list, max_history_length: int = 10):
    try:
        # Append the new user message to the history
        history.append({"role": "user", "content": user_content})

        # Ensure the history does not exceed the maximum length
        if len(history) > max_history_length:
            history = history[-max_history_length:]

        # Add the system message to the beginning of the history
        messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}] + history

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            stream=True
        )

        response_content = []
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
                response_content.append(content)

        # Append the assistant's response to the history
        assistant_message = ''.join(response_content)
        history.append({"role": "assistant", "content": assistant_message})

        # Ensure the history does not exceed the maximum length again
        if len(history) > max_history_length:
            history = history[-max_history_length:]

        # 在独立线程中播放音频
        # response_path = tts(assistant_message)
        # if response_path:
        #     play_audio(response_path)

        return history  # Return the updated history

    except Exception as e:
        logging.error(f"Chat completion error: {e}")
        return history  # Return the history even in case of error