import sounddevice as sd
import numpy as np
from pynput import keyboard
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import ImageGrab
import base64
from pydub import AudioSegment
import threading
import logging
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog
import re
import pyaudio

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

control_pressed = False

def start_recording():
    global is_recording, recording
    is_recording = True
    recording = []
    
    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())
    
    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, callback=callback):
            print("\nRecording...")
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

def check_long_press():
    global control_pressed, is_recording
    if control_pressed and not is_recording:
        message_entry.delete(0, tk.END)
        message_entry.insert(0, "Listening...")
        message_entry.config(fg='gray')
        root.update_idletasks()
        threading.Thread(target=start_recording).start()

def on_press(key):
    global control_pressed
    try:
        if key == keyboard.Key.ctrl:
            control_pressed = True
            root.after(500, check_long_press)  # Check after 500ms
        elif key == keyboard.Key.caps_lock:
            # Ignore Caps Lock key
            return
    except AttributeError:
        pass

def on_release(key):
    global control_pressed, is_recording
    try:
        if key == keyboard.Key.ctrl:
            control_pressed = False
            if is_recording:
                stop_recording()
            message_entry.delete(0, tk.END)
            message_entry.config(fg='black')
        elif key == keyboard.Key.caps_lock:
            # Ignore Caps Lock key
            return
    except AttributeError:
        pass

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"Image encoding error: {e}")
        return None
    
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

def apply_markdown(text):
    formatted_text = []
    lines = text.split('\n')
    in_code_block = False
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                formatted_text.append(('code_start', line + '\n'))
            else:
                formatted_text.append(('code_end', line + '\n'))
            continue
        
        if in_code_block:
            formatted_text.append(('code', line + '\n'))
            continue
        
        # Headers
        header_match = re.match(r'^(#{1,6})\s(.+)', line)
        if header_match:
            level = len(header_match.group(1))
            formatted_text.append((f'h{level}', header_match.group(2) + '\n'))
            continue
        
        # Process inline elements
        processed_line = []
        remaining_line = line
        
        while remaining_line:
            # Links
            link_match = re.match(r'\[([^\]]+)\]\(([^\)]+)\)', remaining_line)
            if link_match:
                processed_line.append(('link', link_match.group(1)))
                remaining_line = remaining_line[link_match.end():]
                continue
            
            # Inline code
            code_match = re.match(r'`([^`]+)`', remaining_line)
            if code_match:
                processed_line.append(('inline_code', code_match.group(1)))
                remaining_line = remaining_line[code_match.end():]
                continue
            
            # Bold and Italic
            bold_italic_match = re.match(r'\*\*\*([^\*]+)\*\*\*', remaining_line)
            if bold_italic_match:
                processed_line.append(('bold italic', bold_italic_match.group(1)))
                remaining_line = remaining_line[bold_italic_match.end():]
                continue
            
            bold_match = re.match(r'\*\*([^\*]+)\*\*', remaining_line)
            if bold_match:
                processed_line.append(('bold', bold_match.group(1)))
                remaining_line = remaining_line[bold_match.end():]
                continue
            
            italic_match = re.match(r'\*([^\*]+)\*', remaining_line)
            if italic_match:
                processed_line.append(('italic', italic_match.group(1)))
                remaining_line = remaining_line[italic_match.end():]
                continue
            
            # Normal text
            normal_match = re.match(r'[^\[\*`]+', remaining_line)
            if normal_match:
                processed_line.append(('normal', normal_match.group(0)))
                remaining_line = remaining_line[normal_match.end():]
                continue
            
            # If no match found, add the first character as normal text
            processed_line.append(('normal', remaining_line[0]))
            remaining_line = remaining_line[1:]
        
        # Blockquotes
        if line.startswith('>'):
            formatted_text.append(('quote', line[1:].strip() + '\n'))
        else:
            formatted_text.extend(processed_line)
            if line != lines[-1]:  # Only add a newline if it's not the last line
                formatted_text.append(('normal', '\n'))
    
    return formatted_text

def get_message(model: str, user_content, history: list, max_history_length: int = 3):
    try:
        # Append the new user message to the history
        history.append({"role": "user", "content": user_content})

        # Ensure the history does not exceed the maximum length
        if len(history) > max_history_length:
            history = history[-max_history_length:]

        # Add the system message to the beginning of the history
        messages = [{"role": "system", "content": "All your replies are prohibited from using markdown format"}] + history

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            stream=True
        )

        # 清空 text_area
        text_area.config(state=tk.NORMAL)
        text_area.delete('1.0', tk.END)
        text_area.config(state=tk.DISABLED)

        response_content = []
        buffer = ""
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
                response_content.append(content)
                
                buffer += content
                
                # 检查是否有完整的段落或句子
                if '\n' in buffer or '. ' in buffer or '。' in buffer:
                    lines = buffer.splitlines(True)  # 保留换行符
                    complete_lines = lines[:-1] if lines else []
                    
                    if complete_lines:
                        complete_text = ''.join(complete_lines)
                        formatted_content = apply_markdown(complete_text)
                        text_area.config(state=tk.NORMAL)
                        for tag, text in formatted_content:
                            text_area.insert(tk.END, text, tag)
                        text_area.config(state=tk.DISABLED)
                        text_area.see(tk.END)
                        root.update_idletasks()
                        
                        buffer = lines[-1] if lines else ""

        # 插入剩余的内容
        if buffer:
            formatted_content = apply_markdown(buffer)
            text_area.config(state=tk.NORMAL)
            for tag, text in formatted_content:
                text_area.insert(tk.END, text, tag)
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)
            root.update_idletasks()

        # Append the assistant's response to the history
        assistant_message = ''.join(response_content)
        history.append({"role": "assistant", "content": assistant_message})

        # Ensure the history does not exceed the maximum length again
        if len(history) > max_history_length:
            history = history[-max_history_length:]

        # stream tts
        threading.Thread(target=stream_tts, args=(assistant_message,)).start()

        return history  # Return the updated history

    except Exception as e:
        logging.error(f"Chat completion error: {e}")
        return history  # Return the history even in case of error

