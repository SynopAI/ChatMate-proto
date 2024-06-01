import requests
import sounddevice as sd
import numpy as np
from pynput import keyboard
import time
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import ImageGrab
import base64
from pydub import AudioSegment
from pydub.playback import play
import threading
import logging
import tempfile
import shutil

# 创建一个事件来控制主线程等待
audio_finished_event = threading.Event()

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Audio recording parameters
RATE = 44100
CHANNELS = 1
DURATION = 5  # seconds

# 自动查找 FFmpeg 路径
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    AudioSegment.ffmpeg = ffmpeg_path
else:
    logging.error("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
    raise EnvironmentError("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")

# Flag to control recording
is_recording = False
recording = []

# 临时目录路径
temp_dir = tempfile.gettempdir()

def start_recording():
    global is_recording, recording
    is_recording = True
    recording = []
    
    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())
    
    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, callback=callback):
            print("Recording...")
            while is_recording:
                sd.sleep(100)
    except Exception as e:
        logging.error(f"Recording error: {e}")
    
    print("Finished recording.")
    audio_data = np.concatenate(recording, axis=0)
    output_path = os.path.join(temp_dir, 'output.wav')
    write(output_path, RATE, audio_data)
    
    # Transcribe audio to text
    transcribe_audio(output_path)

def stop_recording():
    global is_recording
    is_recording = False

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
        screenshot_path = os.path.join(temp_dir, 'screenshot.jpg')
        screenshot.save(screenshot_path)
        print(f"Screenshot taken and saved as {screenshot_path}.")
        return screenshot_path
    except Exception as e:
        logging.error(f"Screenshot error: {e}")
        return None

def on_press(key):
    try:
        if key == keyboard.Key.ctrl:
            if not is_recording:
                threading.Thread(target=start_recording).start()
    except AttributeError:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.ctrl:
            if is_recording:
                stop_recording()
    except AttributeError:
        pass

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"Image encoding error: {e}")
        return None

def tts(text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "tts-1-1106",
                "input": text,
                "voice": "echo",
            },
        )

        audio = b""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            audio += chunk
        # Save the audio file
        response_path = os.path.join(temp_dir, 'response.wav')
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

def get_message(model: str, user_content):
    try:
        history =[]
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
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
        full_response = ''.join(response_content)
        response_path = tts(full_response)
        if response_path:
            play_audio(response_path)

    except Exception as e:
        logging.error(f"Chat completion error: {e}")

def pass_to_gpt(transcription_text, screenshot_path):
    if not screenshot_path:
        logging.error("No screenshot available.")
        return
    
    model_name = "gpt-4"
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
    
    get_message(model_name, user_content)

def main():
    try:
        # 启动键盘监听器
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        # 主线程等待音频播放完成
        while True:
            time.sleep(0.1)
    except Exception as e:
        logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
