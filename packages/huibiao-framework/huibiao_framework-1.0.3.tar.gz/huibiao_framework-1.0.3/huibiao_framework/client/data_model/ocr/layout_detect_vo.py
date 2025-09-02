from pydantic import BaseModel, Field
from typing import List, Tuple, Literal


class LayoutRegionVo(BaseModel):
    """文档布局中单个区域的信息模型"""

    # 识别置信度分数，范围0-1
    score: float = Field(..., ge=0.0, le=1.0, description="区域识别的置信度分数")

    # 区域的四边形坐标，由4个(x,y)坐标点组成
    poly: List[Tuple[int, int]] = Field(
        ...,
        min_items=4,
        max_items=4,
        description="区域的四边形边界坐标，包含4个(x,y)顶点",
    )

    # 区域类型，限制为预定义的几种类型
    type: Literal["header", "title", "paragraph", "seal", "table"] = Field(
        ..., description="区域的语义类型"
    )


class DocumentLayoutDetectVo(BaseModel):
    """分析结果的详细信息模型"""

    # 文档宽度（像素）
    width: int = Field(..., gt=0, description="文档宽度，单位为像素")

    # 文档高度（像素）
    height: int = Field(..., gt=0, description="文档高度，单位为像素")

    # 文档旋转角度
    angle: int = Field(..., description="文档旋转角度，单位为度")

    # 分析模型版本
    version: str = Field(..., description="分析使用的模型版本")

    # 布局区域列表
    layouts: List[LayoutRegionVo] = Field(..., description="文档中识别到的布局区域列表")
