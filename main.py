# main.py
import os
import tkinter as tk
import threading
import logging
from openai import OpenAI
from pynput import keyboard
from config import Config
from tool_func import tools, grab_web, open_browser_search, call_tool_function
from dotenv import load_dotenv
from logging_config import setup_logging
from audio_player import stream_tts
from markdown_text import apply_markdown
from audio_recorder import start_recording, stop_recording
from utils import take_screenshot, encode_image

setup_logging()
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 创建一个事件来控制主线程等待
audio_finished_event = threading.Event()
is_recording = False

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
            stream=True,
            tools=tools,
            tool_choice="auto"
        )

        response_content = []
        buffer = ""
        tool_called = False
        
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            tool_calls = chunk.choices[0].delta.tool_calls
            
            if tool_calls:
                tool_function_name = tool_calls[0].function.name
                tool_query_string = eval(tool_calls[0].function.arguments)['query']
                tool_result = call_tool_function(tool_function_name, tool_query_string)
                
                response_content.append("已调用")
                tool_called = True
                break
            
            if content:
                print(content, end='', flush=True)
                response_content.append(content)
                buffer += content

        if not tool_called:
            # 清空 text_area
            text_area.config(state=tk.NORMAL)
            text_area.delete('1.0', tk.END)
            text_area.config(state=tk.DISABLED)

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