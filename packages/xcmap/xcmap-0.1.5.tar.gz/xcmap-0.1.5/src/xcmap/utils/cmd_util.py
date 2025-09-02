import asyncio
import shlex
from typing import Union, List, Dict, Optional


async def run_command(
        command: Union[str, List[str]],
        input_content=None,
        shell: bool = False,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[str, int]]:
    """
    异步执行命令并返回结果。

    :param input_content:
    :param command: 命令字符串或列表。
    :param shell: 是否使用 shell 执行（支持管道和重定向）。
    :param timeout: 超时时间（秒）。
    :param cwd: 工作目录。
    :param env: 环境变量。
    :return: 包含 stdout、stderr、returncode 的字典。
    """
    # 统一处理命令格式
    if isinstance(command, str):
        cmd = command if shell else shlex.split(command)
    else:
        cmd = command

    # 选择子进程创建方法
    if shell:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,  # 显式启用 shell
            cwd=cwd,
            env=env,
        )
    else:
        process = await asyncio.create_subprocess_exec(
            *cmd,  # 列表需解包为参数
            # stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env
        )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(input=input_content), timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise TimeoutError(f"Command '{command}' timed out after {timeout}秒")

    return {
        "stdout": stdout.decode().strip(),
        "stderr": stderr.decode().strip(),
        "returncode": process.returncode,
    }
