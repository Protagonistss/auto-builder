"""XML Core 配置"""

from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class XmlCoreSettings(BaseModel):
    """XML 核心配置"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    xml_path: Path = Field(description="XML 文件路径")
    encoding: str = Field(default="utf-8", description="文件编码")
    pretty_print: bool = Field(default=True, description="是否美化输出")
    xml_declaration: bool = Field(default=True, description="是否包含 XML 声明")

    # 命名空间配置
    auto_detect_namespaces: bool = Field(
        default=True,
        description="是否自动检测命名空间"
    )
    strip_child_namespaces: bool = Field(
        default=True,
        description="是否移除子元素的命名空间声明"
    )
    namespaces: list[str] = Field(
        default=['biz', 'ext', 'orm', 'i18n-en', 'ui', 'x', 'xpl', 'xs'],
        description="支持的命名空间前缀列表"
    )


class MergeOptions(BaseModel):
    """合并选项"""

    parent_xpath: str = Field(description="父元素 XPath")
    element_matcher: Optional[str] = Field(
        default=None,
        description="元素匹配属性名（如 'name'）"
    )
    merge_strategy: str = Field(
        default="replace_or_append",
        description="合并策略: replace_or_append, always_append, force_replace"
    )
    strip_ns_on_children: bool = Field(
        default=True,
        description="是否移除子元素的命名空间声明"
    )
