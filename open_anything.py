import subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# # 打开电脑上的应用程序（例如文本编辑器）
# def open_application():
#     try:
#         # macOS上打开文本编辑器
#         subprocess.Popen(['open', '-a', 'Feishu'])  # NeteaseMusic
#     except Exception as e:
#         print(f"Error opening application: {e}")

# 打开指定路径的应用程序
def open_application(app_path):
    try:
        # 使用 subprocess 打开应用程序
        subprocess.Popen(['open', app_path])
    except Exception as e:
        print(f"Error opening application: {e}")

# 控制浏览器并进行搜索
def search_in_browser(query):
    try:
        # 初始化Chrome浏览器
        driver = webdriver.Chrome()  # 确保chromedriver在你的PATH中
        driver.get("http://www.google.com")

        # 等待页面加载
        time.sleep(2)

        # 找到搜索框并输入查询
        search_box = driver.find_element_by_name("q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # 等待搜索结果加载
        time.sleep(5)
        
        # 关闭浏览器
        driver.quit()
    except Exception as e:
        print(f"Error controlling browser: {e}")

if __name__ == "__main__":
    # 打开文本编辑器
    open_application('/Applications/Lark.app/Contents/MacOS/Feishu')
    
    # # 在浏览器中搜索特定文本
    # search_query = "Python programming"
    # search_in_browser(search_query)