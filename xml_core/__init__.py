"""XML 核心包 - 通用 XML 处理库

提供 XML 解析、合并、命名空间处理等通用功能。
"""

from .core import XmlCore
from .merger import XmlMerger, MergeResult
from .parser import XmlParser
from .formatter import XmlFormatter
from .namespace import NamespaceHandler
from .settings import XmlCoreSettings, MergeOptions
from .exceptions import (
    XmlCoreError,
    XmlParseError,
    XmlMergeError,
    XmlFileNotFoundError,
    XmlValidationError
)


__version__ = "0.1.0"
__all__ = [
    "XmlCore",
    "XmlMerger",
    "XmlParser",
    "XmlFormatter",
    "NamespaceHandler",
    "MergeResult",
    "XmlCoreSettings",
    "MergeOptions",
    "XmlCoreError",
    "XmlParseError",
    "XmlMergeError",
    "XmlFileNotFoundError",
    "XmlValidationError",
]