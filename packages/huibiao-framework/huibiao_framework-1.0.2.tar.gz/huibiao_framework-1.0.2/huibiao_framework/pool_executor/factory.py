from typing import Callable, Optional

from .executor import AsyncExecutorService, ExecutorType


class AsyncExecutorFactory:
    __PROCESS_POOL = None
    __THREAD_POOL = None

    @classmethod
    def process(cls) -> AsyncExecutorService | None:
        if cls.__PROCESS_POOL is not None:
            return cls.__PROCESS_POOL
        else:
            raise RuntimeError("Process pool has not been initialized")

    @classmethod
    def thread(cls) -> AsyncExecutorService | None:
        if cls.__THREAD_POOL is not None:
            return cls.__THREAD_POOL
        else:
            raise RuntimeError("Thread pool has not been initialized")

    @classmethod
    def shut_down_process_pool(cls):
        if cls.__PROCESS_POOL is not None:
            cls.__PROCESS_POOL.close()
            cls.__PROCESS_POOL.join()
            cls.__PROCESS_POOL = None

    @classmethod
    def shut_down_thread_pool(cls):
        if cls.__THREAD_POOL is not None:
            cls.__THREAD_POOL.shutdown()
            cls.__THREAD_POOL = None

    @classmethod
    def init_thread_pool(
        cls,
        min_workers: int = 1,
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "",
        initializer: Optional[Callable] = None,
        init_args: tuple = (),
    ):
        if cls.__THREAD_POOL is not None:
            return
        cls.__THREAD_POOL = AsyncExecutorService(
            executor_type=ExecutorType.THREAD,
            min_workers=min_workers,
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            init_args=init_args,
        )

    @classmethod
    def init_process_pool(
        cls,
        min_workers: int = 1,
        max_workers: Optional[int] = None,
        initializer: Optional[Callable] = None,
        init_args: tuple = (),
    ):
        if cls.__THREAD_POOL is not None:
            return
        cls.__PROCESS_POOL = AsyncExecutorService(
            executor_type=ExecutorType.PROCESS,
            min_workers=min_workers,
            max_workers=max_workers,
            initializer=initializer,
            init_args=init_args,
        )
