import os
import win32com.client
import winreg

import requests, subprocess, time
from contextlib import contextmanager

from .fun_base import log, create_file_path

default_chrome_user_data = 'D:\chrome_user_data'

def set_chrome_system_path():
    path = os.path.dirname(find_software_install_path('chrome'))
    add_to_system_path(path)

def add_to_system_path(path: str, scope: str = "user"):
    """
    将指定路径添加到系统环境变量 Path 中
    :param path: 要添加的路径（应为绝对路径）
    :param scope: 'user' 表示用户变量，'system' 表示系统变量（需要管理员权限）
    """
    if not os.path.isabs(path):
        raise ValueError("必须提供绝对路径")

    path = os.path.normpath(path)

    if scope == "user":
        root = winreg.HKEY_CURRENT_USER
        subkey = r"Environment"
    elif scope == "system":
        root = winreg.HKEY_LOCAL_MACHINE
        subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    else:
        raise ValueError("scope 参数必须是 'user' 或 'system'")

    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            current_path, _ = winreg.QueryValueEx(key, "Path")
            paths = current_path.split(";")

            if path in paths:
                print("路径已存在于 Path 中，无需添加: ", path)
                return False

            new_path = current_path + ";" + path
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print("✅ 路径已成功添加到Path中: ", new_path)
            return True

    except PermissionError:
        print("❌ 权限不足，系统变量修改需要管理员权限")
        return False
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False

def find_software_install_path(app_keyword: str):
    """从开始菜单或桌面查找指定软件的安装路径"""
    possible_dirs = [
        os.environ.get('PROGRAMDATA', '') + r'\Microsoft\Windows\Start Menu\Programs',
        os.environ.get('APPDATA', '') + r'\Microsoft\Windows\Start Menu\Programs',
        os.environ.get('USERPROFILE', '') + r'\Desktop',
        os.environ.get('PUBLIC', '') + r'\Desktop'
    ]

    shell = win32com.client.Dispatch("WScript.Shell")

    for base_dir in possible_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.lnk') and app_keyword.lower() in file.lower():
                    lnk_path = os.path.join(root, file)
                    try:
                        shortcut = shell.CreateShortcut(lnk_path)
                        target_path = shortcut.Targetpath
                        if os.path.exists(target_path):
                            return target_path
                    except Exception as e:
                        continue

    log(f'未能查找到{str}安装位置')
    return None

def init_chrome_env(account_list):
    target = find_software_install_path('chrome')
    for account in account_list:
        store_key, port, *rest = account
        user_data = rest[0] if rest and rest[0] else fr'{default_chrome_user_data}\{port}'
        create_file_path(user_data)
        args = fr'--remote-debugging-port={port} --user-data-dir="{user_data}"'
        shortcut_name = f'{port}_{store_key}.lnk'
        create_shortcut_on_desktop(target_path=target, arguments=args, shortcut_name=shortcut_name)

def create_shortcut_on_desktop(target_path, arguments='', shortcut_name='MyShortcut.lnk', icon_path=None):
    """
    在桌面上创建快捷方式，若已存在指向相同 target + arguments 的快捷方式，则跳过创建。
    """
    # 获取当前用户桌面路径
    desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')

    shell = win32com.client.Dispatch('WScript.Shell')

    # 检查是否已有相同目标的快捷方式
    for file in os.listdir(desktop_path):
        if file.lower().endswith('.lnk'):
            shortcut_file = os.path.join(desktop_path, file)
            shortcut = shell.CreateShortCut(shortcut_file)
            if (os.path.normpath(shortcut.Targetpath) == os.path.normpath(target_path)
                    and shortcut.Arguments.strip() == arguments.strip()):
                log("已存在指向该 target + args 的快捷方式，跳过创建")
                return

    # 创建新的快捷方式
    shortcut_path = os.path.join(desktop_path, shortcut_name)
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    if icon_path:
        shortcut.IconLocation = icon_path
    shortcut.save()
    log(f"已创建快捷方式：{shortcut_path}")

def check_chrome_dev(port=3000):
    try:
        url = f"http://127.0.0.1:{port}/json"
        response = requests.get(url, timeout=5)  # 设置超时，避免长时间等待
        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    # print("接口返回了数据：", data)
                    print("接口返回了数据：")
                    return True
                else:
                    print("接口返回了空数据")
                    return False
            except ValueError:
                print("返回的不是有效的 JSON")
                return False
        else:
            print(f"接口返回了错误状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"请求接口时发生错误: {e}")
        return False

def is_chrome_running():
    try:
        output = subprocess.check_output('tasklist', shell=True, text=True)
        return 'chrome.exe' in output.lower()
    except subprocess.CalledProcessError:
        return False

@contextmanager
def get_chrome_page_v3(p, port=3000, user_data=None):
    browser = context = page = None
    is_custom_chrome_opened = False  # 标记是否是程序自己开的浏览器

    try:
        if not check_chrome_dev(port):
            set_chrome_system_path()
            chrome_path = r'"chrome.exe"'
            debugging_port = fr"--remote-debugging-port={port}"
            if user_data is not None:
                chrome_user_data = fr'--user-data-dir="{user_data}"'
            else:
                chrome_user_data = fr'--user-data-dir="{create_file_path(default_chrome_user_data)}\{port}"'

            disable_webrtc = "--disable-features=WebRTC"
            disable_webrtc_hw_encoder = "--disable-features=WebRTC-HW-ENCODER"
            disable_webrtc_alt = "--disable-webrtc"
            start_maximized = "--start-maximized"

            command = f"{chrome_path} {debugging_port} {chrome_user_data} {disable_webrtc} {disable_webrtc_hw_encoder} {disable_webrtc_alt}"
            subprocess.Popen(command, shell=True)
            is_custom_chrome_opened = True
            time.sleep(1)

        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        yield browser, context, page

    except Exception as e:
        # 向上抛出错误，否则主函数感知不到错误
        raise

    finally:
        for obj in [("page", page), ("context", context), ("browser", browser)]:
            name, target = obj
            try:
                if target and is_custom_chrome_opened:
                    log(f'关闭: {name}')
                    target.close()
            except Exception:
                pass  # 你可以在这里加日志记录关闭失败
