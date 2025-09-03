import sys

from loguru import logger
import os


class LoguruUtils:
    @classmethod
    def service_setup(
        cls,
        service_name: str,
        log_dir: str,
        *,
        add_pid_suffix: bool = True,
        max_size_mb: int = 100,
        remove_exist: bool = True,
    ):
        """
        日志输出终端和落盘
        """
        if remove_exist:
            logger.remove()  # 清空设置，防止重复

        os.makedirs(log_dir, exist_ok=True)
        pid_suffix = f"_{os.getpid()}" if add_pid_suffix else ""

        # 添加终端处理器（控制台输出）
        logger.add(
            sink=sys.stderr,  # 输出到标准错误流
            level="DEBUG",  # 终端显示更详细的DEBUG日志
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            colorize=True,  # 启用颜色显示
            backtrace=True,  # 堆栈信息显示在终端
        )

        # 配置 INFO 及以上级别日志
        logger.add(
            os.path.join(log_dir, f"{service_name}_info{pid_suffix}.log"),
            rotation=f"{max_size_mb} MB",
            filter=lambda record: record["level"].no >= 20,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {process} | {message}",
            enqueue=True,
        )

        # 配置 DEBUG 级别日志
        logger.add(
            os.path.join(log_dir, f"{service_name}_debug{pid_suffix}.log"),
            rotation=f"{max_size_mb} MB",
            level="DEBUG",
            filter=lambda record: record["level"].no >= 10,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,
        )

        logger.info("日志落盘设置完成")
