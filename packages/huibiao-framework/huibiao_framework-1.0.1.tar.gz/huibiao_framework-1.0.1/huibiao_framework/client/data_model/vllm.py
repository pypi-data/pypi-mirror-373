from typing import List, Optional

from pydantic import BaseModel, field_validator
from huibiao_framework.execption.model import Qwen32bAwqResponseFormatError


class HuizeQwen32bAwqDto(BaseModel):
    class Message(BaseModel):
        content: str = "今天天气如何"
        role: str = "user"

    Action: str = "NormalChat"
    Messages: List[Message] = [
        Message(),
    ]


class HuizeQwen32bAwqVo(BaseModel):
    Output: Optional[str]
    TokenProbs: Optional[List[float]]

    @field_validator("Output")
    def check_output_not_empty(cls, v: str) -> str:
        if v is None or not v.strip():
            raise Qwen32bAwqResponseFormatError("Field 'result.Output' is Empty")
        return v
