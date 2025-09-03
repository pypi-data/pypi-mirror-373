import time

import aiohttp

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from loguru import logger

from huibiao_framework.client.data_model.chunk import ChunkRespVo, ChunkReqDto
from huibiao_framework.client.data_model.model_resp_vo import ModelBaseRespVo
from huibiao_framework.config import ClientConfig
from huibiao_framework.execption.model import HuiZeModelException


class ChunkClient(HuibiaoAbstractClient):
    def __init__(self, session: aiohttp.ClientSession):
        super().__init__(client_name="Chunk", session=session)

    async def post(self, body: ChunkReqDto, session_id: str = "") -> ChunkRespVo:
        session_tag = self.session_tag(session_id)

        start_time = time.perf_counter()

        try:
            # 发送异步POST请求
            async with self.session.post(
                ClientConfig.CHUNK_URL, json=body.model_dump()
            ) as resp:
                sp_time = time.perf_counter() - start_time
                logger.debug(f"{session_tag},resp-{resp.status},cost {sp_time:.2f}s")
                resp.raise_for_status()
                response_data = await resp.json()
                response_data = ModelBaseRespVo[ChunkRespVo](**response_data)
                return response_data.result
        except HuiZeModelException as e:
            logger.error(f"{session_tag} resp error: {str(e)}")
            raise e
        except aiohttp.ClientError as e:
            logger.error(f"{session_tag} failed, {str(e)}")
            raise e
