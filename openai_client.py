import os
import logging
from openai import OpenAI
from config import Config
from logging_config import setup_logging
from utils import take_screenshot, encode_image
from main import get_message

setup_logging()

client = OpenAI(api_key=Config.API_KEY)

def transcribe_audio(audio_path):
    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
        )
        
        # Take screenshot after transcription is done
        screenshot_path = take_screenshot()
        
        # Pass transcription text and screenshot to GPT model
        pass_to_gpt(transcription.text, screenshot_path)
    except Exception as e:
        logging.error(f"Transcription error: {e}")

def pass_to_gpt(transcription_text, screenshot_path):
    if not screenshot_path:
        logging.error("No screenshot available.")
        return
    
    base64_image = encode_image(screenshot_path)
    
    if not base64_image:
        logging.error("Failed to encode image.")
        return
    
    user_content = [
        {"type": "text", "text": transcription_text},
        {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{base64_image}", "detail": "high"}}
    ]
    
    get_message(Config.MODEL_NAME, user_content, history=Config.HISTORY, max_history_length=Config.MAX_HISTORY_LENGTH)