def pass_to_gpt(transcription_text, screenshot_path):
    if not screenshot_path:
        logging.error("No screenshot available.")
        return
    
    model_name = "gpt-4o"
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
    
    get_message(model_name, user_content, history)

def send_message_to_gpt(message):
    try:
        text_area.grid()
        
        text_area.config(state=tk.NORMAL)  # Temporarily enable editing
        text_area.delete('1.0', tk.END)
        text_area.config(state=tk.DISABLED)  # Disable editing again
        
        # Add a "Thinking..." message
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, "Thinking...\n", 'italic')
        text_area.config(state=tk.DISABLED)
        root.update_idletasks()  # Force update of the GUI
        
        screenshot_path = take_screenshot()
        if not screenshot_path:
            logging.error("No screenshot available.")
            return
        base64_image = encode_image(screenshot_path)
        if not base64_image:
            logging.error("Failed to encode image.")
            return
        user_content = [
            {"type": "text", "text": message},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpg;base64,{base64_image}"}
            }
        ]
        global history
        
        # Clear the "Thinking..." message
        text_area.config(state=tk.NORMAL)
        text_area.delete('1.0', tk.END)
        text_area.config(state=tk.DISABLED)
        
        history = get_message("gpt-4o", user_content, history)
    except Exception as e:
        logging.error(f"Error sending message to GPT: {e}")

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as file:
            file_content = file.read()
        send_message_to_gpt(file_content)

def on_enter(event):
    message = message_entry.get()
    if message.strip():  # 只处理非空消息
        message_entry.config(fg='gray')  # 将文本颜色改为灰色
        root.update_idletasks()  # 强制更新 GUI
        send_message_to_gpt(message)
        message_entry.delete(0, tk.END)  # 清空输入框
        root.after(1000, reset_entry_color)  # 1秒后重置颜色

def reset_entry_color():
    message_entry.config(fg='black')  # Reset text color to black

def on_entry_key_press(event):
    if message_entry.cget('fg') == 'gray':
        message_entry.delete(0, tk.END)  # 清除任何现有文本
        message_entry.config(fg='black')  # 将文本颜色重置为白色

def toggle_text_area():
    global text_area, text_area_visible
    if text_area_visible:
        text_area.grid_remove()
    else:
        text_area.grid()
    text_area_visible = not text_area_visible

def create_gui():
    global text_area, root, message_entry, text_area_visible

    root = tk.Tk()
    root.title("Chat-Mate")
    root.grid_columnconfigure(1, weight=1)

    message_entry = tk.Entry(root, fg='black', bg='#f8f8f8')
    message_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
    message_entry.bind("<Return>", on_enter)
    message_entry.bind("<Key>", on_entry_key_press)

    # Add this line to create a hidden button
    hidden_button = tk.Button(root,text="⌆" , command=toggle_text_area)
    hidden_button.grid(row=0, column=0, padx=10, pady=10)

    # Bind the hidden button to a key combination (Ctrl+H in this example)
    root.bind("<Command-Shift-h>", lambda event: toggle_text_area())
    root.bind("<KeyRelease-Control_L>", lambda event: on_release(keyboard.Key.ctrl))

    # Initialize text_area_visible
    text_area_visible = False

    # Use Text widget with custom tags for Markdown rendering
    text_area = tk.Text(root, wrap=tk.WORD, width=50, height=20, padx=10, pady=10, bg="white", fg="black")
    text_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    text_area.grid_remove()
    
    # 禁用默认滚动条
    text_area.config(yscrollcommand=lambda *args: None)
    
    # Make the text area non-editable
    text_area.config(state=tk.DISABLED)

    # 假设 text_size 是一个变量
    text_size = 14
    
    # 设置默认字体
    default_font = ("TkDefaultFont", text_size)
    text_area.configure(font=default_font)

    # Configure tags for Markdown styling
    text_area.tag_configure("h1", font=("TkDefaultFont", text_size + 14, "bold"))
    text_area.tag_configure("h2", font=("TkDefaultFont", text_size + 10, "bold"))
    text_area.tag_configure("h3", font=("TkDefaultFont", text_size + 6, "bold"))
    text_area.tag_configure("h4", font=("TkDefaultFont", text_size + 4, "bold"))
    text_area.tag_configure("h5", font=("TkDefaultFont", text_size + 2, "bold"))
    text_area.tag_configure("h6", font=("TkDefaultFont", text_size, "bold"))
    text_area.tag_configure("bold", font=("TkDefaultFont", text_size, "bold"))
    text_area.tag_configure("italic", font=("TkDefaultFont", text_size, "italic"))
    text_area.tag_configure("code", font=("Courier", text_size), background="#f0f0f0")
    text_area.tag_configure("link", foreground="blue", underline=1)
    text_area.tag_configure("list", lmargin1=20, lmargin2=20)

    message_entry.bind("<Return>", on_enter)

    # Configure row and column weights
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    root.mainloop()

def main():
    try:
        global text_area_visible
        text_area_visible = True

        # 启动键盘监听器
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        # 启动GUI
        create_gui()

    except Exception as e:
        logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    global history
    history = []
    main()