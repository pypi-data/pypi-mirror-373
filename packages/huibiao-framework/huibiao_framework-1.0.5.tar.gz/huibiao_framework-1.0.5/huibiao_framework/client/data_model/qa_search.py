from typing import List, Optional, TypeVar

from pydantic import BaseModel, Field


class QAPair(BaseModel):
    """QA对模型，表示问题和答案的组合"""

    Question: str = Field(..., description="问题")
    Answer: str = Field(..., description="答案")
    SimilarFlag: Optional[int] = Field(
        default=None, description="相似标志位，0表示不相似，1表示相似，此参数可以忽略"
    )


class AddQARequest(BaseModel):
    """添加QA请求模型"""

    UserName: str = Field(..., description="用户名，不能为空")
    DbName: str = Field(..., description="问答库名（分类名），不能为空")
    FileName: str = Field(..., description="文件名称，可重名")
    FileID: int = Field(..., description="文件ID，建议保证唯一性")
    QA: List[QAPair] = Field(..., description="QA对列表")


class SearchQARequest(BaseModel):
    """
    搜索请求参数模型
    """

    UserName: List[str] = Field(..., description="用户名。不能为空。")
    DbName: List[str] = Field(
        ...,
        description="问答向量库名（分类名）。可支持多个库的搜索。列表中向量库和用户名必须一一对应的关系。",
    )
    Query: str = Field(..., description="提问内容。")
    Limit: Optional[int] = Field(
        None,
        description="TopK 个 QA 对。NeedReRank生效时为 ReRank TopK。默认值为5。",
    )
    SearchLimit: Optional[int] = Field(
        None, description="检索的TopK个结果。仅NeedReRank生效时可用。默认值为15。"
    )
    NeedReRank: Optional[bool] = Field(
        None,
        description="是否使用ReRanker重排。默认值为False，不进行重拍。若该值设为True，则进行重排。",
    )


T = TypeVar("T")


class KnowledgeQAException(Exception):
    """知识问答异常基类"""

    pass


class AddQARespVo(BaseModel):
    """添加QA响应VO模型"""

    UserName: str = Field(..., description="用户名")
    DbName: str = Field(..., description="问答库名（分类名）")
    FileName: str = Field(..., description="文件名称")
    FileID: int = Field(..., description="文件ID")
    QA: List[QAPair] = Field(..., description="QA对列表")
    QAID: List[int] = Field(..., description="QA ID列表")
    Status: str = Field(..., description="状态,success表示成功")

    def success(self) -> bool:
        return self.Status == "success"


class SearchAqRespVo(BaseModel):
    """搜索响应VO模型"""

    class MatchItem(BaseModel):
        """匹配项模型"""

        FileID: Optional[int] = Field(..., description="文件ID")
        FileName: Optional[str] = Field(..., description="文件名称")
        QAID: Optional[int] = Field(..., description="QA ID")
        Question: Optional[str] = Field(..., description="问题")
        Answer: Optional[str] = Field(..., description="答案")
        SimilarFlag: Optional[int] = Field(..., description="相似标志位，0表示不相似，1表示相似")
        Score: Optional[float] = Field(..., description="匹配分数")
        UserName: Optional[str] = Field(..., description="用户名")
        DbName: Optional[str] = Field(..., description="问答库名（分类名）")
        From: Optional[str] = Field(..., description="来源")

    Count: Optional[int] = Field(..., description="匹配结果数量")
    MatchList: Optional[List[MatchItem]] = Field(..., description="匹配结果列表")