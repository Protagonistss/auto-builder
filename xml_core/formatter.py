"""XML 格式化器"""

from pathlib import Path
from typing import Optional
from lxml import etree

from .namespace import NamespaceHandler


class XmlFormatter:
    """XML 格式化器"""

    def __init__(
        self,
        encoding: str = "utf-8",
        pretty_print: bool = True,
        xml_declaration: bool = True
    ):
        """
        初始化格式化器

        Args:
            encoding: 文件编码
            pretty_print: 是否美化输出
            xml_declaration: 是否包含 XML 声明
        """
        self.encoding = encoding
        self.pretty_print = pretty_print
        self.xml_declaration = xml_declaration
        self.ns_handler = NamespaceHandler()

    def serialize(
        self,
        tree: etree._ElementTree,
        strip_child_ns: bool = True
    ) -> str:
        """
        序列化 XML 树为字符串

        Args:
            tree: ElementTree 对象
            strip_child_ns: 是否通过提升命名空间来移除子元素的冗余声明

        Returns:
            XML 字符串
        """
        # 如果需要移除子元素命名空间，进行命名空间提升
        if strip_child_ns:
            tree = self._hoist_namespaces(tree)

        xml_content = etree.tostring(
            tree,
            encoding=self.encoding,
            pretty_print=self.pretty_print,
            xml_declaration=self.xml_declaration
        )

        xml_str = xml_content.decode(self.encoding)

        return xml_str

    def _hoist_namespaces(self, tree: etree._ElementTree) -> etree._ElementTree:
        """
        提升命名空间：将所有子节点使用的命名空间移动到根节点
        这样 lxml 在序列化时就会自动移除子节点中冗余的 xmlns 声明

        Args:
            tree: 原始 ElementTree

        Returns:
            处理后的新 ElementTree
        """
        root = tree.getroot()

        # 1. 收集全树所有的命名空间
        all_ns = dict(root.nsmap)
        for elem in root.iter():
            for prefix, uri in elem.nsmap.items():
                # 跳过默认命名空间（None）如果它会导致冲突，或者是 xml 命名空间
                if prefix and prefix not in all_ns and prefix != 'xml':
                    all_ns[prefix] = uri

        # 如果根节点的 nsmap 已经包含了所有，且只需要简单的 cleanup
        if all_ns == root.nsmap:
            etree.cleanup_namespaces(root)
            return tree

        # 2. 创建一个新的根节点，带上全量的 nsmap
        # 注意：使用 etree.Element 时，nsmap 参数一旦设置就不可变
        new_root = etree.Element(root.tag, attrib=root.attrib, nsmap=all_ns)

        # 3. 搬运内容
        new_root.text = root.text
        new_root.tail = root.tail
        for child in root:
            new_root.append(child)

        # 4. 清理多余的命名空间声明
        # 此时因为根节点有了定义，子节点的定义会被识别为冗余并移除
        etree.cleanup_namespaces(new_root)

        return etree.ElementTree(new_root)

    def write_tree(
        self,
        tree: etree._ElementTree,
        file_path: str,
        strip_child_ns: bool = True,
        auto_add_namespaces: bool = True
    ) -> None:
        """
        写入 XML 树到文件

        Args:
            tree: ElementTree 对象
            file_path: 文件路径
            strip_child_ns: 是否移除子元素的命名空间声明
            auto_add_namespaces: 是否自动添加命名空间声明（保留参数以兼容接口，实际由 _hoist_namespaces 处理）
        """
        # 序列化树 (serialize 内部已经处理了命名空间提升)
        xml_str = self.serialize(tree, strip_child_ns=strip_child_ns)

        with open(file_path, "wb") as f:
            f.write(xml_str.encode(self.encoding))

    def format_element(
        self,
        element: etree._Element,
        strip_child_ns: bool = True
    ) -> str:
        """
        格式化单个元素

        Args:
            element: Element 对象
            strip_child_ns: 是否移除子元素的命名空间声明

        Returns:
            XML 字符串
        """
        # 为了复用 _hoist_namespaces 逻辑，我们需要临时把 element 包装成 tree
        # 但如果不希望改变原 element 的结构（比如它没有 parent），我们得复制一份
        if strip_child_ns:
            # 深拷贝元素以避免修改原对象
            element_copy =  etree.fromstring(etree.tostring(element))
            tree = etree.ElementTree(element_copy)
            tree = self._hoist_namespaces(tree)
            element = tree.getroot()

        xml_content = etree.tostring(
            element,
            encoding=self.encoding,
            pretty_print=self.pretty_print
        )

        return xml_content.decode(self.encoding)

    def prettify(self, xml: str) -> str:
        """
        美化 XML 字符串

        Args:
            xml: XML 字符串

        Returns:
            美化后的 XML 字符串
        """
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml.encode(self.encoding), parser)
            return etree.tostring(
                root,
                encoding=self.encoding,
                pretty_print=True
            ).decode(self.encoding)
        except Exception:
            # 如果解析失败，返回原字符串
            return xml
