from loguru import logger
from fastapi.exceptions import StarletteHTTPException
from fastapi.responses import JSONResponse
from urllib.request import Request

from huibiao_framework.backend import BaseRespVo, CommonStatusCode


def http_exception_interceptor(request: Request, exc: StarletteHTTPException):
    logger.info(
        f"req_id: {request.url} | 错误码: {exc.status_code} | 错误信息: {exc.detail}"
    )
    if exc.status_code == 405:
        vo = BaseRespVo.from_status_code(CommonStatusCode.ERROR_REQ_METHOD)
    elif exc.status_code == 404:
        vo = BaseRespVo.from_status_code(CommonStatusCode.ERROR_REQ_URL)
    else:
        vo = BaseRespVo.from_status_code(
            CommonStatusCode.UNKNOWN_ERROR, msg=f"{exc.status_code},{exc.detail}"
        )

    return JSONResponse(content=vo.model_dump(), status_code=200)
