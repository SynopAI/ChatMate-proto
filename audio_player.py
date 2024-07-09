# audio_player.py
import os
from logging_config import setup_logging
from openai import OpenAI
from dotenv import load_dotenv
import pyaudio

setup_logging()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def stream_tts(text):
    p = pyaudio.PyAudio()
    stream = p.open(format=8,
                    channels=1,
                    rate=24_000,
                    output=True)

    with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="pcm"
    ) as response:
        for chunk in response.iter_bytes(1024):
            stream.write(chunk)