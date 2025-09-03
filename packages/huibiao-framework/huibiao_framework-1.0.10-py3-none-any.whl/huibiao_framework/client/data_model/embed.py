from typing import List

from pydantic import BaseModel


class EmbedRespVo(BaseModel):
    Embedding: List[List[float]]
    Count: int
    Dim: int
