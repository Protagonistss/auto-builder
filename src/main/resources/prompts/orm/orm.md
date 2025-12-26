# 从表格配置生成 ORM 实体指导提示词

## 一、输入格式说明

输入是一个 JSON 配置对象，包含以下结构：
- `body.table.columns`: 表格列定义数组，每个列包含：
  - `title`: 列标题（中文显示名）
  - `dataIndex`: 字段标识（用于数据绑定）
  - `width`: 列宽度（可选）
  - `align`: 对齐方式（可选）
- `body.search.fields`: 搜索字段定义数组（可选），每个字段包含：
  - `label`: 字段标签
  - `type`: 字段类型（input/select/date等）
  - `key`: 字段标识

## 二、输出格式说明

输出为 Nop 平台的 ORM 实体定义（XML 格式），文件结构如下：

<orm x:schema="/nop/schema/orm/orm.xdef" xmlns:x="/nop/schema/xdsl.xdef"
     xmlns:biz="biz" xmlns:orm="orm" xmlns:ext="ext">
    <entities>
        <entity name="app.module.EntityName" 
                tableName="entity_name" 
                displayName="实体显示名"
                biz:type="entity"
                registerShortName="true">
            <columns>
                <!-- 字段定义 -->
            </columns>
        </entity>
    </entities>
</orm>## 三、核心生成规则

### 3.1 实体命名规范

1. **实体类名（name 属性）**：
   - 格式：`{basePackage}.{module}.{EntityName}`
   - 示例：`app.mall.Product` → `app.mall.Product`
   - 从 `dataIndex` 或 `title` 提取，转换为 PascalCase
   - 如果 `dataIndex` 是中文，使用 `title` 的拼音或英文翻译

2. **表名（tableName 属性）**：
   - 格式：下划线命名，全小写
   - 示例：`Product` → `product`，`OrderItem` → `order_item`
   - 从实体名转换：PascalCase → snake_case

3. **显示名（displayName 属性）**：
   - 使用表格的标题或实体名称的中文描述
   - 示例：`商品信息`、`订单明细`

### 3.2 字段命名规范

1. **Java 属性名（name 属性）**：
   - 格式：camelCase
   - 从 `dataIndex` 转换：下划线/中文 → camelCase
   - 示例：`商品名称` → `productName`，`商品数量` → `productQuantity`

2. **数据库列名（code 属性）**：
   - 格式：全大写下划线
   - 从 `name` 转换：camelCase → UPPER_SNAKE_CASE
   - 示例：`productName` → `PRODUCT_NAME`
   - 避免 SQL 关键字冲突（如 `order` → `order_no`）

3. **显示名（displayName 属性）**：
   - 直接使用 `title` 字段的值
   - 示例：`商品名称`、`商品数量`

### 3.3 数据类型映射规则

根据字段的语义和类型，映射到对应的 SQL 类型：

| 字段语义/类型 | stdSqlType | stdDomain | precision | scale | 说明 |
|--------------|-----------|-----------|-----------|-------|------|
| 名称/标题/文本 | VARCHAR | string | 100-200 | - | 根据业务含义调整长度 |
| 数量/计数 | INTEGER | - | - | - | 整数类型 |
| 金额/价格 | DECIMAL | - | 18 | 2 | 金额字段固定精度 |
| 百分比 | DECIMAL | - | 5 | 2 | 百分比字段 |
| 日期 | DATE | date | - | - | 仅日期 |
| 日期时间 | DATETIME | datetime | - | - | 日期+时间 |
| 时间 | TIME | time | - | - | 仅时间 |
| 布尔值 | BOOLEAN | - | - | - | true/false |
| 状态/枚举 | VARCHAR | - | 4 | - | 配合字典使用 |
| 来源/类型 | VARCHAR | - | 50 | - | 短文本枚举 |
| 描述/备注 | VARCHAR | text | 500-2000 | - | 长文本 |
| 图片 | VARCHAR | image | 200 | - | 图片URL |
| 文件 | VARCHAR | file | 200 | - | 文件URL |
| 图片列表 | VARCHAR | imageList | 500 | - | 多个图片 |
| 文件列表 | VARCHAR | fileList | 500 | - | 多个文件 |

### 3.4 字段属性配置

1. **主键字段**：
   - 固定字段名：`id`
   - 类型：`VARCHAR(36)`
   - 属性：`primary="true"`, `mandatory="true"`
   - 示例：
   <column name="id" code="ID" propId="1" stdSqlType="VARCHAR" 
           precision="36" primary="true" mandatory="true"/>
   2. **propId 分配**：
   - 从 1 开始递增
   - 主键固定为 1
   - 其他字段按顺序分配 2, 3, 4...

3. **mandatory 属性**：
   - 根据业务语义判断
   - 名称、编号等关键字段通常为 `mandatory="true"`
   - 可选字段不设置或设置为 `false`

4. **字典字段（ext:dict）**：
   - 状态类字段（如 status、state）必须定义字典
   - 有限枚举值字段（≤10个选项）定义字典
   - 字典名格式：`{业务域}_{用途}`，如 `product_status`、`order_source`
   - 字段类型：`VARCHAR(4)`
   - 示例：l
   <column name="status" code="STATUS" propId="5" stdSqlType="VARCHAR" 
           precision="4" ext:dict="product_status"/>
   ### 3.5 必填配置项

