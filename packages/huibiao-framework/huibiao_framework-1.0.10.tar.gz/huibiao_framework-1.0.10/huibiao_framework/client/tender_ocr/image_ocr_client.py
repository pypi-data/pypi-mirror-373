import time
from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.client.data_model.model_resp_vo import ModelBaseRespVo
from huibiao_framework.client.data_model.ocr.image_ocr import ImageOcrVo
from huibiao_framework.config import ClientConfig
from huibiao_framework.utils.image import ImageUtils


class ImageOcrClient(HuibiaoAbstractClient):
    """
    图片版面解析接口
    url: http://host:port/image_ocr
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
            "version": "0.3.32",
            "width": 991,
            "height": 647,
            "angle": 0,
            "lines": [
                {
                    "bbox": [
                                [
                                    293.0,
                                    179.0
                                ],
                                [
                                    714.0,
                                    179.0
                                ],
                                [
                                    714.0,
                                    226.0
                                ],
                                [
                                    293.0,
                                    226.0
                                ]
                            ],
                    "text": "学士学位证书",
                    "score": 1.0
                },...
                ]
            }
        }
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        super().__init__(client_name="ImageOcr", session=session)

    async def query_by_image_base64(
        self, image_base64: str, reqid: str = None, session_id: str = None
    ) -> ImageOcrVo:
        reqid = reqid or ""
        session_id = session_id or ""
        session_tag = self.session_tag(session_id)

        payload = {"data": image_base64}
        headers = {
            "Content-Type": "application/json",  # 根据需要设置内容类型
            "x-request-id": reqid,
        }
        start_time = time.time()
        try:
            async with self.session.post(
                ClientConfig.IMAGE_OCR_TYY_URL, json=payload, headers=headers
            ) as resp:
                sp_time = time.time() - start_time
                logger.debug(
                    f"{session_tag},resp-{resp.status}, 响应时间: {sp_time:.2f}秒"
                )
                resp.raise_for_status()
                response_data = await resp.json()
                response_data = ModelBaseRespVo[ImageOcrVo](**response_data)
                return response_data.result
        except aiohttp.ClientError as e:
            logger.error(f"{session_tag}请求异常", e)
            raise e

    async def query_by_image_path(
        self, image_path: str, reqid: str = None, session_id: str = None
    ) -> ImageOcrVo:
        image_base64 = await ImageUtils.encode_base64(image_path)
        return await self.query_by_image_base64(
            image_base64=image_base64, reqid=reqid, session_id=session_id
        )
