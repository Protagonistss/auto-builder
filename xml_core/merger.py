"""XML 合并器"""

import logging
from typing import Optional, Callable, List
from pathlib import Path
from pydantic import BaseModel
from lxml import etree

from .parser import XmlParser
from .formatter import XmlFormatter
from .exceptions import XmlMergeError, XmlFileNotFoundError
from .settings import MergeOptions


logger = logging.getLogger(__name__)


class MergeResult(BaseModel):
    """合并结果"""
    identifier: str
    action: str  # created/updated/skipped


class XmlMerger:
    """XML 元素合并器"""

    def __init__(self, xml_path: str, encoding: str = "utf-8", namespaces: Optional[List[str]] = None):
        """
        初始化合并器

        Args:
            xml_path: XML 文件路径
            encoding: 文件编码
            namespaces: 支持的命名空间前缀列表
        """
        self.xml_path = Path(xml_path)
        self.encoding = encoding
        self.parser = XmlParser(encoding=encoding, namespaces=namespaces)
        self.formatter = XmlFormatter(encoding=encoding)

    def merge_element(
        self,
        element_xml: str,
        options: MergeOptions
    ) -> MergeResult:
        """
        合并 XML 元素到目标文件

        Args:
            element_xml: 元素 XML 片段
            options: 合并选项

        Returns:
            MergeResult: 合并结果

        Raises:
            XmlFileNotFoundError: 文件不存在
            XmlMergeError: 合并失败
        """
        if not self.xml_path.exists():
            raise XmlFileNotFoundError(f"文件不存在: {self.xml_path}")

        # 1. 解析元素 - 直接返回根元素（XML 片段的第一个元素）
        element = self.parser.parse_fragment(element_xml)

        # 获取元素标识
        identifier = self._get_element_identifier(element, options.element_matcher)
        if not identifier:
            raise XmlMergeError("无法获取元素标识，请检查 element_matcher 配置")

        # 2. 解析目标文件
        tree = self.parser.parse_file(str(self.xml_path))
        root = self.parser.get_root(tree)

        # 3. 查找父容器
        parent = self.parser.find_element(root, options.parent_xpath)
        if parent is None:
            raise XmlMergeError(f"未找到父容器: {options.parent_xpath}")

        # 4. 查找现有元素
        existing = self._find_element_by_identifier(
            parent,
            element.tag,
            identifier,
            options.element_matcher
        )

        # 5. 合并或追加
        if existing is not None:
            if options.merge_strategy == "always_append":
                parent.append(element)
                action = "created"
            elif options.merge_strategy == "force_replace":
                if existing is not None:
                    parent.replace(existing, element)
                else:
                    parent.append(element)
                action = "updated"
            else:  # replace_or_append
                parent.replace(existing, element)
                action = "updated"
        else:
            parent.append(element)
            action = "created"

        # 6. 写回文件
        self.formatter.write_tree(
            tree,
            str(self.xml_path),
            strip_child_ns=options.strip_ns_on_children
        )

        return MergeResult(identifier=identifier, action=action)

    def _get_element_identifier(
        self,
        element: etree._Element,
        matcher_attr: Optional[str]
    ) -> Optional[str]:
        """
        获取元素标识

        Args:
            element: XML 元素
            matcher_attr: 匹配属性名

        Returns:
            元素标识
        """
        if matcher_attr:
            return element.get(matcher_attr)

        # 默认使用 id, name, key 属性
        for attr in ['id', 'name', 'key']:
            value = element.get(attr)
            if value:
                return value

        return None

    def _find_element_by_identifier(
        self,
        parent: etree._Element,
        tag_name: str,
        identifier: str,
        matcher_attr: Optional[str]
    ) -> Optional[etree._Element]:
        """
        在父元素中查找指定标识的元素

        Args:
            parent: 父元素
            tag_name: 标签名
            identifier: 标识值
            matcher_attr: 匹配属性名

        Returns:
            找到的元素，未找到返回 None
        """
        if matcher_attr:
            attr_name = matcher_attr
        else:
            # 自动检测匹配属性
            attr_name = None
            for child in parent.findall(tag_name):
                for attr in ['id', 'name', 'key']:
                    if child.get(attr):
                        attr_name = attr
                        break
                if attr_name:
                    break

        if not attr_name:
            return None

        for child in parent.findall(tag_name):
            if child.get(attr_name) == identifier:
                return child

        return None

    def find_element(
        self,
        xpath: str,
        namespace_map: Optional[dict] = None
    ) -> Optional[etree._Element]:
        """
        在文件中查找元素

        Args:
            xpath: XPath 表达式
            namespace_map: 命名空间映射

        Returns:
            找到的元素，未找到返回 None
        """
        tree = self.parser.parse_file(str(self.xml_path))
        root = self.parser.get_root(tree)
        return self.parser.find_element(root, xpath, namespace_map)

    def replace_element(
        self,
        xpath: str,
        new_element: etree._Element,
        namespace_map: Optional[dict] = None
    ) -> bool:
        """
        替换元素

        Args:
            xpath: 目标元素 XPath
            new_element: 新元素
            namespace_map: 命名空间映射

        Returns:
            是否成功替换
        """
        tree = self.parser.parse_file(str(self.xml_path))
        root = self.parser.get_root(tree)
        old_element = self.parser.find_element(root, xpath, namespace_map)

        if old_element is None:
            return False

        parent = old_element.getparent()
        if parent is None:
            return False

        parent.replace(old_element, new_element)
        self.formatter.write_tree(tree, str(self.xml_path))
        return True
