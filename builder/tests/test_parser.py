import pytest
from builder.services.parser import OrmXmlParser

class TestOrmXmlParser:
    def test_parse_simple_entity(self):
        """Test parsing a simple entity XML"""
        parser = OrmXmlParser()
        xml = """<entity name="com.example.Test" tableName="test_table">
            <column name="id" />
        </entity>"""
        
        result = parser.parse(xml)
        
        assert result.entity_name == "com.example.Test"
        assert result.table_name == "test_table"
        assert '<entity' in result.xml
        assert 'name="com.example.Test"' in result.xml

    def test_parse_with_markdown_blocks(self):
        """Test parsing XML wrapped in markdown code blocks"""
        parser = OrmXmlParser()
        xml = """```xml
        <entity name="com.example.Test" tableName="test_table">
            <column name="id" />
        </entity>
        ```"""
        
        result = parser.parse(xml)
        
        assert result.entity_name == "com.example.Test"
        assert result.table_name == "test_table"

    def test_parse_with_namespace_wrapper(self):
        """Test parsing when AI returns wrapped XML (e.g. inside <orm>)"""
        parser = OrmXmlParser()
        xml = """<orm>
            <entity name="com.example.Test" tableName="test_table">
                <column name="id" />
            </entity>
        </orm>"""
        
        result = parser.parse(xml)
        
        # It should extract the entity specifically
        assert result.entity_name == "com.example.Test"
        assert result.table_name == "test_table"
        assert '<entity' in result.xml
        assert '<orm>' not in result.xml  # Should extract just the entity

    def test_parse_with_namespaces(self):
        """Test parsing with namespace attributes"""
        parser = OrmXmlParser()
        xml = """<entity xmlns:biz="biz" name="com.example.Test" biz:type="foo">
            <column name="id" />
        </entity>"""
        
        result = parser.parse(xml)
        
        assert result.entity_name == "com.example.Test"
        # Namespaces might be stripped in the output string depending on implementation
        # The key is that it parses correctly

    def test_parse_error(self):
        """Test invalid XML"""
        parser = OrmXmlParser()
        xml = "<entity>unclosed"
        
        with pytest.raises(ValueError) as exc:
            parser.parse(xml)
        assert "XML 解析失败" in str(exc.value)

    def test_missing_entity_tag(self):
        """Test XML without entity tag"""
        parser = OrmXmlParser()
        xml = "<other>content</other>"
        
        with pytest.raises(ValueError) as exc:
            parser.parse(xml)
        assert "XML 解析失败" in str(exc.value)
