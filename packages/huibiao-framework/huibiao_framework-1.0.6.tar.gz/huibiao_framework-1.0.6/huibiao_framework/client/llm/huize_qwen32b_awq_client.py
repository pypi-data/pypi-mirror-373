import time

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.client.data_model.model_resp_vo import ModelBaseRespVo
from huibiao_framework.client.data_model.vllm import (
    HuizeQwen32bAwqDto,
    HuizeQwen32bAwqVo,
)
from huibiao_framework.client.llm.abstrast_llm_client import AbstractLlmModelClient
from huibiao_framework.config.config import ModelConfig
from huibiao_framework.execption.model import (
    Qwen32bAwqResponseFormatError,
    Qwen32bAwqException,
)


class HuiZeQwen32bQwqClient(HuibiaoAbstractClient, AbstractLlmModelClient):
    """
    慧泽Qwen-32B模型客户端
    url: http://vllm-qwen-32b.model.hhht.ctcdn.cn:9080/common/query
    request:
        {
        "Action": "NormalChat",
        "DoSample": true,
        "Messages": [
                {
                    "content": "请将下面这段英文翻译成中文：请将下面这段英文翻译成中文：I am a test。",
                    "role": "user"
                }
            ]
        }
    response:
        {
            "code": 0,
            "result": {
                "Output": "我是一个测试。",
                "TokenProbs": [
                    1.0
                ]
            },
            "message": "success"
        }
    """

    def __init__(self, session: aiohttp.ClientSession):
        super().__init__(client_name="HuiZeQwen32bQwq", session=session)

    async def post(
        self, dto: HuizeQwen32bAwqDto, session_id: str = ""
    ) -> HuizeQwen32bAwqVo:
        session_tag = self.session_tag(session_id)
        logger.debug(
            f"{session_tag},contentLien={[len(i.content) for i in dto.Messages]}"
        )
        start_time = time.time()
        try:
            # 发送异步POST请求
            async with self.session.post(
                ModelConfig.REQUEST_URL, json=dto.model_dump()
            ) as resp:
                sp_time = time.time() - start_time
                logger.debug(f"{session_tag},resp-{resp.status},cost {sp_time:.2f}s")
                resp.raise_for_status()
                response_data = await resp.json()
                response_data = ModelBaseRespVo[HuizeQwen32bAwqVo](**response_data)
                return response_data.result
        except (Qwen32bAwqException, Qwen32bAwqResponseFormatError) as e:
            logger.error(f"{session_tag} resp error: {str(e)}")
            raise e
        except aiohttp.ClientError as e:
            logger.error(f"{session_tag} failed, {str(e)}")
            raise e

    async def query(self, content, session_id: str = "") -> HuizeQwen32bAwqVo:
        dto = HuizeQwen32bAwqDto()
        dto.Messages[0].content = content
        return await self.post(dto=dto, session_id=session_id)

    async def simple_query(self, content, session_id: str = "") -> str:
        return (await self.query(content, session_id)).Output
