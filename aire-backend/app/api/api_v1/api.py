"""
API v1 路由配置

组织和配置所有的 API v1 端点。
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    recipes,
    # TODO: Create meal_plans and diet_profiles modules
    # meal_plans,
    # diet_profiles,
    ai_assistant,
    health,
    data_management,
    rag,
)

# 创建 API v1 路由器
api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["健康检查"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证授权"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"]
)

api_router.include_router(
    recipes.router,
    prefix="/recipes",
    tags=["食谱管理"]
)

api_router.include_router(
    ai_assistant.router,
    prefix="/ai",
    tags=["AI 助手"]
)

api_router.include_router(
    data_management.router,
    prefix="/data",
    tags=["数据管理"]
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["智能问答 (RAG)"]
)