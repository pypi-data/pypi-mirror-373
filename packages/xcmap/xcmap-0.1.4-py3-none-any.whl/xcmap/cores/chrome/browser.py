import base64
import socket
import subprocess
import zlib
from subprocess import Popen
from typing import Tuple, Any, Optional

import win32gui
from DrissionPage import Chromium


BROWSER_REMOTE_RANGE = (11000, 21000)


def control_browser(remote_port, *args, **kwargs):
    browser = Chromium(f'127.0.0.1:{remote_port}')
    # 设置自动处理弹出警告框
    browser.set.auto_handle_alert(accept=False)
    return browser


def open_cmd_browser(config, browser_bin, extension=None,
                   import_cookies_file=None, export_cookies_file=None) -> Tuple[Optional[subprocess.Popen], Any]:
    remote_port = __get_available_port(BROWSER_REMOTE_RANGE)
    cmd = [rf'{browser_bin}', rf'--config={config}', rf' --remote-debugging-port={remote_port}']
    if extension:
        cmd.append(rf' --load-extension={extension}')
    if import_cookies_file:
        cmd.append(rf' --import-cookies-file={import_cookies_file}')
    if export_cookies_file:
        cmd.append(rf' --export-cookies-timely={export_cookies_file}')
    try:
        process = Popen(cmd)
        return process, remote_port
    except OSError as e:
        process = None
    return process, None


def __get_available_port(range_port):
    for port in range(range_port[0], range_port[1] + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError("没有可用的端口")


def sync_browser(hwnd, browser_type, crc_str, windows_message_id, x=0, y=0, width=500, height=400):
    """
    同步浏览器（群控）
    :param hwnd: 浏览器窗口句柄
    :param browser_type: 浏览器类型 1 表示主控浏览器 0 表示受控浏览器 只能有一个主控和N个受控
    :param crc_str: 浏览器配置文件中上定义的fpMagic值，用crc32加密后生成唯一id
    :param windows_message_id: windows中注入的CustomWindowSyncMessage消息事件，浏览器会接收该消息的内容
    :param x: 位于屏幕横轴x处
    :param y: 位于屏幕纵轴y处
    :param width 宽度
    :param height 高度
    :return:
    """
    high_id = __generate_id_by_crc32(crc_str)
    # 注册自定义消息

    # 创建窗口类和窗口
    # browser_type 主控为 1 受控为 0
    if browser_type == 1:
        lparam_1 = 2
    else:
        lparam_1 = 3
    # 设置 WPARAM 和 LPARAM
    wparam_1 = (high_id << 16) | 104  # 高16位为生成的ID，低16位为104
    # 发送控制类型消息
    win32gui.SendMessage(hwnd, windows_message_id, wparam_1, lparam_1)

    # 发送同步状态消息
    wparam_2 = (high_id << 16) | 120  # 高16位为生成的ID，低16位为104
    lparam_2 = 0
    win32gui.SendMessage(hwnd, windows_message_id, wparam_2, lparam_2)

    # # 设置坐标
    # wparam_3 = (high_id << 16) | 136
    # lparam_3 = (y << 16) | x
    # win32gui.SendMessage(hwnd, windows_message_id, wparam_3, lparam_3)
    #
    # # 设置大小
    # wparam_4 = (high_id << 16) | 152
    # lparam_4 = (height << 16) | width
    # win32gui.SendMessage(hwnd, windows_message_id, wparam_4, lparam_4)
    set_browser_size(hwnd, crc_str, windows_message_id, x, y, width, height)

    # 发送控制消息
    wparam_5 = (1 << 16) | 168  # 高16位为生成的ID，低16位为104
    lparam_5 = 0
    win32gui.SendMessage(hwnd, windows_message_id, wparam_5, lparam_5)


def set_browser_size(hwnd, crc_str, windows_message_id, x=0, y=0, width=500, height=400):
    """
    设置浏览器大小（群控）
    :param hwnd: 浏览器窗口句柄
    :param crc_str: 浏览器配置文件中上定义的fpMagic值，用crc32加密后生成唯一id
    :param windows_message_id: windows中注入的CustomWindowSyncMessage消息事件，浏览器会接收该消息的内容
    :param x: 位于屏幕横轴x处
    :param y: 位于屏幕纵轴y处
    :param width 宽度
    :param height 高度
    :return:
    """
    high_id = __generate_id_by_crc32(crc_str)

    # 设置坐标
    wparam_3 = (high_id << 16) | 136
    lparam_3 = (y << 16) | x
    win32gui.SendMessage(hwnd, windows_message_id, wparam_3, lparam_3)

    # 设置大小
    wparam_4 = (high_id << 16) | 152
    lparam_4 = (height << 16) | width
    win32gui.SendMessage(hwnd, windows_message_id, wparam_4, lparam_4)


def cancel_sync(hwnd, windows_message_id):
    wparam = (0 << 16) | 168  # 高16位为生成的ID，低16位为104
    lparam = 0
    win32gui.SendMessage(hwnd, windows_message_id, wparam, lparam)


def __generate_id_by_crc32(input_str):
    # Base64 编码
    encoded_fp_magic = base64.b64encode(input_str.encode('utf-8')).decode('utf-8')

    # 计算 CRC32
    crc_value = zlib.crc32(encoded_fp_magic.encode('utf-8'))

    # 转换为16位整数
    short_result = abs(__to_short(crc_value))  # 取CRC32结果的低16位并确保结果为非负

    return short_result


def __to_short(value):
    # 模拟 C++ 中的 (short) 类型转换
    value = value & 0xFFFF  # 取低 16 位
    if value & 0x8000:  # 如果最高位是 1，表示负数
        value -= 0x10000
    return value
