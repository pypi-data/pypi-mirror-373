import subprocess
import httpx
from packaging import version
from xcmap.utils import cmd_util, decorator_util
import asyncio


def get_current_version(package_name):
    current_version_cmd = f'poetry show {package_name}'
    result = asyncio.run(cmd_util.run_command(current_version_cmd))
    # result = subprocess.run(["poetry", "show", package_name], capture_output=True, text=True)
    if result.get('returncode') == 0:
        return result.get('stdout').splitlines()[1].split()[2]
    raise RuntimeError(f"Error checking package version: {result.get('stderr')}")


@decorator_util.retry(max_retries=3, delay=3)
def check_package_update(package_name, current_version):
    if not current_version:
        print(f"未找到 {package_name}")
        return None
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = httpx.get(url, timeout=10)
    try:
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            if version.parse(latest_version) > version.parse(current_version):
                print(f"{package_name} 有更新：{current_version} -> {latest_version}")
                return True
            else:
                print(f"{package_name} 已为最新版本。")
                return False
        return False
    except Exception as e:
        print(f"检查 {package_name} 版本时出错：{e}")
        raise RuntimeError(f"Error checking package version: {e}")


@decorator_util.retry(max_retries=3, delay=3)
def update_package(package_name, current_version):
    # result = subprocess.run(
    #     ["poetry", "cache", "clear", f"pypi:{package_name}:{current_version}", " --no-interaction"],
    #     input="\n",  # 发送回车确认
    #     text=True,
    #     capture_output=True,
    #     shell=True  # Windows 需要 shell=True
    # )
    # if result.stderr:
    #     print("Cache clear Error:", result.stderr)
    #     raise RuntimeError(f"Error clearing cache: {result.stderr}")
    result = subprocess.run(["poetry", "update", package_name, " --no-cache "], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error updating package: {result.stderr}")
        raise RuntimeError(f"Error updating package: {result.stderr}")
