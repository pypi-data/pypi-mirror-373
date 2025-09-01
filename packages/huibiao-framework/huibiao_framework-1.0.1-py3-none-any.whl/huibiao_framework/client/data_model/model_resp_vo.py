from pydantic import BaseModel, Field, model_validator
from typing import Generic, TypeVar, Optional

from huibiao_framework.execption.model import (
    HuiZeModelResponseCodeError,
    HuiZeModelResponseFormatError,
)

T = TypeVar("T")


class ModelBaseRespVo(BaseModel, Generic[T]):
    # 响应状态码，0通常表示成功
    code: int = Field(..., description="响应状态码，0表示成功")

    # 响应消息
    message: str = Field("", description="响应状态描述信息")

    # 分析结果数据（泛型类型，可动态指定）
    result: Optional[T] = Field(None, description="分析结果数据，类型由泛型参数指定")

    @model_validator(mode="after")
    def check_result_consistent_with_code(cls, values):
        code = values.code
        result = values.result
        msg = values.message
        if code is None or code != 0:
            # 校验 code 合法性（通常 0 表示成功，非 0 表示错误）
            raise HuiZeModelResponseCodeError(code, msg)
        if code == 0 and result is None:
            raise HuiZeModelResponseFormatError("Field 'result' is empty!")
        return values
