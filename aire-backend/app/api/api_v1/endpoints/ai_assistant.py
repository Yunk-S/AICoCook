"""
AI 助手 API 端点

提供 AI 驱动的食谱推荐、膳食计划生成等功能。
支持用户在前端动态选择AI服务商 (Google, Openai，DeepSeek等) 并提供密钥。
"""
from typing import Any, Dict, List, Optional
import json
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from fastapi.responses import StreamingResponse
import structlog

from app.schemas.ai import ChatRequest, ChatResponse
from app.core.ai_service import get_ai_service, ChatMessage
from app.core.exceptions import AIServiceException

router = APIRouter()
logger = structlog.get_logger()

# --- 依赖函数 ---
async def get_api_credentials(
    x_api_provider: str = Header("google"),
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, str]:
    """从请求头中提取AI服务商和API密钥。"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"An API key for '{x_api_provider}' is required in the 'X-API-Key' header.",
        )
    return {"provider": x_api_provider, "api_key": x_api_key}


# --- API 端点 ---
@router.post("/chat", response_model=ChatResponse, summary="AI 聊天助手")
async def chat_with_assistant(
    request: ChatRequest,
    creds: Dict[str, str] = Depends(get_api_credentials),
) -> ChatResponse:
    """
    与 AI 助手进行对话。

    用户通过请求头选择服务商并提供密钥:
    - `X-API-Provider`: 'google' or 'deepseek' (默认为 'google')
    - `X-API-Key`: 对应的API密钥
    """
    try:
        # 动态获取AI服务实例
        ai_service = get_ai_service(creds["provider"])
        
        system_prompt = """你是一个专业的 AI 膳食助手，名叫"小食"。你的主要任务是：
1. 帮助用户制定健康的膳食计划。
2. 根据用户的食材推荐食谱。
3. 提供专业的营养建议。
4. 解答与食物、烹饪和健康饮食相关的问题。

请始终以友好、专业、乐于助人的语气回答问题，并尽可能提供清晰、可操作的建议。"""
        
        messages = [ChatMessage(role="system", content=system_prompt)]
        messages.extend([ChatMessage(role=msg.role, content=msg.content) for msg in request.messages])
        
        # 使用提取的密钥进行调用
        response = await ai_service.chat_completion(
            messages=messages,
            api_key=creds["api_key"],
            temperature=request.temperature,
        )
        
        return response
        
    except AIServiceException as e:
        # 捕获我们自定义的AI服务异常，向用户返回清晰的错误信息
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AI Service Error ({creds['provider']}): {e.message}"
        )
    except Exception as e:
        # 捕获所有其他意外错误
        logger.error("Unexpected Chat Error", error=str(e), provider=creds['provider'], exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred. Please try again later."
        )


@router.post("/chat/stream", summary="流式AI聊天对话")
async def stream_chat_with_assistant(
    request: ChatRequest,
    creds: Dict[str, str] = Depends(get_api_credentials),
) -> StreamingResponse:
    """
    流式AI聊天对话 - 解决超时问题
    
    使用Server-Sent Events (SSE)实现文字逐步输出，避免超时问题。
    特别适合DeepSeek等需要长时间思考的模型。
    
    响应格式：
    - type: 'start' | 'chunk' | 'done' | 'error'
    - content: 当前块内容
    - accumulated: 累积内容（可选）
    """
    try:
        ai_service = get_ai_service(creds["provider"])
        
        async def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'content': '', 'provider': creds['provider']}, ensure_ascii=False)}\n\n"
                
                # 检查是否为测试密钥，如果是则返回模拟响应
                if creds["api_key"] == "test":
                    # 模拟响应用于测试
                    test_content = "这是一个流式响应测试。您好！我是AI助手，正在测试流式输出功能。"
                    accumulated = ""
                    
                    # 模拟逐字输出
                    for char in test_content:
                        accumulated += char
                        chunk_data = {
                            "type": "chunk",
                            "content": char,
                            "accumulated": accumulated
                        }
                        yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)  # 模拟打字延迟
                    
                    # 发送完成信号
                    final_data = {
                        "type": "done", 
                        "content": accumulated,
                        "model": "test-model",
                        "usage": {"tokens": len(test_content)}
                    }
                    yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                    return
                
                # 真实AI服务调用
                # 构建完整的聊天消息，包含系统提示词
                system_prompt = """你是一个专业的 AI 膳食助手，名叫"小食"。你的主要任务是：