1. **实体级别**：
   - `name`: 实体完整类名
   - `tableName`: 数据库表名
   - `displayName`: 显示名称
   - `biz:type`: 业务类型（entity/entity-detail/txn/txn-detail/report/report-detail/config/config-detail）
   - `registerShortName`: 是否注册短名称（通常为 `true`）

2. **字段级别**：
   - `name`: Java 属性名
   - `code`: 数据库列名
   - `propId`: 属性ID（唯一，从1开始）
   - `stdSqlType`: SQL 类型（必填）
   - `displayName`: 显示名称

## 四、生成流程

### 步骤1：解析输入 JSON
1. 提取表格列定义（`body.table.columns`）
2. 提取搜索字段定义（`body.search.fields`，可选）
3. 识别实体名称（从上下文或第一个列推断）

### 步骤2：生成实体定义
1. 确定实体名称和表名
2. 设置 `biz:type`（默认为 `entity`）
3. 添加主键字段 `id`

### 步骤3：生成字段定义
对每个列执行：
1. **字段名转换**：
   - `dataIndex` → Java 属性名（camelCase）
   - Java 属性名 → 数据库列名（UPPER_SNAKE_CASE）

2. **类型推断**：
   - 根据 `title` 语义推断类型
   - 根据 `dataIndex` 名称推断（如包含"数量"→INTEGER，"价格"→DECIMAL）
   - 根据搜索字段的 `type` 辅助推断

3. **属性设置**：
   - `propId`: 按顺序分配（主键=1，其他从2开始）
   - `mandatory`: 根据业务语义判断
   - `stdDomain`: 根据类型设置（如 image、file）
   - `ext:dict`: 状态/枚举字段设置字典

### 步骤4：生成完整 XML
组装为完整的 ORM XML 结构

## 五、示例转换

### 输入 JSON：
{
  "body": {
    "table": {
      "columns": [
        {"title": "商品名称", "dataIndex": "商品名称"},
        {"title": "商品数量", "dataIndex": "商品数量"},
        {"title": "商品来源", "dataIndex": "商品来源"},
        {"title": "商品价格", "dataIndex": "商品价格"}
      ]
    }
  }
}### 输出 ORM XML：
<orm x:schema="/nop/schema/orm/orm.xdef" xmlns:x="/nop/schema/xdsl.xdef"
     xmlns:biz="biz" xmlns:orm="orm" xmlns:ext="ext">
    <entities>
        <entity name="app.mall.Product" 
                tableName="product" 
                displayName="商品"
                biz:type="entity"
                registerShortName="true">
            <columns>
                <column name="id" code="ID" propId="1" stdSqlType="VARCHAR" 
                        precision="36" primary="true" mandatory="true" 
                        displayName="ID"/>
                <column name="productName" code="PRODUCT_NAME" propId="2" 
                        stdSqlType="VARCHAR" precision="200" mandatory="true" 
                        displayName="商品名称"/>
                <column name="productQuantity" code="PRODUCT_QUANTITY" propId="3" 
                        stdSqlType="INTEGER" displayName="商品数量"/>
                <column name="productSource" code="PRODUCT_SOURCE" propId="4" 
                        stdSqlType="VARCHAR" precision="50" 
                        ext:dict="product_source" displayName="商品来源"/>
                <column name="productPrice" code="PRODUCT_PRICE" propId="5" 
                        stdSqlType="DECIMAL" precision="18" scale="2" 
                        displayName="商品价格"/>
            </columns>
        </entity>
    </entities>
</orm>## 六、约束条件

1. **主键固定**：必须使用 `id` 字段，类型 `VARCHAR(36)`
2. **SQL 类型限制**：仅允许 `VARCHAR/CHAR/DATE/TIME/DATETIME/TIMESTAMP/INTEGER/BIGINT/DECIMAL/BOOLEAN/VARBINARY`
3. **禁止字段**：不要手动添加 `IS_DELETED`、`CREATE_TIME`、`UPDATE_TIME`、`CREATED_BY` 等系统字段（平台会自动处理）
4. **字典规范**：状态和枚举字段使用 `VARCHAR(4)` + `ext:dict`
5. **命名规范**：避免 SQL 关键字，使用下划线命名数据库列

## 七、特殊处理

1. **中文字段名处理**：
   - 如果 `dataIndex` 是中文，尝试从 `title` 提取英文含义
   - 或使用拼音转换（如 `商品名称` → `productName`）

2. **类型推断增强**：
   - 字段名包含"数量"、"个数" → `INTEGER`
   - 字段名包含"价格"、"金额"、"费用" → `DECIMAL(18,2)`
   - 字段名包含"日期" → `DATE` 或 `DATETIME`
   - 字段名包含"状态"、"类型" → `VARCHAR(4)` + 字典
   - 字段名包含"图片"、"照片" → `VARCHAR(200)` + `stdDomain="image"`
   - 字段名包含"文件"、"附件" → `VARCHAR(200)` + `stdDomain="file"`

3. **搜索字段辅助**：
   - 如果搜索字段的 `type` 为 `select`，对应的表格列可能是枚举类型
   - 如果搜索字段的 `type` 为 `date`，对应的表格列是日期类型

## 八、输出要求

1. 生成的 XML 必须符合 `references/orm.xdef` 规范
2. 所有必填属性必须设置
3. 字段顺序：主键 → 业务字段（按输入顺序）
4. 代码格式：缩进 4 个空格，属性换行对齐
5. 注释：为复杂字段添加注释说明