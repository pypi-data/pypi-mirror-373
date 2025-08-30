import asyncio
import logging
import time
from functools import wraps


def async_debounce(wait):
    def decorator(func):
        task: asyncio.Task | None = None

        @wraps(func)
        async def debounced(*args, **kwargs):
            nonlocal task

            async def call_func():
                await asyncio.sleep(wait)
                await func(*args, **kwargs)

            if task and not task.done():
                logging.info("[debounce] has task cancel")
                task.cancel()

            task = asyncio.create_task(call_func())
            return task

        return debounced

    return decorator


def async_throttle(wait: float):
    """
    异步节流器（控制程序在固定时间内只执行一次）
    使用时间戳控制执行频率
    :param wait: 节流等待时间（秒）
    :return: 装饰器
    """

    def decorator(func):
        last_exec_time = 0

        @wraps(func)
        async def throttle(*args, **kwargs):
            nonlocal last_exec_time
            current_time = time.time()
            # 对请求进行节流
            if current_time - last_exec_time < wait:
                logging.info("[throttle] Too frequent, ignoring call")
                return
            # 更新最后执行时间
            last_exec_time = current_time
            # 执行原函数
            return await func(*args, **kwargs)

        return throttle

    return decorator
