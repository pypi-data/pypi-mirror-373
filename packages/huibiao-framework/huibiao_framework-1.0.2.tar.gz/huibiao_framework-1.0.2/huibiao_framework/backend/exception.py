from huibiao_framework.backend.status_code import BasicStatusCode
from typing import TypeVar, Generic

class BasicException(Exception):
    """
    基础异常类
    """

    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg


# 定义泛型变量 T，限定为 BasicStatusCode 的子类
T = TypeVar('T', bound=BasicStatusCode)

class BasicCommonException(BasicException, Generic[T]):
    def __init__(self, status_code: T, **kwargs):
        super().__init__(code=status_code.code, msg=status_code.msg.format(**kwargs))