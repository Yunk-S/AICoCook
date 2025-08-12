"""
RAG检索增强生成API端点
=====================

提供智能问答和菜谱推荐服务。
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
import structlog

from app.services.rag_service import get_rag_service, AdvancedRAGService

logger = structlog.get_logger()
router = APIRouter()


class RAGQueryRequest(BaseModel):
    """RAG查询请求模型"""
    query: str
    max_results: int = 5
    include_search_details: bool = False


class RAGQueryResponse(BaseModel):
    """RAG查询响应模型"""
    answer: str
    results: List[Dict[str, Any]]
    query_expanded: str
    processing_time: float
    total_results: int
    search_context: Optional[str] = None
    timestamp: Optional[str] = None


class SimpleSearchRequest(BaseModel):
    """简单搜索请求模型"""
    query: str
    limit: int = 10


@router.post("/query", response_model=RAGQueryResponse, summary="智能问答")
async def rag_query(
    request: RAGQueryRequest,
    rag_service: AdvancedRAGService = Depends(get_rag_service)
) -> RAGQueryResponse:
    """
    使用RAG技术进行智能问答
    
    - **query**: 用户问题或查询
    - **max_results**: 最大返回的相关菜谱数量
    - **include_search_details**: 是否包含详细的搜索信息
    
    返回AI生成的回答和相关菜谱推荐。
    """
    try:
        logger.info("收到RAG查询请求", query=request.query, max_results=request.max_results)
        
        response_data = await rag_service.generate_rag_response(
            query=request.query,
            max_results=request.max_results,
            include_search_details=request.include_search_details
        )
        
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data["error"])
        
        return RAGQueryResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG查询处理失败: {e}")
        raise HTTPException(status_code=500, detail="查询处理失败")


@router.post("/search", summary="混合搜索")
async def hybrid_search(
    request: SimpleSearchRequest,
    rag_service: AdvancedRAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    使用混合检索技术搜索菜谱
    
    - **query**: 搜索关键词
    - **limit**: 返回结果数量限制
    
    返回相关菜谱列表，按相关性排序。
    """
    try:
        logger.info("收到混合搜索请求", query=request.query, limit=request.limit)
        
        # 先进行查询扩展
        expanded_query = await rag_service.query_expansion(request.query)
        
        # 执行混合检索
        results = await rag_service.hybrid_retrieval(
            query=expanded_query,
            top_k=request.limit
        )
        
        return {
            "results": results,
            "total": len(results),
            "query": request.query,
            "expanded_query": expanded_query
        }
        
    except Exception as e:
        logger.error(f"混合搜索失败: {e}")
        raise HTTPException(status_code=500, detail="搜索失败")


@router.get("/suggest", summary="查询建议")
async def query_suggestions(
    q: str = Query(..., description="查询前缀", min_length=1, max_length=100),
    limit: int = Query(default=5, description="建议数量", ge=1, le=10)
) -> Dict[str, Any]:
    """
    根据输入提供查询建议
    
    - **q**: 查询前缀
    - **limit**: 返回建议数量
    """
    try:
        # 简单的查询建议实现
        # 实际项目中可以基于历史查询、热门搜索等
        common_suggestions = [
            "川菜",
            "家常菜",
            "素食",
            "快手菜",
            "汤品",
            "甜点",
            "早餐",
            "减脂餐",
            "下饭菜",
            "凉菜"
        ]
        
        # 过滤匹配的建议
        suggestions = [s for s in common_suggestions if q.lower() in s.lower()][:limit]
        
        return {
            "suggestions": suggestions,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"获取查询建议失败: {e}")
        raise HTTPException(status_code=500, detail="获取建议失败")


@router.get("/health", summary="RAG服务健康检查")
async def rag_health_check() -> Dict[str, Any]:
    """检查RAG服务状态"""
    try:
        rag_service = get_rag_service()
        
        # 简单的健康检查
        health_status = {
            "status": "healthy",
            "service": "RAG Service",
            "ai_client": "available" if rag_service.ai_client else "unavailable",
            "vector_db": "available" if rag_service.vector_db else "unavailable"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"RAG健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/rebuild-embeddings", summary="重新生成向量嵌入")
async def rebuild_embeddings(
    provider: str = Query(..., description="嵌入服务提供商 (google, openai, doubao, zhipu, deepseek)"),
    batch_size: int = Query(default=100, description="批处理大小", ge=1, le=500)
) -> Dict[str, Any]:
    """
    使用指定的服务提供商重新生成所有食谱的向量嵌入
    
    支持的服务商：
    - google: Google Embedding API
    - openai: OpenAI Embeddings
    - doubao: 字节跳动豆包
    - zhipu: 智谱AI
    - deepseek: DeepSeek
    """
    try:
        from app.services.data_import_service import DataImportService
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # 验证服务商
        supported_providers = settings.get_supported_embedding_providers()
        if provider not in supported_providers:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的服务商: {provider}。支持的服务商: {supported_providers}"
            )
        
        # 检查API密钥
        api_key = settings.get_embedding_api_key(provider)
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail=f"未配置{provider.upper()}的API密钥。请在配置文件中设置相应的API密钥。"
            )
        
        logger.info(f"开始使用{provider.upper()}重新生成向量嵌入")
        
        # 创建数据导入服务
        import_service = DataImportService()
        
        # 执行重建
        result = await import_service.rebuild_embeddings(batch_size=batch_size)
        
        logger.info(f"使用{provider.upper()}完成向量嵌入重建", **result)
        
        return {
            "message": f"成功使用{provider.upper()}重新生成向量嵌入",
            "provider": provider,
            "processed_count": result.get("total_processed", 0),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新生成向量嵌入失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新生成向量嵌入失败: {str(e)}")


@router.get("/providers", summary="获取支持的嵌入服务商")
async def get_embedding_providers() -> Dict[str, Any]:
    """
    获取当前支持的嵌入服务提供商列表
    """
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        providers = []
        for provider in settings.get_supported_embedding_providers():
            api_key = settings.get_embedding_api_key(provider)
            model = settings.get_embedding_model(provider)
            
            providers.append({
                "name": provider,
                "display_name": provider.upper(),
                "model": model,
                "configured": bool(api_key),
                "is_default": provider == settings.EMBEDDING_PROVIDER
            })
        
        return {
            "providers": providers,
            "default_provider": settings.EMBEDDING_PROVIDER,
            "current_model": settings.get_embedding_model(),
        }
        
    except Exception as e:
        logger.error(f"获取嵌入服务商列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取嵌入服务商列表失败")


@router.post("/feedback", summary="用户反馈")
async def submit_feedback(
    query: str,
    answer_quality: int,
    is_helpful: bool,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    收集用户对RAG回答的反馈
    
    用于持续改进RAG系统性能。
    """
    try:
        # 记录反馈信息
        feedback_data = {
            "query": query,
            "answer_quality": answer_quality,
            "is_helpful": is_helpful,
            "comment": comment,
            "timestamp": "2024-01-01T00:00:00Z"  # 实际项目中使用真实时间
        }
        
        logger.info("收到用户反馈", **feedback_data)
        
        # 实际项目中可以将反馈存储到数据库
        # 用于训练和改进模型
        
        return {
            "message": "感谢您的反馈！",
            "feedback_id": "feedback_123"  # 实际项目中生成真实ID
        }
        
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail="提交反馈失败")