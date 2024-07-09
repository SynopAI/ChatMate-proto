import os
import logging
from PIL import ImageGrab
import base64
from config import Config

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot = screenshot.convert("RGB")  # Convert RGBA to RGB
        screenshot_path = os.path.join(Config.TEMP_DIR, 'screenshot.jpg')
        screenshot.save(screenshot_path)
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