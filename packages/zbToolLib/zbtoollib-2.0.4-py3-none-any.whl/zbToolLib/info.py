import os
import sys

USER_PATH = os.path.expanduser("~")  # 系统用户路径
REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}  # 程序默认网络请求头
if sys.platform == "win32":
    SYSTEM_TYPE = "Windows"
    SYSTEM_VERSION = [sys.getwindowsversion().major, sys.getwindowsversion().minor, sys.getwindowsversion().build]
elif sys.platform == "darwin":
    SYSTEM_TYPE = "MacOS"
    SYSTEM_VERSION = [sys.version_info.major, sys.version_info.minor, sys.version_info.micro]
elif sys.platform.startswith("linux"):
    SYSTEM_TYPE = "Linux"
    SYSTEM_VERSION = [sys.version_info.major, sys.version_info.minor, sys.version_info.micro]
else:
    SYSTEM_TYPE = "Unknown"
    SYSTEM_VERSION = [0, 0, 0]

if SYSTEM_TYPE == "Windows":
    from winreg import QueryValueEx, OpenKey, HKEY_CURRENT_USER


    def DESKTOP_PATH():
        return QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]


    def DOWNLOAD_PATH():
        return QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "{374DE290-123F-4565-9164-39C4925E467B}")[0]
