"""
Celery 异步任务配置

配置 Celery 用于处理异步任务，如 AI 推理、大数据处理等。
"""

import os
from typing import Any, Dict

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

# 创建 Celery 实例
celery_app = Celery(
    "aire_backend",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.recipe_tasks", 
        "app.tasks.embedding_tasks",
        "app.tasks.maintenance_tasks",
        "app.tasks.data_import_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    # 基础配置
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务路由
    task_routes={
        "app.tasks.ai_tasks.*": {"queue": "ai"},
        "app.tasks.embedding_tasks.*": {"queue": "embedding"},
        "app.tasks.recipe_tasks.*": {"queue": "recipe"},
        "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
        "app.tasks.data_import_tasks.*": {"queue": "data_import"},
    },
    
    # 任务优先级
    task_default_priority=5,
    worker_prefetch_multiplier=1,
    
    # 结果过期时间
    result_expires=3600,  # 1 hour
    
    # 任务超时
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # 重试配置
    task_acks_late=True,
    
    # 定时任务配置
    beat_schedule={
        # 每天凌晨清理过期的嵌入向量
        "cleanup-expired-embeddings": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_embeddings",
            "schedule": crontab(hour=2, minute=0),  # 每天凌晨 2 点
        },
        
        # 每周更新食谱推荐模型
        "update-recommendation-model": {
            "task": "app.tasks.ai_tasks.update_recommendation_model",
            "schedule": crontab(hour=3, minute=0, day_of_week=1),  # 每周一凌晨 3 点
        },
        
        # 每天统计用户活跃度
        "calculate-user-stats": {
            "task": "app.tasks.maintenance_tasks.calculate_user_stats",
            "schedule": crontab(hour=1, minute=30),  # 每天凌晨 1:30
        },
        
        # 每小时检查系统健康状态
        "health-check": {
            "task": "app.tasks.maintenance_tasks.system_health_check",
            "schedule": crontab(minute=0),  # 每小时整点
        },
    },
)

# 配置队列
celery_app.conf.task_routes = {
    # AI 相关任务使用专门的队列
    "app.tasks.ai_tasks.generate_recipe": {"queue": "ai_high"},
    "app.tasks.ai_tasks.generate_meal_plan": {"queue": "ai_high"},
    "app.tasks.ai_tasks.chat_with_assistant": {"queue": "ai_normal"},
    
    # 嵌入任务使用专门的队列
    "app.tasks.embedding_tasks.generate_recipe_embeddings": {"queue": "embedding"},
    "app.tasks.embedding_tasks.update_recipe_embeddings": {"queue": "embedding"},
    
    # 其他任务使用默认队列
    "app.tasks.recipe_tasks.*": {"queue": "default"},
    "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    
    # 数据导入任务使用专门的队列
    "app.tasks.data_import_tasks.import_epicurious_data": {"queue": "data_import_high"},
    "app.tasks.data_import_tasks.rebuild_all_embeddings": {"queue": "data_import_high"},
    "app.tasks.data_import_tasks.generate_missing_embeddings": {"queue": "data_import_normal"},
    "app.tasks.data_import_tasks.cleanup_orphaned_vectors": {"queue": "maintenance"},
}


def create_celery_app() -> Celery:
    """创建并配置 Celery 应用"""
    return celery_app


# 任务装饰器
def task(*args, **kwargs):
    """Celery 任务装饰器"""
    return celery_app.task(*args, **kwargs)


# 工具函数
def get_task_info(task_id: str) -> Dict[str, Any]:
    """获取任务信息"""
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result,
        "traceback": result.traceback,
        "info": result.info,
    }


def revoke_task(task_id: str, terminate: bool = False, signal: str = "SIGTERM") -> bool:
    """撤销任务"""
    try:
        celery_app.control.revoke(task_id, terminate=terminate, signal=signal)
        return True
    except Exception:
        return False


def get_active_tasks() -> Dict[str, Any]:
    """获取活跃任务"""
    inspect = celery_app.control.inspect()
    return {
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "reserved": inspect.reserved(),
    }


def get_worker_stats() -> Dict[str, Any]:
    """获取工作者统计信息"""
    inspect = celery_app.control.inspect()
    return {
        "stats": inspect.stats(),
        "registered": inspect.registered(),
        "ping": inspect.ping(),
    }