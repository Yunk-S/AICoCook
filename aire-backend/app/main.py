"""
FastAPI 应用程序主入口

配置和启动 AI Meal Coach 后端服务。
"""

import logging
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from app.api.api_v1.api import api_router
from app.core.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging
from app.database import init_db

# 获取配置
settings = get_settings()

# 设置日志
setup_logging()
logger = structlog.get_logger()

# Prometheus 指标 - 使用异常处理避免重复注册错误
try:
    REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
except Exception as e:
    # 如果Prometheus指标创建失败（如重复注册），创建空的指标对象
    logger.warning(f"Prometheus metrics already registered, using dummy metrics: {e}")
    
    class DummyMetric:
        def labels(self, **kwargs):
            return self
        def inc(self):
            pass
        def observe(self, value):
            pass
    
    REQUEST_COUNT = DummyMetric()
    REQUEST_DURATION = DummyMetric()


async def auto_import_data_on_startup():
    """应用启动时自动检测和导入数据"""
    from pathlib import Path
    from app.services.data_import_service import DataImportService
    from app.database import SessionLocal
    from app.models.recipe import Recipe
    from app.core.config import get_settings
    
    settings = get_settings()
    
    # 检查是否启用自动导入
    if not settings.AUTO_IMPORT_ON_STARTUP:
        logger.info("自动导入已禁用，跳过数据导入")
        return
    
    logger.info("开始检查是否需要自动导入数据...")
    
    # 检查数据库中是否已有数据
    with SessionLocal() as db:
        recipe_count = db.query(Recipe).count()
        
    if recipe_count > 0:
        logger.info(f"数据库中已有 {recipe_count} 条食谱记录，跳过自动导入")
        return
    
    # 如果没有数据，检查raw目录下的CSV文件
    data_import_service = DataImportService()
    data_dir = Path(data_import_service.data_dir)
    
    if not data_dir.exists():
        logger.info(f"数据目录不存在: {data_dir}")
        return
    
    # 查找CSV文件
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        logger.info("未找到CSV文件，跳过自动导入")
        return
    
    logger.info(f"发现 {len(csv_files)} 个CSV文件，开始自动导入...")
    
    total_imported = 0
    for csv_file in csv_files:
        try:
            logger.info(f"正在导入: {csv_file.name}")
            
            # 如果是标准Epicurious文件，使用专门的导入方法
            if csv_file.name == "epi_r.csv":
                result = await data_import_service.import_epicurious_csv(
                    csv_path=str(csv_file),
                    generate_embeddings=settings.AUTO_GENERATE_EMBEDDINGS,
                    limit=settings.AUTO_IMPORT_LIMIT  # 使用配置文件设置
                )
            else:
                # 使用通用导入方法
                result = await data_import_service.import_file(
                    file_path=csv_file,
                    file_type='csv',
                    generate_embeddings=True
                )
            
            imported_count = result.get("successful_imports", 0)
            total_imported += imported_count
            
            logger.info(f"成功导入 {csv_file.name}: {imported_count} 条记录")
            
        except Exception as e:
            logger.error(f"导入文件 {csv_file.name} 失败", error=str(e))
    
    if total_imported > 0:
        logger.info(f"自动导入完成，共导入 {total_imported} 条食谱记录")
    else:
        logger.warning("自动导入完成，但未成功导入任何记录")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting AI Meal Coach application", version=settings.VERSION)
    
    # 初始化数据库
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # 初始化向量数据库连接
    try:
        from app.core.vector_db import get_vector_db
        vector_db = get_vector_db()
        await vector_db.initialize()
        logger.info("Vector database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize vector database", error=str(e))
        # 向量数据库初始化失败不阻止应用启动
    
    # 自动检测和导入CSV数据
    try:
        await auto_import_data_on_startup()
    except Exception as e:
        logger.warning("Auto import failed during startup", error=str(e))
        # 自动导入失败不阻止应用启动
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down AI Meal Coach application")


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI Meal Coach - 智能膳食助手后端服务",
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 设置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加可信主机中间件
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机名
        )

    # 请求处理中间件
    @app.middleware("http")
    async def process_time_middleware(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client=request.client.host if request.client else None,
        )
        
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 更新 Prometheus 指标
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_DURATION.observe(process_time)
        
        # 记录响应
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
        )
        
        return response

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # 指标端点
    if settings.ENABLE_METRICS:
        @app.get("/metrics")
        async def metrics():
            """Prometheus 指标"""
            return Response(generate_latest(), media_type="text/plain")

    # 包含 API 路由
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 挂载静态文件目录 (已禁用，UI 已统一到主前端)
    # app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

    # 设置异常处理器
    setup_exception_handlers(app)

    return app


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    # 当启用reload时需要使用字符串导入路径
    app_str = "app.main:app" if (settings.RELOAD and settings.is_development) else app
    
    uvicorn.run(
        app_str,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        workers=settings.WORKERS if not settings.RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )