from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ChunkReqDto(BaseModel):
    """
    请求参数示例
    {
        "Action": "CommonChunk",
        "TextData": "ddddddddddddd",
        "FileName": "ddddddd",
        "IsJson": false
    }
    """

    Action: str = "CommonChunk"
    TextData: str
    FileName: str
    IsJson: bool


class ChunkRespVo(BaseModel):
    """
    返回值示例
    {
    "code": 0,
    "result": {
        "docInfo": {
            "docId": 3714767230599517013,
            "docName": "ddddddd"
        },
        "contents": [
            {
                "info": {
                    "contentId": 1,
                    "docTitle": "ddddddd",
                    "subtitle": "",
                    "text": "ddddddddddddd",
                    "offset": 13,
                    "strategy": "ARTICLE_SPLITTER"
                },
                "chunks": [
                    {
                        "id": 1,
                        "text": "ddddddd\nddddddddddddd",
                        "type": "HEAD_SENTENCE_FEATURE",
                        "offset": 21
                    }
                ]
            }
        ],
        "outline": {
            "outlineStr": "",
            "offset": 0,
            "items": [],
            "type": "RE_OUTLINE"
        },
        "redHeader": {
            "红头": "",
            "发文号": "",
            "发文单位": "",
            "发文日期": "",
            "发文类型": "",
            "发文数量": ""
        }
    },
    "message": "success"
    }
    """

    docInfo: Optional["DocInfo"]
    contents: Optional[List["ContentItem"]]
    outline: Optional["Outline"]
    redHeader: Optional[Dict[str, Any]]


class DocInfo(BaseModel):
    docId: int
    docName: str


class Chunk(BaseModel):
    id: int
    text: str
    type: str
    offset: int


class ContentInfo(BaseModel):
    contentId: int
    docTitle: str
    subtitle: str
    text: str
    offset: int
    strategy: str


class ContentItem(BaseModel):
    info: ContentInfo
    chunks: List[Chunk]


class Outline(BaseModel):
    outlineStr: str
    offset: int
    items: List
    type: str
