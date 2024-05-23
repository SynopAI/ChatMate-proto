import pyautogui
import time
import threading
from pynput import keyboard

# 指定点击的坐标
x, y = 1402, 777  # 你需要点击的屏幕坐标

# 指定点击的间隔时间（以秒为单位）
interval = 0.05  # 每0.5秒点击一次

# 指定总运行时间（以秒为单位）
total_time = 600  # 程序总共运行的时间

# 标记程序是否应该继续运行
running = True

def click_forever():
    global running
    start_time = time.time()
    click_count = 0
    print("点击线程已启动")
    
    while running and time.time() - start_time < total_time:
        pyautogui.click(x, y)  # 点击指定坐标
        click_count += 1
        print(f"点击第 {click_count} 次，坐标 ({x}, {y})")
        time.sleep(interval)  # 等待指定的间隔时间

    print("时间到，点击线程已终止")

def on_press(key):
    global running
    try:
        if key == keyboard.Key.enter:
            running = False
            print("检测到回车键，键盘监控线程已终止")
            return False  # 停止监听
    except AttributeError:
        pass

# 创建并启动点击线程
click_thread = threading.Thread(target=click_forever)
click_thread.start()
print("点击线程已启动")

# 启动键盘监听
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# 等待点击线程结束
click_thread.join()
print("所有线程已结束")