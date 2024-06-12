# config.py
import os
import tempfile
from dotenv import load_dotenv
from logging_config import setup_logging

setup_logging()

# Load environment variables
load_dotenv()

class Config:
    API_KEY = os.getenv("OPENAI_API_KEY")
    RATE = 44100
    CHANNELS = 1
    DURATION = 5  # seconds
    TEMP_DIR = os.path.join(tempfile.gettempdir(), 'audio_project')
    MODEL_NAME = "gpt-4o"
    TTS_MODEL = "tts-1-1106"
    TTS_VOICE = "echo"
    SYSTEM_PROMPT = "你是一个人工智能助手，我会给你一张我当前电脑屏幕的截图，并且我会问你一些问题，有可能我的问题与截图无关，你需要帮我解决我的问题，一般来说请使用简体中文回答我的问题"
    HISTORY = []
    MAX_HISTORY_LENGTH = 3

    # Ensure necessary directories exist
    os.makedirs(TEMP_DIR, exist_ok=True)