from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

from huibiao_framework.backend import CommonStatusCode
from huibiao_framework.backend.status_code import BasicStatusCode

T = TypeVar("T")


class BaseRespVo(BaseModel, Generic[T]):
    code: int
    message: str
    result: Optional[T] = Field(None, description="结果")

    @classmethod
    def success(cls, result: Optional[T]):
        return cls(
            code=CommonStatusCode.SUCCESS.code,
            result=result,
            message=CommonStatusCode.SUCCESS.msg,
        )

    @classmethod
    def from_status_code(cls, http_status: BasicStatusCode, **kwargs):
        return cls(
            code=http_status.code,
            message=http_status.msg.format(**kwargs),
            result=None,
        )
