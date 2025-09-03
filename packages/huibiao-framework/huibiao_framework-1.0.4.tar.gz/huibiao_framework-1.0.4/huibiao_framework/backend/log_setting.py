import os
from loguru import logger


class LoggerSetup:
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {process} | {name}:{function}:{line} - {message}"

    @classmethod
    def save_rotate_by_size(
        cls,
        service_name: str,
        log_dir: str,
        *,
        max_size_mb: int = 100,
    ):
        os.makedirs(log_dir, exist_ok=True)

        # 配置 INFO 及以上级别日志
        logger.add(
            os.path.join(log_dir, service_name, f"{service_name}_info.log"),
            rotation=f"{max_size_mb} MB",
            filter=lambda record: record["level"].no >= 20,
            format=cls.LOG_FORMAT,
            enqueue=True,
        )

        # 配置 DEBUG 级别日志
        logger.add(
            os.path.join(log_dir, service_name, f"{service_name}_debug.log"),
            rotation=f"{max_size_mb} MB",
            level="DEBUG",
            filter=lambda record: record["level"].no >= 10,
            format=cls.LOG_FORMAT,
            enqueue=True,
        )

        logger.info("日志落盘设置完成")
