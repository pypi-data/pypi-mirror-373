from huibiao_framework.utils.meta_class import OsAttrMeta, ConstantClass


class MinioConfig(metaclass=OsAttrMeta):
    ENDPOINT: str
    AK: str
    SK: str
    BUCKET_NAME: str = "huibiao"
    OSS_SECURE: bool = False


class LlmModelNameConstant(ConstantClass):
    HuiZeQwen32bQwq = "HuiZeQwen32bQwq"

class ModelConfig(metaclass=OsAttrMeta):
    """大语言模型的参数"""
    LLM_MODEL_TYPE: str = "HuiZeQwen32bQwq"
    REQUEST_URL: str = "http://vllm-qwen-32b.model.hhht.ctcdn.cn:9080/common/query"


class ClientConfig(metaclass=OsAttrMeta):
    SEARCH_URL: str = "http://knowledge-qa-search-pipeline-mgr-svc-dev.ctcdn.cn:9080"
    IMAGE_OCR_TYY_URL: str = (
        "http://tender-document-parser.hhht.ctcdn.cn:9080/image_ocr"
    )
    LAYOUT_DETECTION_TYY_URL: str = (
        "http://tender-document-parser.hhht.ctcdn.cn:9080/image_layout"
    )
    EMBED_URL: str = "http://dmx.model.zz.ctcdn.cn:9080/vllm-huize-embedding-zhengwu0329/common/encode"
    CHUNK_URL: str = (
        "http://dmx.model.dev.zz.ctcdn.cn:9080/text-content-chunk-tools-dev/chunk"
    )
