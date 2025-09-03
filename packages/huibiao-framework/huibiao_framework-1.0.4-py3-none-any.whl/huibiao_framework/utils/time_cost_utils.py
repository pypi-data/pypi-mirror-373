import asyncio
import time
from functools import wraps
from loguru import logger


def func_time_cost(step_name=None):
    """
    记录函数执行耗时，并支持指定步骤名称

    参数:
        step_name: 步骤名称，默认为函数名
    """

    def decorator(func):
        @wraps(func)  # 保留原函数元信息
        def wrapper(*args, **kwargs):
            nonlocal step_name
            step_name = step_name or func.__name__

            # 执行原函数并处理返回值
            result = None
            start_time = time.perf_counter()
            try:
                logger.debug(f"StepStart [{step_name}]")
                result = func(*args, **kwargs)

                # 检查是否为协程对象
                if asyncio.iscoroutine(result):

                    async def wrapped_coroutine():
                        try:
                            return await result
                        finally:
                            logger.debug(
                                f"StepTimeCost | [{step_name}][{time.perf_counter() - start_time:.6f}]秒"
                            )

                    return wrapped_coroutine()

                # 普通函数直接返回结果
                return result
            finally:
                # 普通函数在这里记录时间
                if not asyncio.iscoroutine(result):
                    logger.debug(
                        f"StepTimeCost | [{step_name}][{time.perf_counter() - start_time:.6f}]秒"
                    )

        return wrapper

    return decorator
