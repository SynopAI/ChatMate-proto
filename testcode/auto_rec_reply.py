from openai import OpenAI
import openai
import os
import time
import pyautogui
import azure.cognitiveservices.speech as speechsdk
import glob
import base64
import io
import threading
import soundfile as sf
import sounddevice as sd
from IPython.display import Markdown
# 缺失模块请自行"pip install ..."进行安装
# 请提前将"OPENAI_API_KEY"以及Azure的"SPEECH_KEY"和"SPEECH_REGION"写入Windows环境变量
recognized_text = None
continue_screenshot = True
screenshot_filename = None

# 自动截屏
def capture_screenshots(screenshot_path, screenshot_interval):
    global continue_screenshot, screenshot_filename
    if not os.path.exists(screenshot_path):
        os.makedirs(screenshot_path)

    while continue_screenshot:
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_filename = f'{screenshot_path}/{timestamp}.png'
        pyautogui.screenshot().save(screenshot_filename)
        print(f'Screenshot saved: {screenshot_filename}')
        time.sleep(screenshot_interval)

# Azure语音识别
def recognize_from_microphone():
    global recognized_text, continue_screenshot
    speech_config = speechsdk.SpeechConfig(subscription=os.environ['SPEECH_KEY'], region=os.environ['SPEECH_REGION'])
    speech_config.speech_recognition_language = "zh-CN"
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "zh-CN"])
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config, audio_config=audio_config)

    def recognized_handler(event):
        global recognized_text, continue_screenshot
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_text = event.result.text
            print(f"已识别语音: {recognized_text}")
            continue_screenshot = False
            speech_recognizer.stop_continuous_recognition()

    speech_recognizer.recognized.connect(recognized_handler)
    speech_recognizer.start_continuous_recognition()

    while recognized_text is None:
        time.sleep(0.5)

# 将图像编码为Base64字符串
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# OpenAI GPT-4o
def chat_response(recognized_text, base64_image):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    if recognized_text:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in Markdown."},
                {"role": "user", "content": [
                    {"type": "text", "text": recognized_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}} # "detail"可选"low"或"high"，low detail模式每张图像固定消耗85 tokens，无视图像分辨率；high detail模型下，1024x1024图像消耗765 tokens，2048x4096图像消耗1105 tokens，递增
                ]}
            ],
            temperature=0.0, max_tokens=300,
        )
        return response.choices[0].message.content

# OpenAI文本转语音
def generate_audio_stream(response_content):
    client = openai.OpenAI()
    spoken_response = client.audio.speech.create(
    model="tts-1",
    voice="shimmer", # 声音选择
    response_format="opus", # 音频格式
    input=chat_response(recognized_text, base64_image)
    )

    buffer = io.BytesIO()
    for chunk in spoken_response.iter_bytes(chunk_size=4096):
        buffer.write(chunk)

    buffer.seek(0)

    with sf.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
        sd.play(data, sound_file.samplerate)
        sd.wait()

# 主程序
if __name__ == "__main__":
    screenshot_path = '/Code/Screenshots' # 屏幕截图保存路径（相对），可自行修改
    screenshot_interval = 5 # 自动截图时间间隔（5s），可适当缩短间隔以增强图像内容时效性
    while True:
        continue_screenshot = True
        threading.Thread(target=capture_screenshots, args=(screenshot_path, screenshot_interval)).start()
        recognize_from_microphone()
        if recognized_text:
            continue_screenshot = False
            time.sleep(screenshot_interval)
            files = glob.glob(os.path.join(screenshot_path, '*.png'))
            latest_file = max(files, key=os.path.getmtime)
            base64_image = encode_image(latest_file)
            response_content = chat_response(recognized_text, base64_image)
            print(response_content)
            generate_audio_stream(response_content)
            recognized_text = None
        time.sleep(1)
