import functools
import os.path
from abc import ABC, abstractmethod
from typing import Optional, Any, Generic, TypeVar

import aiofiles
import aiohttp
from loguru import logger

from huibiao_framework.client import MinIOClient
from huibiao_framework.config import MinioConfig


def with_oss_client(func):
    @functools.wraps(func)
    async def wrapper(self, client: MinIOClient = None, *args, **kwargs):
        self.valid_oss_param()

        if client:
            return await func(self, client, *args, **kwargs)
        else:
            async with aiohttp.ClientSession() as session:
                client = MinIOClient(session=session)
                return await func(self, client, *args, **kwargs)

    return wrapper


T = TypeVar("T")


class AbstractAsyncFile(ABC, Generic[T]):
    """
    临时文件管理器
    """

    def __init__(
        self,
        *,
        file_path: str = None,
        wget_link: str = None,
        oss_key=None,
        oss_bucket: str = MinioConfig.BUCKET_NAME,
    ):
        if file_path:
            self.local_path = file_path

            if os.path.dirname(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

        self.wget_link = wget_link
        self.oss_bucket = oss_bucket
        self.oss_key = oss_key
        self.__data: T = None

    def set_data(self, data):
        self.__data = data

    @property
    def data(self) -> T:
        return self.__data

    def exist(self) -> bool:
        return os.path.exists(self.local_path)

    @abstractmethod
    async def load(self) -> T:
        pass

    @abstractmethod
    async def save(self):
        pass

    @abstractmethod
    async def wget(self, session: aiohttp.ClientSession = None) -> T:
        """下载数据，但是不保存"""
        pass


    def delete(self):
        """
        删除本地文件
        """
        if self.local_path and os.path.exists(self.local_path):
            os.remove(self.local_path)
            logger.debug(f"file delete success: {self.local_path}")

    # region oss操作
    def valid_oss_param(self):
        assert self.local_path, "请设置文件路径"
        assert self.oss_key, "请设置文件oss_key"
        assert self.oss_bucket, "请设置文件oss_bucket"

    @with_oss_client
    async def upload_oss(self, client: MinIOClient = None):
        """上传到oss"""
        self.valid_oss_param()
        await client.upload_file(
            bucket_name=self.oss_bucket,
            object_name=self.oss_key,
            file_path=self.local_path,
        )

    @with_oss_client
    async def download_oss(self, client: MinIOClient = None):
        """从oss下载到本地"""
        self.valid_oss_param()
        await client.download_file(
            bucket_name=self.oss_bucket,
            object_name=self.oss_key,
            file_path=self.local_path,
        )

    @with_oss_client
    async def gen_oss_url(self, client: MinIOClient = None):
        """生成oss链接"""
        self.valid_oss_param()
        return await client.get_object_url(
            bucket_name=self.oss_bucket,
            object_name=self.oss_key,
        )

    # endregion

    async def basic_wget(self, session: aiohttp.ClientSession = None) -> bytes:
        """下载json，保存到本地"""
        assert self.wget_link, "请设置json文件的下载链接"

        async def fun(_session):
            async with _session.get(self.wget_link) as response:
                response.raise_for_status()
                data: bytes = await response.read()
                logger.info(f"success wget {self.wget_link}")
                return data

        if session is not None:
            return await fun(session)
        else:
            async with aiohttp.ClientSession() as session:
                return await fun(session)
