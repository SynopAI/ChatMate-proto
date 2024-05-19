import subprocess

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

if __name__ == "__main__":
    # 打开文本编辑器
    open_application('/Applications/[APPNAME].app/Contents/MacOS/[APPNAME]')