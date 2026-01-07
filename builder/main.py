import asyncio
import logging
import platform
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api import upload, conversations, orm, xml, build

# Windows 上设置 ProactorEventLoop 以支持 subprocess
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("🚀 Auto-Builder Python 启动")
    logger.info(f"📦 AI Provider: {settings.ai_provider}")
    logger.info(f"🧠 Model: {settings.ai_model}")

    # 确保上传目录存在
    import os
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info(f"📁 上传目录: {settings.upload_dir}")

    yield
    # 关闭时清理
    logger.info("👋 Auto-Builder Python 关闭")


app = FastAPI(
    title="Auto-Builder API",
    description="AI 驱动的代码生成和对话系统",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(upload.router, tags=["任务管理"])
app.include_router(conversations.router, tags=["对话管理"])
app.include_router(orm.router, tags=["ORM管理"])
app.include_router(xml.router, prefix="/xml", tags=["XML管理"])
app.include_router(build.router, prefix="/build", tags=["构建管理"])


@app.get("/", summary="服务信息", tags=["系统"])
async def root():
    """获取 API 服务信息"""
    return {"message": "Auto-Builder API is running", "version": "2.0.0"}


@app.get("/health", summary="健康检查", tags=["系统"])
async def health():
    """检查服务健康状态"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "builder.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
