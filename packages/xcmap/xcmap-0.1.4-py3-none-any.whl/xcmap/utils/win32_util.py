import time
import tkinter as tk

import psutil
import win32gui
import win32process
from win32.lib import win32con


def activate_window_by_pid(t_pid):
    hwnd = None
    start_time = time.time()
    timeout = 30  # 设置超时时间为10秒
    while True:
        if time.time() - start_time > timeout:
            print("Operation timed out")
            break  # 退出循环
        hwnd = get_hwnd_by_pid(t_pid)
        if hwnd:
            break
        time.sleep(0.5)
    if hwnd:
        for _ in range(5):
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
                time.sleep(0.1)
                win32gui.ShowWindow(hwnd, win32con.SW_FORCEMINIMIZE)
                time.sleep(0.1)
                # 否则，显示并激活窗口
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.1)
                # win32gui.BringWindowToTop(hwnd)
                # win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
                print(f"Window with PID {t_pid} has been activated.")
                break
            except Exception as e:
                print(e)
        time.sleep(0.5)
        return True
    else:
        print(f"No window found with PID {t_pid}.")
        return False


def enum_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        windows.append((hwnd, pid, win32gui.GetWindowText(hwnd)))


def get_all_windows():
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows


def checkProcessExist(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.name() == process_name:
            return True
    return False


def check_if_already_running():
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name']):
        if process.pid != current_process.pid and process.name() == current_process.name():
            return True, current_process
    return False, None


def get_hwnd_by_pid(t_pid):
    hwnd = None
    windows = get_all_windows()
    for ahwnd, pid, title in windows:
        try:
            if pid == t_pid:
                hwnd = ahwnd
                break
        except psutil.NoSuchProcess:
            print(f"Window Title: {title}, Process ID: {pid}, Process Name: Not found")
    return hwnd


def fetch_screen_size():
    root = tk.Tk()
    window_x = root.winfo_screenwidth()
    window_y = root.winfo_screenheight()
    root.destroy()
    return window_x, window_y


# 获取屏幕个数，并标记主控屏幕
def fetch_screen_number():
    root = tk.Tk()

    # 获取程序窗口的位置信息
    window_x = root.winfo_screenwidth()
    window_y = root.winfo_screenheight()

    # 获取屏幕个数
    screen_count = root.tk.call('tk', 'windowingsystem', 'window', 'list')

    # 获取每个屏幕的位置信息
    screen_positions = [(root.winfo_x(), root.winfo_y()) for i in range(len(screen_count))]

    # 确定程序窗口所在的屏幕
    main_screen_index = 0
    for i, (x, y) in enumerate(screen_positions):
        if x <= window_x < x + root.winfo_screenwidth(
        ) and y <= window_y < y + root.winfo_screenheight():
            main_screen_index = i
            break

    print("程序窗口所在的屏幕索引:", main_screen_index)

    root.destroy()
