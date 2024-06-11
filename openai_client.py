# openai_client.py
import os
import logging
from openai import OpenAI
from PIL import ImageGrab
import base64
from config import Config
from chat_manager import get_message
from audio_player import tts, play_audio
from logging_config import setup_logging

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

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot = screenshot.convert("RGB")  # Convert RGBA to RGB
        screenshot_path = os.path.join(Config.TEMP_DIR, 'screenshot.jpg')
        screenshot.save(screenshot_path)
        # print(f"Screenshot taken and saved as {screenshot_path}.")
        return screenshot_path
    except Exception as e:
        logging.error(f"Screenshot error: {e}")
        return None

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"Image encoding error: {e}")
        return None

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
        {"type": "image_url", "image_url": {
            "url": f"data:image/jpg;base64,{base64_image}"}
        }
    ]
    
    get_message(Config.MODEL_NAME, user_content, history=Config.HISTORY, max_history_length=Config.MAX_HISTORY_LENGTH)