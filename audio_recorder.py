# audio_recorder.py
import sounddevice as sd
import numpy as np
import os
import logging
from scipy.io.wavfile import write
from config import Config
from openai_client import transcribe_audio

recording = []
is_recording = False

def start_recording():
    global recording, is_recording
    recording = []  # 初始化录音列表
    is_recording = True
    
    def callback(indata, frames, time, status):
        if isinstance(recording, list):
            recording.append(indata.copy())
    
    try:
        with sd.InputStream(samplerate=Config.RATE, channels=Config.CHANNELS, callback=callback):
            print("\nRecording...")
            while is_recording:
                sd.sleep(100)
    except Exception as e:
        logging.error(f"Recording error: {e}")
    
    print("Finished recording.\n")
    audio_data = np.concatenate(recording, axis=0)
    output_path = os.path.join(Config.TEMP_DIR, 'output.wav')
    write(output_path, Config.RATE, audio_data)
    
    # Transcribe audio to text
    transcribe_audio(output_path)

def stop_recording():
    global is_recording
    is_recording = False