1. 帮助用户制定健康的膳食计划。
2. 根据用户的食材推荐食谱。
3. 提供专业的营养建议。
4. 解答与食物、烹饪和健康饮食相关的问题。

请始终以友好、专业、乐于助人的语气回答问题，并尽可能提供清晰、可操作的建议。注意内容分段，条理清晰。"""
                
                chat_messages = [ChatMessage(role="system", content=system_prompt)]
                chat_messages.extend([ChatMessage(role=msg.role, content=msg.content) for msg in request.messages])
                
                response = await ai_service.chat_completion(
                    messages=chat_messages,
                    api_key=creds["api_key"],
                    temperature=request.temperature if hasattr(request, 'temperature') else 0.7,
                )
                
                # 模拟逐步输出，提升用户体验
                content = response.content
                accumulated = ""
                
                # 智能分词：优先按句子分割，其次按词分割
                import re
                sentences = re.split(r'([.!?。！？\n])', content)
                
                for i, part in enumerate(sentences):
                    if part.strip():
                        accumulated += part
                        
                        chunk_data = {
                            "type": "chunk",
                            "content": part,
                            "accumulated": accumulated
                        }
                        yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                        
                        # 自适应延迟：句子间稍长，词间较短
                        if part in '.!?。！？':
                            await asyncio.sleep(0.1)  # 句子结束，稍作停顿
                        else:
                            await asyncio.sleep(0.03)  # 词间短暂停顿
                
                # 发送完成信号
                final_data = {
                    "type": "done", 
                    "content": accumulated,
                    "model": getattr(response, 'model', 'unknown'),
                    "usage": getattr(response, 'usage', {})
                }
                yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                
            except AIServiceException as e:
                error_data = {
                    "type": "error",
                    "content": f"AI服务错误 ({creds['provider']}): {str(e)}",
                    "provider": creds['provider']
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error("流式聊天错误", error=str(e), provider=creds['provider'], exc_info=True)
                error_data = {
                    "type": "error",
                    "content": f"意外错误: {str(e)}",
                    "provider": creds['provider']
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                # 🔑 关键流式响应头 - 防止代理缓冲
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用nginx缓冲
                "Transfer-Encoding": "chunked",  # 明确启用分块传输
                "Pragma": "no-cache",
                "Expires": "0",
                # CORS 头
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式聊天服务错误: {str(e)}"
        )


# --- 增强RAG功能端点 ---
@router.post("/rag-search", summary="增强型RAG搜索")
async def enhanced_rag_search(
    query: str,
    max_passages: Optional[int] = Query(20, ge=5, le=50, description="最大检索段落数"),
    use_advanced_features: bool = Query(True, description="是否使用高级RAG功能"),
    creds: Dict[str, str] = Depends(get_api_credentials),
) -> Dict[str, Any]:
    """
    增强型RAG搜索功能
    
    基于最新RAG研究实现的高级搜索，包含：
    - 多查询并行处理
    - 检索重排序
    - 查询优化和分解
    - 注意力引导的上下文剪枝
    """
    try:
        from app.core.ai_service import get_advanced_rag_service, RAGConfig
        
        # 配置RAG服务
        config = RAGConfig(
            max_retrieved_passages=max_passages,
            use_multi_query=use_advanced_features,
            use_query_decomposition=use_advanced_features,
            use_context_pruning=use_advanced_features
        )
        
        rag_service = get_advanced_rag_service(config)
        
        # 模拟文档库（实际应用中应该从数据库获取）
        # 这里使用示例文档，实际实现中应该连接到真实的文档数据库
        sample_documents = [
            {
                "id": "1",
                "content": "人工智能是计算机科学的一个分支，致力于创造能够执行通常需要人类智能的任务的机器。",
                "title": "人工智能概述",
                "source": "AI教科书"
            },
            {
                "id": "2", 
                "content": "机器学习是人工智能的一个子集，它使计算机能够从数据中学习，而无需明确编程。",
                "title": "机器学习基础",
                "source": "ML指南"
            },
            {
                "id": "3",
                "content": "深度学习是机器学习的一个子集，它基于人工神经网络，特别是深层神经网络。",
                "title": "深度学习介绍", 
                "source": "DL手册"
            },
            {
                "id": "4",
                "content": "自然语言处理是人工智能的一个分支，专注于计算机和人类语言之间的交互。",
                "title": "自然语言处理",
                "source": "NLP教程"
            },
            {
                "id": "5",
                "content": "计算机视觉是一个跨学科的科学领域，研究如何使计算机从数字图像或视频中获得高层次的理解。",
                "title": "计算机视觉",
                "source": "CV概论"
            }
        ]
        
        # 执行增强RAG搜索
        result = await rag_service.enhanced_rag_query(
            query=query,
            documents=sample_documents,
            api_key=creds["api_key"],
            provider=creds["provider"],
            max_passages=max_passages
        )
        
        return {
            "status": "success",
            "query": query,
            "answer": result["answer"],
            "sources": result["source_passages"],
            "analysis": result["query_analysis"],
            "performance": result["performance_metrics"],
            "rag_config": {
                "provider": creds["provider"],
                "advanced_features_enabled": use_advanced_features,
                "max_passages": max_passages
            }
        }
        
    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RAG Search Error ({creds['provider']}): {e.message}"
        )
    except Exception as e:
        logger.error("Enhanced RAG search failed", error=str(e), query=query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="增强RAG搜索失败，请稍后重试"
        )


@router.post("/recipe-recommendation", summary="智能食谱推荐")
async def smart_recipe_recommendation(
    query: str = Query(..., description="食谱需求描述"),
    dietary_restrictions: Optional[List[str]] = Query(None, description="饮食限制"),
    cuisine_preference: Optional[str] = Query(None, description="菜系偏好"),
    max_results: int = Query(5, ge=1, le=20, description="最大推荐数量"),
    creds: Dict[str, str] = Depends(get_api_credentials),
) -> Dict[str, Any]:
    """
    基于AI的智能食谱推荐
    
    结合用户需求、饮食限制和偏好，提供个性化食谱推荐。
    """
    try:
        # 构建智能推荐查询
        recommendation_query = f"推荐食谱：{query}"
        
        if dietary_restrictions:
            recommendation_query += f"，饮食限制：{', '.join(dietary_restrictions)}"
        
        if cuisine_preference:
            recommendation_query += f"，偏好菜系：{cuisine_preference}"
        
        # 使用AI服务生成推荐
        ai_service = get_ai_service(creds["provider"])
        
        system_prompt = """你是一个专业的营养师和厨师，擅长根据用户需求推荐健康美味的食谱。

