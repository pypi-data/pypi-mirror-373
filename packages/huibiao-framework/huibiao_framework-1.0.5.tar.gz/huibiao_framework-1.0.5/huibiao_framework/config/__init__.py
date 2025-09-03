from dotenv import load_dotenv

load_dotenv(".env")

from .config import MinioConfig, ClientConfig, ModelConfig

__all__ = ["MinioConfig", "ClientConfig", "ModelConfig"]
