from enum import Enum
from typing import Optional

import aiohttp

from huibiao_framework.client.llm.huize_qwen32b_awq_client import HuiZeQwen32bQwqClient
from huibiao_framework.client.llm.abstrast_llm_client import AbstractLlmModelClient
from huibiao_framework.config.config import ModelConfig, LlmModelNameConstant
from huibiao_framework.execption.model import LLMException


class LlmModelClient(AbstractLlmModelClient):
    def __init__(self, session: aiohttp.ClientSession, model: str = None):
        self.model_name: str = model if model else ModelConfig.LLM_MODEL_TYPE
        self.__model: Optional[AbstractLlmModelClient] = None

        if self.model_name.lower() == LlmModelNameConstant.HuiZeQwen32bQwq.lower():
            self.__model = HuiZeQwen32bQwqClient(session)
        else:
            raise LLMException("错误的llm模型类型")

    async def simple_query(self, content, session_id: str = "") -> str:
        return await self.__model.simple_query(content, session_id)
