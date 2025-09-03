from pydantic import BaseModel, Field
from typing import List, Any, Tuple


class Line(BaseModel):
    """单个文本行的 OCR 识别结果"""

    poly: List[Tuple[int, int]] = Field(
        ...,
        min_items=4,
        max_items=4,
        description="区域的四边形边界坐标，包含4个(x,y)顶点",
    )
    text: str  # 识别的文本内容
    type: str  # 识别类型（如 img_ocr）
    score: List[Any]  # 识别置信度相关数据，格式为 [置信度数值, 其他参数]


class ImageOcrVo(BaseModel):
    """OCR 模型的整体识别结果"""

    version: str  # 模型版本号
    width: int  # 图片宽度
    height: int  # 图片高度
    angle: int  # 图片旋转角度
    lines: List[Line]  # 所有识别到的文本行列表
