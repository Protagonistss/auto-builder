from lxml import etree
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import re

from ..config import settings


class WriteEntityResult(BaseModel):
    """写入结果"""
    entity_name: str
    action: str  # created/updated


class OrmXmlService:
    """ORM XML 文件操作服务"""

    def __init__(self):
        self.xml_file_path = Path(settings.orm_xml_path)
        self._namespace_map = {
            'x': '/nop/schema/xdsl.xdef',
            'xpl': '/nop/schema/xpl.xdef'
        }

    def write_entity(self, entity_xml: str) -> WriteEntityResult:
        """
        智能合并 entity 到 app.orm.xml

        Args:
            entity_xml: entity XML 片段

        Returns:
            WriteEntityResult: 写入结果

        Raises:
            ValueError: XML 解析失败或缺少必填字段
            FileNotFoundError: 文件不存在
            IOError: 文件操作失败
        """
        # 1. 解析输入的 entity XML
        new_entity = self._parse_entity_xml(entity_xml)
        entity_name = new_entity.get("name")

        if not entity_name:
            raise ValueError("entity 标签缺少必填的 name 属性")

        # 2. 读取目标文件
        if not self.xml_file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.xml_file_path}")

        # 先读取文件内容，检查并修复命名空间声明
        with open(self.xml_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 检查文件中使用的命名空间
        used_namespaces = set()
        for prefix in ['biz', 'ext', 'orm', 'i18n-en', 'ui']:
            if f'{prefix}:' in file_content:
                used_namespaces.add(prefix)

        # 检查根元素 <orm> 是否已声明这些命名空间
        root_start = file_content.find('<orm')
        if root_start != -1:
            root_end = file_content.find('>', root_start)
            root_tag = file_content[root_start:root_end + 1]

            # 添加缺失的命名空间声明
            for prefix in used_namespaces:
                ns_decl = f'xmlns:{prefix}="{prefix}"'
                if ns_decl not in root_tag and f'xmlns:{prefix}=' not in root_tag:
                    # 在 <orm 标签中插入命名空间声明
                    root_tag = root_tag.replace('<orm', f'<orm {ns_decl}')

            # 替换文件内容
            file_content = file_content[:root_start] + root_tag + file_content[root_end + 1:]

            # 重新写入修复后的文件
            with open(self.xml_file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

        parser = etree.XMLParser(remove_blank_text=False, remove_comments=False)
        tree = etree.parse(self.xml_file_path, parser)
        root = tree.getroot()

        # 3. 查找 entities 节点
        entities_node = root.find(".//entities", self._namespace_map)
        if entities_node is None:
            raise ValueError("app.orm.xml 中未找到 entities 节点")

        # 4. 检查是否重复
        existing_entity = self._find_entity_by_name(root, entity_name)

        # 移除 entity 上可能存在的命名空间声明（保持与 AI 输出一致）
        for ns_attr in list(new_entity.attrib.keys()):
            if ns_attr.startswith('xmlns:'):
                del new_entity.attrib[ns_attr]

        if existing_entity is not None:
            # 替换
            entities_node.replace(existing_entity, new_entity)
            action = "updated"
        else:
            # 追加
            entities_node.append(new_entity)
            action = "created"

        # 5. 写回文件
        self._write_tree(tree)

        return WriteEntityResult(
            entity_name=entity_name,
            action=action
        )

    def _parse_entity_xml(self, xml: str) -> etree._Element:
        """
        解析 entity XML 片段

        Args:
            xml: entity XML 字符串

        Returns:
            lxml Element 对象

        Raises:
            ValueError: XML 解析失败或未找到 entity 标签
        """
        # 清理代码块标记
        cleaned = xml.replace("```xml", "").replace("```", "").strip()

        # 检测实际使用的命名空间，临时包装以便解析
        used_namespaces = []
        if 'biz:' in cleaned:
            used_namespaces.append('xmlns:biz="biz"')
        if 'ext:' in cleaned:
            used_namespaces.append('xmlns:ext="ext"')
        if 'orm:' in cleaned:
            used_namespaces.append('xmlns:orm="orm"')
        if 'i18n-en:' in cleaned:
            used_namespaces.append('xmlns:i18n-en="i18n-en"')
        if 'ui:' in cleaned:
            used_namespaces.append('xmlns:ui="ui"')

        # 如果使用了命名空间前缀，临时包装以提供命名空间上下文
        if used_namespaces:
            ns_decls = ' '.join(used_namespaces)
            wrapper = f'<root {ns_decls}>{cleaned}</root>'
        else:
            wrapper = f'<root>{cleaned}</root>'

        # 调试：打印处理后的 XML（前200字符）
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"包装后的 XML: {wrapper[:300]}...")

        parser = etree.XMLParser(remove_blank_text=False)

        try:
            # 解析包装后的 XML
            root = etree.fromstring(wrapper.encode("utf-8"), parser)
            entity = root.find(".//entity")
            if entity is None:
                raise ValueError("未找到 entity 标签")
            return entity
        except Exception as e:
            logger.error(f"XML 解析失败: {e}\nXML 内容: {cleaned[:500]}")
            raise ValueError(f"XML 解析失败: {e}")

    def _find_entity_by_name(self, root: etree._Element, entity_name: str) -> Optional[etree._Element]:
        """
        查找指定名称的 entity

        Args:
            root: XML 根节点
            entity_name: entity 的 name 属性值

        Returns:
            找到的 entity 节点，未找到返回 None
        """
        entities_node = root.find(".//entities", self._namespace_map)
        if entities_node is None:
            return None

        for entity in entities_node.findall("entity"):
            if entity.get("name") == entity_name:
                return entity
        return None

    def _write_tree(self, tree: etree._ElementTree):
        """
        写回文件

        Args:
            tree: lxml ElementTree 对象
        """
        # 序列化 XML
        xml_content = etree.tostring(
            tree,
            encoding="utf-8",
            pretty_print=True,
            xml_declaration=True
        )

        # 解码为字符串
        xml_str = xml_content.decode('utf-8')

        # 移除所有子元素上的 xmlns:* 声明（保留根元素的）
        import re

        # 对于 <entity>, <column>, <comment> 等标签，移除其上的 xmlns:* 声明
        def remove_ns_attrs(match):
            tag_name = match.group(1)
            attrs = match.group(2)
            # 移除 xmlns:xxx="xxx" 格式的属性
            cleaned_attrs = re.sub(r'\s+xmlns:[a-z0-9\-]+="[^"]*"', '', attrs)
            return f'<{tag_name}{cleaned_attrs}>'

        xml_str = re.sub(r'<(entity|column|comment)([^>]*)>', remove_ns_attrs, xml_str)

        with open(self.xml_file_path, "wb") as f:
            f.write(xml_str.encode('utf-8'))
