import os
import pyaudio
import wave
import time
import openai
from openai import OpenAI
import tempfile
from pynput import keyboard
import threading
from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder
import sys

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# 录音参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# 获取系统临时目录
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'audio_project')
os.makedirs(TEMP_DIR, exist_ok=True)
WAVE_OUTPUT_FILENAME = os.path.join(TEMP_DIR, 'output.wav')

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.thread = None
        self.realtimestt_text = ""
        self.realtimestt_duration = 0

    def start_recording(self):
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True,
                                      frames_per_buffer=CHUNK)
        self.frames = []
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()
        print("Recording started...")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            print("Recording stopped.")

            # 保存音频文件
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(self.frames))
            waveFile.close()

    def record(self):
        while self.recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

def process_text(text):
    # 使用回车符将光标移动到行首，然后输出新的文本
    print("实时转录文本: ", text)

def start_realtimestt():
    global recorder
    recorder.realtimestt_model = AudioToTextRecorder(
        model="base", 
        language="zh", 
        device="cpu", 
        spinner=True,
        enable_realtime_transcription=True,
        on_realtime_transcription_update=process_text
    )
    recorder.realtimestt_model.start()

def stop_realtimestt():
    global recorder
    start_time = time.time()
    recorder.realtimestt_model.stop()
    recorder.realtimestt_text = recorder.realtimestt_model.text()
    recorder.realtimestt_duration = time.time() - start_time
    recorder.realtimestt_model.shutdown()

def transcribe_with_openai_whisper(audio_file):
    openai.api_key = API_KEY
    audio_file = open(audio_file, 'rb')
    start_time = time.time()
    response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    end_time = time.time()
    transcription = response.text
    return transcription, end_time - start_time

def on_press(key):
    try:
        if key == keyboard.Key.ctrl:
            start_realtimestt()
            recorder.start_recording()
            start_realtimestt()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.ctrl:
        recorder.stop_recording()
        stop_realtimestt()
        return False  # 停止监听

if __name__ == "__main__":
    recorder = AudioRecorder()
    print("Press 'control-l' to start recording and release to stop.")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("\nRealtimeSTT Transcription: ")
    print(recorder.realtimestt_text)
    print(f"RealtimeSTT Time taken: {recorder.realtimestt_duration} seconds")

    print("Transcribing with OpenAI Whisper...")
    openai_transcription, openai_time = transcribe_with_openai_whisper(WAVE_OUTPUT_FILENAME)
    print(f"OpenAI Whisper Transcription: {openai_transcription}")
    print(f"Time taken: {openai_time} seconds")