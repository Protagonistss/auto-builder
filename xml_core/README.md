# XML Core

一个通用且健壮的 XML 处理库，专为**自动化代码生成**和**增量合并**场景设计。它能完美处理 AI 生成的不完整 XML 片段，并提供安全的 DOM 级合并与格式化功能。

## ✨ 核心特性

*   **🛡️ 防御性解析 (Defensive Parsing)**
    *   自动处理 Markdown 代码块（```xml ... ```）。
    *   支持解析不带根节点、缺失 `xmlns` 声明的 XML 片段。
    *   利用 `lxml` 的 recover 模式修复轻微格式错误。

*   **⚡ 智能合并 (Smart Merging)**
    *   支持多种合并策略：`replace_or_append`（智能更新）、`force_replace`（覆盖）、`always_append`（追加）。
    *   自动识别元素标识符（优先匹配 `id`, `name`, `key` 属性）。
    *   保持原有 XML 结构和注释完整性。

*   **🧹 命名空间清洗 (Namespace Hoisting)**
    *   **去正则化**：完全基于 DOM 操作，不使用正则表达式修改 XML，杜绝误伤风险。
    *   **自动提升**：将子元素分散的命名空间声明自动提升至根节点。
    *   **输出整洁**：利用 `lxml.cleanup_namespaces` 自动移除冗余的 `xmlns` 属性。

*   **🔌 通用性与解耦**
    *   不绑定特定业务逻辑。
    *   支持通过 `namespaces` 参数自定义支持的命名空间前缀（如 `android`, `maven`, `spring` 等）。

## 🚀 快速开始

### 1. 基础合并

适用于通用的配置文件合并场景。

```python
from xml_core import XmlCore

# 初始化核心对象
core = XmlCore("config.xml")

# 待合并的 XML 片段（可以是不完整的）
fragment = """
<item key="timeout" value="60">
    <description>Connection timeout</description>
</item>
"""

# 执行合并
# 自动在 .//items 下查找 key="timeout" 的元素进行更新，不存在则创建
result = core.merge_element(
    element_xml=fragment,
    parent_xpath=".//items",
    element_matcher="key"  # 指定匹配属性
)

print(f"结果: {result.action} ({result.identifier})")
```

### 2. ORM 场景

```python
from xml_core import XmlCore

# 使用工厂方法（预置了 Nop 常用命名空间）
core = XmlCore.for_orm("app.orm.xml")

# 模拟 AI 返回的代码块
ai_response = """
```xml
<entity name="io.nop.app.LoginLog" tableName="nop_login_log">
    <column name="userId" code="USER_ID" stdSqlType="VARCHAR" />
</entity>
```
"""

# 一键合并 Entity
# 默认 parent_xpath=".//entities", element_matcher="name"
result = core.merge_entity(ai_response)
```
**默认配置说明：**
*   **支持的前缀 (Namespaces)**: `biz`, `ext`, `orm`, `i18n-en`, `ui`, `x`, `xpl`, `xs`。
*   **Schema 映射**: 
    *   `x`: `/nop/schema/xdsl.xdef`
    *   `xpl`: `/nop/schema/xpl.xdef`
*   **实体容器**: 默认在 `.//entities` 路径下查找并合并。
*   **实体标识**: 默认使用 `name` 属性作为实体的唯一标识。
```

### 3. 自定义命名空间 (Custom Namespaces)

如果您处理的是 Maven `pom.xml` 或 Android `layout.xml`，可以配置自定义前缀。

```python
# 初始化支持 Android 命名空间的解析器
core = XmlCore(
    "layout.xml", 
    namespaces=['android', 'app', 'tools']
)

layout_fragment = """
<TextView
    android:id="@+id/message"
    android:text="Hello World" />
"""

core.merge_element(
    element_xml=layout_fragment,
    parent_xpath=".//LinearLayout",
    element_matcher="android:id"
)
```

## ⚙️ API 说明

### `XmlCore` 类

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `xml_path` | str | 必填 | XML 文件路径 |
| `encoding` | str | "utf-8" | 文件编码 |
| `namespaces` | list[str] | None | 支持的命名空间前缀列表。不传则使用默认的 Nop 平台前缀集合。 |
| `pretty_print` | bool | True | 是否美化输出（缩进） |

### `merge_element` 方法

| 参数 | 说明 |
| :--- | :--- |
| `element_xml` | 待合并的 XML 字符串片段 |
| `parent_xpath` | 目标父节点的 XPath |
| `element_matcher` | 用于匹配现有元素的属性名（如 `id`）。若不传，自动尝试 `id`, `name`, `key`。 |
| `merge_strategy` | `replace_or_append` (默认), `force_replace`, `always_append` |

## 🛠️ 开发者指南

本项目使用 `uv` 进行依赖管理。

**安装依赖:**
```bash
uv sync
```

**运行测试:**
```bash
uv run python -m pytest xml_core/tests
```
