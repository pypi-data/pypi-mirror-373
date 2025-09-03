from enum import Enum


class BasicStatusCode(Enum):
    def __new__(cls, value: int, msg: str):
        obj = object.__new__(cls)
        obj._value_ = obj
        obj.code = value
        obj.msg = msg
        return obj

    @property
    def value(self):
        return self.code


class CommonStatusCode(BasicStatusCode):
    SUCCESS = (0, "成功")

    ERROR_REQ_URL = (40001, "请求路径错误")
    ERROR_REQ_METHOD = (40002, "请求方法错误")
    BODY_EMPTY_ERR = (40003, "请求体内容为空")
    PARAM_ERROR = (40006, "参数错误:{msg}")
    ERROR_HEADER_NOW_EXISTS = (40007, "缺少请求头:{header}")

    UNKNOWN_ERROR = (50000, "未知错误: {msg}")

    INTERNAL_ERROR = (50001, "内部错误: {msg}")
