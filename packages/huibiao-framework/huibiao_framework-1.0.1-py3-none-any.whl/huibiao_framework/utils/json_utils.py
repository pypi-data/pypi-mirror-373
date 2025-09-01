import functools
import os

import aiofiles
import json

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


class JsonFile:
    def __init__(
        self,
        local_path: str,
        wget_link: str = None,
        oss_key=None,
        oss_bucket: str = MinioConfig.BUCKET_NAME,
    ):
        self.local_path = local_path
        self.wget_link = wget_link
        self.oss_bucket = oss_bucket
        self.oss_key = oss_key
        self.__data = None

        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)

    @property
    def data(self):
        return self.__data

    def set_data(self, data) -> 'JsonFile':
        self.__data = data
        return self

    def exists(self) -> bool:
        return os.path.exists(self.local_path)

    async def load_json(self):
        """
        异步io加载
        """
        async with aiofiles.open(self.local_path, "r", encoding="utf-8") as f:
            self.__data = json.loads(await f.read())
            logger.debug(f"load json {self.local_path}")
            return self.__data

    async def save_json(self):
        """
        异步io保存
        """
        async with aiofiles.open(self.local_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(self.__data, ensure_ascii=False, indent=4))
            logger.debug(f"save json {self.local_path}")

    async def wget(self, session: aiohttp.ClientSession = None):
        """下载json，保存到本地"""
        assert self.wget_link, "请设置json文件的下载链接"

        async def fun(_session):
            async with _session.get(self.wget_link) as response:
                response.raise_for_status()
                data = json.loads(await response.read())
                logger.info(f"wget json {self.wget_link} -> {self.local_path}")
                self.__data = data
                await self.save_json()

        if session is not None:
            await fun(session)
        else:
            async with aiohttp.ClientSession() as session:
                await fun(session)

    def valid_oss_param(self):
        assert self.oss_key, "请设置json文件oss_key"
        assert self.oss_bucket, "请设置json文件oss_bucket"

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
        await self.load_json()

    @with_oss_client
    async def gen_oss_url(self, client: MinIOClient = None):
        """生成oss链接"""
        self.valid_oss_param()
        return await client.get_object_url(
            bucket_name=self.oss_bucket,
            object_name=self.oss_key,
        )