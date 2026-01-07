from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Dict, Optional
from pydantic import BaseModel


class XmlBuildConfig(BaseModel):
    """XML 构建类型配置"""
    name: str  # 类型名称
    xml_path: str  # 目标 XML 文件路径
    parent_xpath: str  # 父容器 XPath
    element_matcher: str  # 元素匹配属性名
    element_tag: str  # 元素标签名
    display_name: str  # 显示名称（中文）


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

    # ORM 配置
    orm_xml_path: str = "builder/templates/app.orm.xml"  # ORM 文件路径
    orm_default_package: str = "app.module"  # 默认包名前缀
    orm_table_prefix: str = ""  # 表名前缀（如 "lt_", "mall_"）

    # 构建配置
    project_root: str = "."  # 项目根目录
    default_build_timeout: int = 300  # 默认构建超时时间（秒）

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()


# XML 构建类型配置
XML_BUILD_TYPES: Dict[str, XmlBuildConfig] = {
    "orm": XmlBuildConfig(
        name="ORM Entity",
        xml_path=settings.orm_xml_path,
        parent_xpath=".//entities",
        element_matcher="name",
        element_tag="entity",
        display_name="实体"
    ),
    "config": XmlBuildConfig(
        name="配置项",
        xml_path="builder/templates/app.config.xml",
        parent_xpath=".//settings",
        element_matcher="key",
        element_tag="setting",
        display_name="配置"
    ),
    "api": XmlBuildConfig(
        name="API 定义",
        xml_path="builder/templates/api.xml",
        parent_xpath=".//endpoints",
        element_matcher="path",
        element_tag="endpoint",
        display_name="接口"
    )
}


def get_xml_config(xml_type: str) -> Optional[XmlBuildConfig]:
    """
    获取 XML 类型配置

    Args:
        xml_type: XML 类型标识（orm/config/api 等）

    Returns:
        XmlBuildConfig 对象，不存在返回 None
    """
    return XML_BUILD_TYPES.get(xml_type)
