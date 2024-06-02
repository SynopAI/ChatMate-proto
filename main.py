# main.py
import threading
import time
import logging
from pynput import keyboard
from audio_recorder import start_recording, stop_recording
from config import Config
from logging_config import setup_logging

setup_logging()

# 创建一个事件来控制主线程等待
audio_finished_event = threading.Event()
is_recording = False

def on_press(key):
    global is_recording
    try:
        if key == keyboard.Key.ctrl:
            if not is_recording:
                is_recording = True
                threading.Thread(target=start_recording).start()
    except AttributeError:
        pass

def on_release(key):
    global is_recording
    try:
        if key == keyboard.Key.ctrl:
            if is_recording:
                stop_recording()
                is_recording = False
    except AttributeError:
        pass

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