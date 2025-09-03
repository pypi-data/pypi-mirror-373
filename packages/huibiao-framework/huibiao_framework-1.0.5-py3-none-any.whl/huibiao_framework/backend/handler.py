import time
import traceback
from functools import wraps

from loguru import logger

from huibiao_framework.backend import BasicException, BaseRespVo, CommonStatusCode
from huibiao_framework.backend.metrics.request_metrics import RequestOperationMetrics


def timing_and_exception_handler(func):
    """
    装饰器：用于统计函数执行时间并捕获异常
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        request_id = kwargs.get("request_id", "unknown-reqid")

        try:
            # 执行原函数
            logger.info(f"ReqId: {request_id} | Function: {func.__name__} | Start")
            result = await func(*args, **kwargs)
            # 计算耗时
            elapsed_time = time.perf_counter() - start_time
            logger.info(
                f"ReqId: {request_id} | Function: {func.__name__} | COST:{elapsed_time:.4f}s"
            )
            RequestOperationMetrics.add(func.__name__, elapsed_time)
            return result
        except Exception as e:
            # 计算耗时
            elapsed_time = time.perf_counter() - start_time
            RequestOperationMetrics.add_error(func.__name__)
            # 记录异常信息和完整堆栈
            logger.error(
                f"ReqId: {request_id} | Function: {func.__name__} | COST:{elapsed_time:.4f}s | Exception: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            if isinstance(e, BasicException):
                return BaseRespVo(code=e.code, message=e.msg, result=None)
            return BaseRespVo.from_status_code(
                CommonStatusCode.INTERNAL_ERROR, msg=str(e)
            )

    return wrapper
