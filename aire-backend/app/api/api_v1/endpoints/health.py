"""
健康检查 API 端点

提供系统健康状态检查功能。
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db

settings = get_settings()
router = APIRouter()


@router.get("/", summary="基础健康检查")
async def health_check() -> Dict[str, Any]:
    """
    基础健康检查端点
    
    返回服务的基本状态信息。
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/detailed", summary="详细健康检查")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    详细健康检查端点
    
    检查数据库连接、AI 服务状态等。
    """
    health_status = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # 检查数据库连接
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # 检查 AI 服务状态
    try:
        from app.core.ai_service import get_ai_service_instance
        ai_service = get_ai_service_instance()
        health_status["checks"]["ai_service"] = {
            "status": "healthy",
            "message": "AI service available"
        }
    except Exception as e:
        health_status["checks"]["ai_service"] = {
            "status": "warning",
            "message": f"AI service issue: {str(e)}"
        }
    
    # 检查向量数据库状态
    try:
        from app.core.vector_db import get_vector_db_instance
        vector_db = await get_vector_db_instance()
        vector_count = await vector_db.get_vector_count()
        health_status["checks"]["vector_db"] = {
            "status": "healthy",
            "message": f"Vector database available with {vector_count} vectors"
        }
    except Exception as e:
        health_status["checks"]["vector_db"] = {
            "status": "warning",
            "message": f"Vector database issue: {str(e)}"
        }
    
    return health_status


@router.get("/metrics", summary="系统指标")
async def system_metrics() -> Dict[str, Any]:
    """
    系统指标端点
    
    返回系统运行指标。
    """
    import psutil
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
    }