from ..models.task import OrmGenerationResult
from xml_core.parser import XmlParser
from xml_core.formatter import XmlFormatter
from xml_core.exceptions import XmlParseError


class OrmXmlParser:
    def __init__(self):
        self.parser = XmlParser()
        self.formatter = XmlFormatter()

    def parse(self, ai_response: str) -> OrmGenerationResult:
        """解析 AI 返回的 XML"""
        try:
            # 使用 xml_core 解析并查找 entity 标签
            # parse_fragment 会自动处理代码块标记和命名空间
            entity_element = self.parser.parse_fragment(
                ai_response,
                target_tag="entity"
            )

            entity_name = entity_element.get("name", "app.module.Entity")
            table_name = entity_element.get("tableName", "entity_table")

            # 格式化为字符串
            xml_content = self.formatter.format_element(entity_element)

            return OrmGenerationResult(
                xml=xml_content,
                entity_name=entity_name,
                table_name=table_name,
            )

        except XmlParseError as e:
            raise ValueError(f"XML 解析失败: {e}")
