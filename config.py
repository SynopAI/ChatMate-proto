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
    SYSTEM_PROMPT = "You are a helpful assistant"

    # Ensure necessary directories exist
    os.makedirs(TEMP_DIR, exist_ok=True)