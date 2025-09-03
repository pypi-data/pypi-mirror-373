from urllib.request import Request

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from huibiao_framework.backend import CommonStatusCode, BaseRespVo


def validate_interceptor(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    拦截接口关于schema检验的报错，并返回约定的body
    """

    # 检验请求头
    reqid: str = request.headers.get("x-request-id", None)
    if not reqid:
        return JSONResponse(
            status_code=200,
            content=BaseRespVo.from_status_code(
                CommonStatusCode.ERROR_HEADER_NOW_EXISTS, header="x-request-id"
            ).model_dump(),
        )

    logger.error(f"Reqid: {reqid} | 请求体参数错误: {str(exc)[:400]}...")
    if int(request.headers.get("content-length")) == 0 and request.method in (
        "POST",
        "PUT",
        "PATCH",
    ):
        vo = BaseRespVo.from_status_code(CommonStatusCode.BODY_EMPTY_ERR)
    else:
        reason: str = parse_request_validation_error(exc)
        vo = BaseRespVo.from_status_code(CommonStatusCode.PARAM_ERROR, msg=reason)

    return JSONResponse(
        status_code=200,  # 或其他合适的 HTTP 状态码
        content=vo.model_dump(),  # 将 Pydantic 模型转换为字典
    )


def parse_request_validation_error(exc: RequestValidationError):
    """
    报错润色
    RequestValidationError([{'type': 'string_type', 'loc': ('body', 'messages', 0, 'role'), 'msg': 'Input should be a valid string...[]},
    {'type': 'string_type', 'loc': ('body', 'messages', 0, 'content'), 'msg': 'Input should be a valid string', 'input': []}])
    转换结果如下：
    '请求参数错误，发现2个字段问题：messages[0].role: Input should be a valid string；messages[0].content: Input should be a valid string'
    """
    error_fields = []
    for error in exc.errors():
        loc = error["loc"]
        # 忽略第一个元素（通常是 body）
        field_path = ".".join(
            f"[{i}]" if isinstance(i, int) else i for i in loc[1:]
        ).replace(".[", "[")
        msg = error["msg"]
        error_fields.append(f"{field_path}: {msg}")
    return f"请求参数错误，发现{len(error_fields)}个字段问题：" + "；".join(
        error_fields
    )
