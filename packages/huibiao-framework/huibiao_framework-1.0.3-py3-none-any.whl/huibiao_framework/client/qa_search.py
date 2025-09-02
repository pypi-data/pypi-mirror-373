import aiohttp

from huibiao_framework.client.data_model.model_resp_vo import ModelBaseRespVo
from huibiao_framework.client.data_model.qa_search import (
    AddQARespVo,
    AddQARequest,
    SearchQARequest,
    SearchAqRespVo,
)
from huibiao_framework.config.config import ClientConfig


class KnowledgeQaSearchClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.base_url = ClientConfig.SEARCH_URL
        self.headers = {"Content-Type": "application/json"}
        self.session = session

    async def add_qa(
        self,
        request_body: AddQARequest,
    ) -> AddQARespVo:
        """
        异步添加QA对到知识库
        """
        url = f"{self.base_url}/qa/add_qa"

        async with self.session.post(
            url, json=request_body.model_dump(), headers=self.headers
        ) as response:
            response.raise_for_status()
            raw_response = await response.json()
            return ModelBaseRespVo[AddQARespVo](**raw_response).result

    async def search_qa(self, request_body: SearchQARequest) -> SearchAqRespVo:
        """
        异步搜索QA对
        """
        url = f"{self.base_url}/qa/search"

        async with self.session.post(
            url, json=request_body.model_dump(), headers=self.headers
        ) as response:
            response.raise_for_status()
            raw_response = await response.json()
            return ModelBaseRespVo[SearchAqRespVo](**raw_response).result
