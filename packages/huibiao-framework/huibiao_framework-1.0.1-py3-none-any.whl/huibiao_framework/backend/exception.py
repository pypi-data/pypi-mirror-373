from huibiao_framework.backend.status_code import BasicStatusCode


class BasicException(Exception):
    """
    基础异常类
    """

    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg


class BasicCommonException(BasicException):
    def __init__(self, status_code: BasicStatusCode, **kwargs):
        super().__init__(code=status_code.value, msg=status_code.msg.format(**kwargs))
