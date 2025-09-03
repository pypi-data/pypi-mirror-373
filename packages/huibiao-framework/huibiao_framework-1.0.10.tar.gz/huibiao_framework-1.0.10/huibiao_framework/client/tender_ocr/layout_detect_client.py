import time
from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.client.data_model.model_resp_vo import ModelBaseRespVo
from huibiao_framework.client.data_model.ocr.layout_detect_vo import (
    DocumentLayoutDetectVo,
)
from huibiao_framework.config import ClientConfig
from huibiao_framework.utils.image import ImageUtils


class LayoutDetectionClient(HuibiaoAbstractClient):
    """
    tender-ocr的文件实现类
    url: http://host:port/image_layout
    request:
        payload = {"data": encode_base64_string(file_path)}
        headers = {
                "Content-Type": "application/json",  # 根据需要设置内容类型
                "x-request-id": reqid
                }
    response:
        {
            "code": 0,
            "result": {
                "width": 1266,
                "height": 1806,
                "angle": 0,
                "version": "0.3.32",
                "layouts": [
                    {
                        "score": 0.983,
                        "type": "table",
                        "bbox": [
                                    [
                                        139,
                                        1128
                                    ],
                                    [
                                        1122,
                                        1128
                                    ],
                                    [
                                        1122,
                                        1618
                                    ],
                                    [
                                        139,
                                        1618
                                    ]
                                ]
                    },...
                ]
            }
        }
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        super().__init__(client_name="LayoutDetect", session=session)

    async def query_by_image_base64(
        self, image_base64: str, reqid: str = None, session_id: str = None
    ) -> DocumentLayoutDetectVo:
        reqid = reqid or ""
        session_id = session_id or ""

        session_tag = self.session_tag(session_id)

        payload = {"data": image_base64}
        headers = {
            "Content-Type": "application/json",
            "x-request-id": reqid,
        }
        # 发送异步POST请求
        start_time = time.time()
        try:
            async with self.session.post(
                ClientConfig.LAYOUT_DETECTION_TYY_URL, json=payload, headers=headers
            ) as resp:
                sp_time = time.time() - start_time
                logger.debug(f"{session_tag},resp-{resp.status},cost {sp_time:.2f}s")
                resp.raise_for_status()
                response_data = await resp.json()
                response_data = ModelBaseRespVo[DocumentLayoutDetectVo](**response_data)
                return response_data.result
        except aiohttp.ClientError as e:
            logger.error(f"{session_tag} failed, {str(e)}")
            raise e

    async def query_by_image_path(
        self, image_path: str, reqid: str = None, session_id: str = None
    ) -> DocumentLayoutDetectVo:
        image_base64 = await ImageUtils.encode_base64(image_path)
        return await self.query_by_image_base64(
            image_base64=image_base64, reqid=reqid, session_id=session_id
        )
