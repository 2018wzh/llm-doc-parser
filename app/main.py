"""
FastAPI应用主文件
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 在导入其他模块之前加载环境变量
import dotenv
dotenv.load_dotenv()

from app.core import settings, AppException
from app.api import router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动事件
    logger.info(f"启动应用: {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"LLM提供商: {settings.LLM_PROVIDER}")
    logger.info(f"环境变量加载完成，DEBUG模式: {settings.DEBUG}")
    yield
    # 关闭事件
    logger.info("应用已关闭")


def create_app() -> FastAPI:
    """
    创建FastAPI应用
    
    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 异常处理中间件
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """应用异常处理"""
        logger.warning(f"应用异常: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.APP_TITLE,
            "version": settings.APP_VERSION,
        }
    
    # 包含API路由
    app.include_router(router)
    
    # 文档
    @app.get("/", tags=["info"])
    async def root():
        """API信息"""
        return {
            "title": settings.APP_TITLE,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "openapi": "/openapi.json",
        }
    
    logger.info("FastAPI应用创建完成")
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