请根据用户的需求，推荐合适的食谱。每个推荐应包含：
1. 食谱名称
2. 主要食材
3. 制作难度（简单/中等/困难）
4. 预计制作时间
5. 营养特点
6. 制作要点

请以JSON格式返回推荐结果：
{
    "recommendations": [
        {
            "name": "食谱名称",
            "ingredients": ["食材1", "食材2"],
            "difficulty": "简单",
            "cook_time": "30分钟",
            "nutrition": "营养特点",
            "tips": "制作要点"
        }
    ],
    "reasoning": "推荐理由"
}"""

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=recommendation_query)
        ]
        
        response = await ai_service.chat_completion(
            messages=messages,
            api_key=creds["api_key"],
            temperature=0.7
        )
        
        try:
            import json
            result = json.loads(response.content)
            recommendations = result.get("recommendations", [])
            reasoning = result.get("reasoning", "基于您的需求生成的推荐")
        except:
            # 如果解析失败，返回原始回答
            recommendations = []
            reasoning = response.content
        
        return {
            "status": "success",
            "query": query,
            "recommendations": recommendations[:max_results],
            "reasoning": reasoning,
            "filters_applied": {
                "dietary_restrictions": dietary_restrictions,
                "cuisine_preference": cuisine_preference,
                "max_results": max_results
            }
        }
        
    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe Recommendation Error ({creds['provider']}): {e.message}"
        )
    except Exception as e:
        logger.error("Recipe recommendation failed", error=str(e), query=query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="智能食谱推荐失败，请稍后重试"
        )


# 注意：为了保持示例简洁，其他需要调用AI的端点（如智能搜索）暂未实现动态切换。
# 实现方式与/chat端点类似，即通过依赖注入获取provider和api_key，然后传递给AI服务。
