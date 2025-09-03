import json
from typing import Union

import aiohttp
import aiofiles
from loguru import logger

from .abstract_async_file import AbstractAsyncFile


class BytesAsyncFile(AbstractAsyncFile[bytes]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def load(self) -> bytes:
        async with aiofiles.open(self.local_path, mode="rb") as f:
            data: bytes = await f.read()
            self.set_data(data)
            logger.debug(f"load bytes {self.local_path}")
            return data

    async def save(self):
        async with aiofiles.open(self.local_path, mode="wb") as f:
            await f.write(self.data)
            logger.debug(f"save bytes {self.local_path}")

    async def wget(self, session: aiohttp.ClientSession = None) -> bytes:
        data: bytes = await self.basic_wget(session=session)
        self.set_data(data)
        return data


class JsonAsyncFile(AbstractAsyncFile[Union[dict, list]]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def load(self) -> Union[dict, list]:
        async with aiofiles.open(self.local_path, "r", encoding="utf-8") as f:
            data: Union[dict, list] = json.loads(await f.read())
            logger.debug(f"load json {self.local_path}")
            self.set_data(data)
            return data

    async def save(self):
        async with aiofiles.open(self.local_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(self.data, ensure_ascii=False, indent=4))
            logger.debug(f"save json {self.local_path}")

    async def wget(self, session: aiohttp.ClientSession = None) -> Union[dict, list]:
        data: bytes = await self.basic_wget(session=session)
        json_data = json.loads(data)
        self.set_data(json_data)
        return json_data
