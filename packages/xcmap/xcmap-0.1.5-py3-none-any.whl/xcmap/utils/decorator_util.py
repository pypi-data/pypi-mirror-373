import asyncio
import functools
import time


def retry(max_retries=3, delay=3):
    """
    重试装饰器，支持同步和异步方法
    :param max_retries: 最大重试次数
    :param delay: 每次重试之间的延迟（秒）
    :return: 装饰后的函数
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None  # 保存最后一次异常
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)  # 尝试执行异步函数
                    except Exception as e:
                        last_exception = e  # 保存异常
                        print(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:  # 如果不是最后一次重试，则等待
                            await asyncio.sleep(delay)
                # 如果所有重试都失败，抛出最后一次异常
                raise Exception(f"All {max_retries} attempts failed. Last error: {last_exception}")

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None  # 保存最后一次异常
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)  # 尝试执行同步函数
                    except Exception as e:
                        last_exception = e  # 保存异常
                        print(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:  # 如果不是最后一次重试，则等待
                            time.sleep(delay)
                # 如果所有重试都失败，抛出最后一次异常
                raise Exception(f"All {max_retries} attempts failed. Last error: {last_exception}")

            return sync_wrapper

    return decorator
