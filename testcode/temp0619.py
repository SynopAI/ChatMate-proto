import speech_recognition as sr
import pyautogui
import time
import sounddevice as sd
import numpy as np
# from pypinyin import lazy_pinyin
from xpinyin import Pinyin

def take_screenshot():
    # 使用pyautogui进行截图并保存
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    print("Screenshot taken and saved as screenshot.png")

def recognize_speech_from_mic(recognizer, duration=5):
    """Transcribe speech from recorded from `microphone`."""
    # Record audio for the given duration
    fs = 44100  # Sample rate
    print("Listening for the keyword...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    # Convert the recorded audio to AudioData
    audio_data = sr.AudioData(np.array(audio, dtype='int16').tobytes(), fs, 2)

    # Try recognizing the speech in the recording
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio_data, language="zh-CN")
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def main():
    p = Pinyin()
    recognizer = sr.Recognizer()
    target_pinyin = p.get_pinyin("小容", splitter=" ").split()

    while True:
        print("Listening...")
        response = recognize_speech_from_mic(recognizer)

        if response["transcription"]:
            print(f"Recognized: {response['transcription']}")
            if p.get_pinyin(response["transcription"], splitter=" ").split() == target_pinyin:
                take_screenshot()
        elif response["error"]:
            print(f"Error: {response['error']}")

        time.sleep(1)  # avoid too frequent polling

if __name__ == "__main__":
    main()