import sounddevice as sd
import numpy as np
from pynput import keyboard
import threading
import time
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import ImageGrab

load_dotenv()  
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Audio recording parameters
RATE = 44100
CHANNELS = 1
DURATION = 5  # seconds

# Flag to control recording
is_recording = False
recording = []

def start_recording():
    global is_recording, recording
    is_recording = True
    recording = []
    
    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())
    
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, callback=callback):
        print("Recording...")
        while is_recording:
            sd.sleep(100)
    
    print("Finished recording.")
    audio_data = np.concatenate(recording, axis=0)
    write('./temp/output.wav', RATE, audio_data)
    
    # Transcribe audio to text
    transcribe_audio()

def stop_recording():
    global is_recording
    is_recording = False

def transcribe_audio():
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=open('./temp/output.wav', "rb"),
    )
    print("Transcription: ", transcription.text)

def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot = screenshot.convert("RGB")  # Convert RGBA to RGB
    screenshot.save('./temp/screenshot.jpg')
    print("Screenshot taken and saved as screenshot.jpg.")

def on_press(key):
    try:
        if key == keyboard.Key.ctrl:
            if not is_recording:
                threading.Thread(target=start_recording).start()
                take_screenshot()
    except AttributeError:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.ctrl:
            if is_recording:
                stop_recording()
    except AttributeError:
        pass

# Start listening to the keyboard
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Keep the program running
while True:
    time.sleep(0.1)