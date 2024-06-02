# audio_player.py
import os
import requests
import logging
from pydub import AudioSegment
from pydub.playback import play
import threading
from config import Config
from logging_config import setup_logging

setup_logging()

audio_finished_event = threading.Event()

def tts(text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {Config.API_KEY}",
            },
            json={
                "model": Config.TTS_MODEL,
                "input": text,
                "voice": Config.TTS_VOICE,
            },
        )

        audio = b""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            audio += chunk
        # Save the audio file
        response_path = os.path.join(Config.TEMP_DIR, 'response.wav')
        with open(response_path, "wb") as audio_file:
            audio_file.write(audio)
        return response_path
    except Exception as e:
        logging.error(f"TTS error: {e}")
        return None

def play_audio_thread(file_path):
    try:
        audio = AudioSegment.from_mp3(file_path)
        play(audio)
        audio_finished_event.set()  # 设置事件，表示音频播放完成
        print("Audio playback finished.")
    except Exception as e:
        logging.error(f"Audio playback error: {e}")

def play_audio(file_path):
    # 创建并启动一个新的线程来播放音频
    audio_thread = threading.Thread(target=play_audio_thread, args=(file_path,))
    audio_thread.start()