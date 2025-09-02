from datetime import timedelta
from typing import Any, Dict, List, Optional
from miniopy_async.datatypes import Bucket

import aiohttp
from loguru import logger
from miniopy_async import Minio
from miniopy_async.error import S3Error

from huibiao_framework.config import MinioConfig
from huibiao_framework.execption.minio import (
    MinioClientBucketNotExistsException,
    MinioDownloadException,
    MinioRemoveObjectException,
    MinioUploadException,
    MinioFileNotExistedException,
    MinioPresignedGetObjectException,
)


class MinIOClient:
    def __init__(
        self,
        endpoint: str = MinioConfig.ENDPOINT,
        access_key: str = MinioConfig.AK,
        secret_key: str = MinioConfig.SK,
        secure: bool = MinioConfig.OSS_SECURE,
        session: aiohttp.ClientSession = None,
    ):
        self.__http_client: Optional[aiohttp.ClientSession] = session
        self.__endpoint: str = endpoint
        self.__access_key: str = access_key
        self.__secrete_key: str = secret_key
        self.__seccure: bool = secure
        self.__client: Optional[Minio] = Minio(
            self.__endpoint,
            access_key=self.__access_key,
            secret_key=self.__secrete_key,
            secure=self.__seccure,
            session=self.__http_client,
        )

    async def test(self) -> bool:
        try:
            await self.__client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"连接Minio失败: {str(e)}")
            return False

    async def bucket_exists(self, bucket_name: str) -> Optional[bool]:
        """检查桶是否存在"""
        try:
            exists = await self.__client.bucket_exists(bucket_name)
            logger.debug(f"桶 {bucket_name} 是否存在: {exists}")
            return exists
        except Exception as e:
            logger.error(f"检查桶 {bucket_name} 存在失败: {e}")
            raise e

    async def list_buckets(self) -> List[Bucket]:
        """列出所有桶"""
        try:
            return await self.__client.list_buckets()
        except Exception as e:
            logger.error(f"列出桶失败: {e}")
            raise e

    async def list_objects(
        self, bucket_name: str, prefix: Optional[str] = None, recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        列出桶中的对象

        Args:
            bucket_name: 桶名称
            prefix: 对象前缀，用于过滤
            recursive: 是否递归查询

        Returns:
            对象列表，包含名称、大小、修改时间等信息
        """
        try:
            objects = await self.__client.list_objects(
                bucket_name, prefix=prefix, recursive=recursive
            )
            object_list = [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": str(obj.last_modified),
                    "etag": obj.etag,
                    "content_type": obj.content_type,
                }
                for obj in objects
            ]
            logger.debug(f"桶 {bucket_name} 中列出 {len(object_list)} 个对象")
            return object_list
        except S3Error as e:
            logger.error(f"列出桶 {bucket_name} 中的对象失败: {e}")
            return []

    async def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        上传文件到MinIO

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
            file_path: 本地文件路径

        """
        try:
            if not await self.bucket_exists(bucket_name):
                raise MinioClientBucketNotExistsException(bucket_name)

            await self.__client.fput_object(bucket_name, object_name, file_path)
            logger.info(f"成功上传文件: {file_path} 到 bucket:{bucket_name}, object:{object_name}")
        except Exception as e:
            logger.error(
                f"上传文件 {file_path} 到 bucket:{bucket_name}, object:{object_name} 失败: {e}"
            )
            raise MinioUploadException(str(e))

    async def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        从MinIO下载文件

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
            file_path: 本地保存路径
        """
        try:
            await self.__client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"成功下载文件: bucket:{bucket_name}, object:{object_name} 到 {file_path}")
        except Exception as e:
            logger.error(
                f"下载文件 bucket:{bucket_name}, object:{object_name} 到 {file_path} 失败: {e}"
            )
            if isinstance(e, S3Error) and e.code == "NoSuchKey":
                raise MinioFileNotExistedException(bucket=bucket_name, key=object_name)
            else:
                raise MinioDownloadException(str(e))

    async def remove_object(self, bucket_name: str, object_name: str):
        """
        删除对象

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
        """
        try:
            await self.__client.remove_object(bucket_name, object_name)
            logger.info(f"成功删除对象: bucket:{bucket_name}, object:{object_name}")
        except Exception as e:
            logger.error(f"删除对象 bucket:{bucket_name}, object:{object_name}失败: {e}")
            raise MinioRemoveObjectException(str(e))

    async def get_object_url(
        self, bucket_name: str, object_name: str, expires: timedelta = timedelta(days=1)
    ) -> str:
        """
        生成对象的预签名URL

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
            expires: URL过期时间(秒)，默认1小时

        Returns:
            预签名的URL
        """
        try:
            url = await self.__client.presigned_get_object(
                bucket_name, object_name, expires
            )
            logger.debug(f"生成预签名URL: {url}")
            return url
        except Exception as e:
            logger.error(
                f"生成预签名URL失败 bucket:{bucket_name}, object:{object_name}, {e}"
            )
            raise MinioPresignedGetObjectException(str(e))
