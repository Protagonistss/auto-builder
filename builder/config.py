from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # AI 配置
    zhipu_api_key: str
    ai_model: str = "glm-4.7"
    ai_provider: str = "zhipu"

    # 服务配置
    port: int = 8000
    host: str = "0.0.0.0"

    # 文件上传配置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads/conversations"
    allowed_file_types: List[str] = [
        "application/json",
        "text/plain",
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/octet-stream",  # Windows 常见文件类型
    ]

    # 对话配置
    max_context_messages: int = 20  # 保留的上下文消息数量

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
