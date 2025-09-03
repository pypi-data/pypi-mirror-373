from typing import Generic, TypeVar

from huibiao_framework.utils.file_manage import AbstractAsyncFile

from loguru import logger

T = TypeVar("T", bound=AbstractAsyncFile)


class TempFileWrapper(Generic[T]):
    def __init__(self, async_file: T):
        self.async_file = async_file

    async def __aenter__(self) -> T:
        """支持 async with 语法"""
        return self.async_file

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出时自动删除临时文件"""
        try:
            self.async_file.delete()
        except Exception as e:
            logger.debug(
                f"Warning: Failed to delete temp file {self.async_file.local_path}: {e}"
            )
