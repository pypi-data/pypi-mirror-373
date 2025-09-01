import asyncio
import concurrent.futures
from enum import Enum
from typing import Any, Callable, List, Optional

from loguru import logger


class ExecutorType(Enum):
    PROCESS = "process"
    THREAD = "thread"


class AsyncExecutorService:
    def __init__(
        self,
        executor_type: ExecutorType,
        min_workers: int = 1,
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "",
        initializer: Optional[Callable] = None,
        init_args: tuple = (),
    ):
        """
        初始化异步执行器服务

        :param executor_type: 执行器类型（进程池或线程池）
        :param min_workers: 最小工作线程/进程数
        :param max_workers: 最大工作线程/进程数
        :param thread_name_prefix: 线程名称前缀（仅线程池有效）
        :param initializer: 初始化函数
        :param init_args: 初始化函数参数
        """
        self.executor_type = executor_type
        self.min_workers = min_workers
        self.max_workers = max_workers or min_workers

        # 根据类型创建不同的执行器
        if executor_type == ExecutorType.PROCESS:
            self.executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.max_workers,
                initializer=initializer,
                initargs=init_args,
            )
            logger.info(
                f"Process pool initialized with min={min_workers}, max={max_workers}"
            )
        else:  # ExecutorType.THREAD
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix=thread_name_prefix,
                initializer=initializer,
                initargs=init_args,
            )
            logger.info(
                f"Thread pool initialized with min={min_workers}, max={max_workers}"
            )

    async def submit_task(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        异步提交任务到执行器

        :param func: 要执行的函数
        :param args: 函数的位置参数
        :param kwargs: 函数的关键字参数
        :return: 函数执行结果
        """
        loop = asyncio.get_running_loop()
        logger.info(f"Submitting task to {self.executor_type.value} pool")
        future = await loop.run_in_executor(self.executor, func, *args, **kwargs)
        return future

    async def shutdown(self, wait: bool = True):
        """
        异步关闭执行器

        :param wait: 是否等待所有任务完成
        """
        await asyncio.to_thread(self.executor.shutdown, wait=wait)
        logger.info(f"{self.executor_type.value.capitalize()} pool has been shut down")

    async def batch_submit(
        self,
        tasks: List[Callable],
        args_list: Optional[List[tuple]] = None,
        kwargs_list: Optional[List[dict]] = None,
    ) -> List[Any]:
        """
        批量异步提交任务

        :param tasks: 要执行的函数列表
        :param args_list: 位置参数列表，每个元素对应一个任务的位置参数
        :param kwargs_list: 关键字参数列表，每个元素对应一个任务的关键字参数
        :return: 按顺序排列的任务执行结果列表
        """
        args_list = args_list or [()] * len(tasks)
        kwargs_list = kwargs_list or [{}] * len(tasks)

        if len(args_list) != len(tasks) or len(kwargs_list) != len(tasks):
            raise ValueError("参数列表长度必须与任务数量一致")

        coros = [
            self.submit_task(task, *args, **kwargs)
            for task, args, kwargs in zip(tasks, args_list, kwargs_list)
        ]

        return await asyncio.gather(*coros)
