# Builder - AI 驱动的 ORM 实体生成器

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128%2B-009688)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0%2B-e92063)
![License](https://img.shields.io/badge/license-MIT-green)

**Builder** 是一个基于 **FastAPI** 和 **智谱 AI (GLM-4.7)** 的智能代码生成服务。只需上传简单的 JSON 配置文件，即可自动分析实体关系，生成高质量的 ORM 实体类代码（如 MyBatis/Plus、Hibernate 等）。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备

确保你的系统已安装 **Python 3.11+**。本项目使用 [uv](https://github.com/astral-sh/uv) 进行极速包管理（推荐），也可以使用标准的 pip。

**安装 uv (推荐):**
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 获取代码与安装依赖

```bash
git clone git@github.com:Protagonistss/auto-backend.git
cd auto-backend

# 使用 uv 同步所有依赖
uv sync
```

### 3. 配置 API Key

复制环境变量模板并填入你的智谱 AI Key：

```bash
cp .env.example .env
# 编辑 .env 文件，修改 ZHIPU_API_KEY=你的Key
```

### 4. 启动服务

**方式一：通过 Python 模块启动（推荐）**
利用 `main.py` 中的配置直接启动：
```bash
uv run python -m builder.main
```

**方式二：通过 Uvicorn 命令行启动**
```bash
uv run uvicorn builder.main:app --reload
```

服务启动后访问：
- **Swagger UI (接口文档)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **服务状态**: [http://localhost:8000/](http://localhost:8000/)

---

## ⚙️ 配置说明 (Configuration)

项目配置通过环境变量 (`.env`) 管理。

| 变量名 | 必填 | 默认值 | 说明 |
| :--- | :---: | :--- | :--- |
| `ZHIPU_API_KEY` | ✅ | - | 智谱 AI 开放平台申请的 API Key |
| `AI_MODEL` | ❌ | `glm-4.7` | 使用的 AI 模型版本 |
| `AI_PROVIDER` | ❌ | `zhipu` | AI 提供商标识 |
| `PORT` | ❌ | `8000` | 服务监听端口 |
| `HOST` | ❌ | `0.0.0.0` | 服务绑定地址 |
| `MAX_FILE_SIZE` | ❌ | `10485760` | 上传文件大小限制 (Bytes, 默认 10MB) |

---

## 📖 使用指南 (Usage)

### 1. 准备实体定义文件 (JSON)

创建一个 JSON 文件（例如 `entity_config.json`），定义你需要生成的表结构：

```json
{
  "database": "mysql",
  "orm_type": "mybatis-plus",
  "tables": [
    {
      "name": "sys_user",
      "comment": "系统用户表",
      "columns": [
        {"name": "id", "type": "bigint", "primary": true, "auto_increment": true, "comment": "主键ID"},
        {"name": "username", "type": "varchar", "length": 50, "not_null": true, "comment": "用户名"},
        {"name": "password", "type": "varchar", "length": 100, "comment": "加密密码"},
        {"name": "email", "type": "varchar", "length": 100, "comment": "邮箱"},
        {"name": "created_at", "type": "datetime", "comment": "创建时间"}
      ]
    },
    {
      "name": "sys_role",
      "comment": "角色表",
      "columns": [
        {"name": "id", "type": "bigint", "primary": true},
        {"name": "code", "type": "varchar", "length": 50, "comment": "角色编码"},
        {"name": "name", "type": "varchar", "length": 50, "comment": "角色名称"}
      ]
    }
  ]
}
```

### 2. 调用生成接口

使用 API 上传该文件以生成代码：

**接口地址**: `POST /api/upload`

**Curl 示例**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@entity_config.json"
```

**响应示例**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully, processing started."
}
```

### 3. 获取结果

*(注：根据具体实现，可以是同步返回或异步轮询，请参考 Swagger 文档中的具体定义)*

---

## 🛠️ 开发常用命令

本项目使用 `uv` 管理开发流程：

- **添加依赖**: `uv add <package_name>`
- **运行测试**: `uv run pytest`
- **代码格式化**: `uv run ruff format .`
- **类型检查**: `uv run mypy builder/`
- **构建 Docker 镜像**:
  ```bash
  docker build -t auto-builder .
  ```

---

## 📂 项目结构

```text
auto-backend/
├── builder/                # 核心源码目录
│   ├── api/                # API 路由控制层
│   ├── models/             # Pydantic 数据模型
│   ├── services/           # 核心业务逻辑 (AI交互, 解析等)
│   ├── storage/            # 任务/文件存储层
│   ├── prompts/            # AI 提示词模版
│   ├── config.py           # 全局配置类
│   └── main.py             # 程序入口
├── tests/                  # 测试用例
├── uploads/                # 上传文件临时存储
├── .env.example            # 环境变量示例
├── pyproject.toml          # 项目与依赖配置
└── README.md               # 项目文档
```

## 🤝 贡献与支持

- 欢迎提交 Issue 和 Pull Request。
- 项目地址: [GitHub - Auto Backend](https://github.com/Protagonistss/auto-backend)

## License

MIT License

---