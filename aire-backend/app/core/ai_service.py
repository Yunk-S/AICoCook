"""
AI 服务集成模块

提供与各种 AI 服务的动态集成，包括 Google Gemini 和 DeepSeek。
支持用户在前端选择服务商并提供自己的API密钥。
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import numpy as np
import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.exceptions import AIServiceException

logger = structlog.get_logger()

# --- 通用数据模型 ---
class EmbeddingResult(BaseModel):
    embedding: List[float]
    model: str
    dimensions: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None

# --- 服务接口 ---
class AIServiceInterface(ABC):
    @abstractmethod
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = None, temperature: float = 0.7) -> ChatResponse:
        pass

# --- Google Gemini 实现 ---
class GoogleGeminiService(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "gemini-1.5-flash", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("Google API key is required.")
        try:
            genai.configure(api_key=api_key)
            chat_model = genai.GenerativeModel(model)
            
            history = self._format_history(messages)

            response = await asyncio.to_thread(
                chat_model.generate_content,
                history,
                generation_config={"temperature": temperature}
            )
            return ChatResponse(
                content=response.text,
                model=model,
                usage=self._extract_usage(response)
            )
        except Exception as e:
            logger.error("Google AI Error", error=str(e))
            # 尝试解析更具体的错误信息
            if "API key not valid" in str(e):
                raise AIServiceException("Your Google API key is not valid. Please check and try again.")
            raise AIServiceException(f"Google AI API Error: {e}")

    def _format_history(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        history = []
        system_prompt = ""
        for msg in messages:
            if msg.role == 'system':
                system_prompt += msg.content + "\n\n"
                continue
            
            if system_prompt and msg.role == 'user' and not any(h['role'] == 'user' for h in history):
                content = system_prompt + msg.content
                system_prompt = "" 
            else:
                content = msg.content

            role = "model" if msg.role == "assistant" else "user"
            
            if history and history[-1]["role"] == role:
                history[-1]["parts"].append(content)
            else:
                history.append({"role": role, "parts": [content]})
        return history
        
    def _extract_usage(self, response) -> Dict[str, int]:
        if hasattr(response, 'usage_metadata'):
            return {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
            }
        return {}

# --- OpenAI 实现 ---
class OpenAIService(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "gpt-3.5-turbo", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("OpenAI API key is required.")
        try:
            client = AsyncOpenAI(api_key=api_key)
            
            chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = await client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=temperature,
            )
            return ChatResponse(
                content=response.choices[0].message.content,
                model=model,
                usage=response.usage.model_dump() if response.usage else {}
            )
        except Exception as e:
            logger.error("OpenAI Error", error=str(e))
            if "Incorrect API key" in str(e) or "Invalid API" in str(e):
                raise AIServiceException("Your OpenAI API key is incorrect. Please check and try again.")
            raise AIServiceException(f"OpenAI API Error: {e}")

# --- 豆包 (ByteDance) AI 实现 ---
class DouBaoService(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "doubao-pro-32k", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("DouBao API key is required.")
        try:
            # 豆包使用OpenAI兼容接口
            client = AsyncOpenAI(
                api_key=api_key, 
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            
            chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = await client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=temperature,
            )
            return ChatResponse(
                content=response.choices[0].message.content,
                model=model,
                usage=response.usage.model_dump() if response.usage else {}
            )
        except Exception as e:
            logger.error("DouBao AI Error", error=str(e))
            if "Incorrect API key" in str(e) or "Invalid API" in str(e):
                raise AIServiceException("Your DouBao API key is incorrect. Please check and try again.")
            raise AIServiceException(f"DouBao AI API Error: {e}")

# --- 智谱 (ZhiPu) AI 实现 ---
class ZhiPuService(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "glm-4", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("ZhiPu API key is required.")
        try:
            # 智谱使用OpenAI兼容接口
            client = AsyncOpenAI(
                api_key=api_key, 
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
            
            chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = await client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=temperature,
            )
            return ChatResponse(
                content=response.choices[0].message.content,
                model=model,
                usage=response.usage.model_dump() if response.usage else {}
            )
        except Exception as e:
            logger.error("ZhiPu AI Error", error=str(e))
            if "Incorrect API key" in str(e) or "Invalid API" in str(e):
                raise AIServiceException("Your ZhiPu API key is incorrect. Please check and try again.")
            raise AIServiceException(f"ZhiPu AI API Error: {e}")

# --- DeepSeek AI 实现 ---
class DeepSeekService(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "deepseek-chat", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("DeepSeek API key is required.")
        
        # 重试配置 - 根据DeepSeek社区反馈优化
        max_retries = 5  # 增加重试次数
        retry_delay = 3  # 增加初始延迟
        
        for attempt in range(max_retries):
            try:
                # DeepSeek的API与OpenAI兼容
                client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
                
                chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

                response = await client.chat.completions.create(
                    model=model,
                    messages=chat_messages,
                    temperature=temperature,
                    timeout=120.0  # 增加到120秒超时，适应DeepSeek服务器繁忙情况
                )
                return ChatResponse(
                    content=response.choices[0].message.content,
                    model=model,
                    usage=response.usage.model_dump() if response.usage else {}
                )
            except Exception as e:
                logger.error(f"DeepSeek AI Error (attempt {attempt + 1})", error=str(e))
                
                # 特殊错误处理
                error_str = str(e).lower()
                if "incorrect api key" in error_str:
                    raise AIServiceException("DeepSeek API密钥错误，请检查您的API密钥配置。")
                elif "server busy" in error_str or "rate limit" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        logger.info(f"DeepSeek服务繁忙，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        raise AIServiceException("DeepSeek服务当前繁忙，请稍后重试。建议：\n1. 检查API额度是否充足\n2. 稍后再试，高峰期服务可能繁忙\n3. 可以切换到其他AI服务提供商")
                elif "timeout" in error_str:
                    if attempt < max_retries - 1:
                        logger.info(f"DeepSeek请求超时，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise AIServiceException("DeepSeek服务响应超时，请检查网络连接或稍后重试。")
                elif "network" in error_str or "connection" in error_str:
                    raise AIServiceException("网络连接错误，请检查网络设置。")
                else:
                    # 对于其他错误，不重试
                    raise AIServiceException(f"DeepSeek AI服务错误: {str(e)}")
        
        # 不应该到达这里
        raise AIServiceException("DeepSeek服务调用失败，已达到最大重试次数。")

# --- DeepSeek R1 推理模型实现 ---
class DeepSeekR1Service(AIServiceInterface):
    async def chat_completion(self, messages: List[ChatMessage], api_key: str, model: Optional[str] = "deepseek-r1", temperature: float = 0.7) -> ChatResponse:
        if not api_key:
            raise AIServiceException("DeepSeek API key is required.")
        
        # 重试配置（R1模型可能需要更长时间）
        max_retries = 5  # 增加重试次数
        retry_delay = 5  # 增加初始延迟，R1模型需要更多推理时间
        
        for attempt in range(max_retries):
            try:
                # DeepSeek R1使用相同的API接口，但模型名称不同
                client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
                
                chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

                response = await client.chat.completions.create(
                    model=model,
                    messages=chat_messages,
                    temperature=temperature,
                    timeout=180.0  # R1模型需要更长的推理时间，根据社区反馈增加到3分钟
                )
                return ChatResponse(
                    content=response.choices[0].message.content,
                    model=model,
                    usage=response.usage.model_dump() if response.usage else {}
                )
            except Exception as e:
                logger.error(f"DeepSeek R1 Error (attempt {attempt + 1})", error=str(e))
                
                # 特殊错误处理
                error_str = str(e).lower()
                if "incorrect api key" in error_str:
                    raise AIServiceException("DeepSeek API密钥错误，请检查您的API密钥配置。")
                elif "server busy" in error_str or "rate limit" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        logger.info(f"DeepSeek R1服务繁忙，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        raise AIServiceException("DeepSeek R1服务当前繁忙，请稍后重试。建议：\n1. 检查API额度是否充足\n2. R1模型推理需要更多资源，高峰期可能繁忙\n3. 可以切换到DeepSeek普通模型或其他AI服务")
                elif "timeout" in error_str:
                    if attempt < max_retries - 1:
                        logger.info(f"DeepSeek R1推理超时，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise AIServiceException("DeepSeek R1推理超时，R1模型需要更长的思考时间，请稍后重试。")
                elif "network" in error_str or "connection" in error_str:
                    raise AIServiceException("网络连接错误，请检查网络设置。")
                else:
                    # 对于其他错误，不重试
                    raise AIServiceException(f"DeepSeek R1服务错误: {str(e)}")
        
        # 不应该到达这里
        raise AIServiceException("DeepSeek R1服务调用失败，已达到最大重试次数。")

# --- 服务工厂 ---
_service_instances: Dict[str, AIServiceInterface] = {
    "google": GoogleGeminiService(),
    "openai": OpenAIService(),
    "doubao": DouBaoService(),
    "zhipu": ZhiPuService(),
    "deepseek": DeepSeekService(),
    "deepseek-r1": DeepSeekR1Service(),
}

def get_ai_service(provider: str) -> AIServiceInterface:
    """
    根据提供商名称获取对应的AI服务实例。
    """
    provider = provider.lower()
    service = _service_instances.get(provider)
    if not service:
        raise AIServiceException(f"Unsupported AI provider: '{provider}'. Supported providers are: {list(_service_instances.keys())}")
    return service


# --- 向量嵌入功能 ---
async def generate_embeddings_batch(
    texts: List[str], 
    api_key: str,
    provider: str = "google",
    model: str = "models/embedding-001"
) -> List[List[float]]:
    """
    批量生成文本嵌入向量
    
    Args:
        texts: 要生成嵌入的文本列表
        api_key: API密钥
        provider: 服务提供商 (google, openai, doubao, zhipu, deepseek)
        model: 嵌入模型名称
    
    Returns:
        嵌入向量列表
    """
    try:
        provider_lower = provider.lower()
        
        if provider_lower == "google":
            return await _generate_google_embeddings(texts, api_key, model)
        elif provider_lower == "openai":
            return await _generate_openai_embeddings(texts, api_key, model)
        elif provider_lower == "zhipu":
            return await _generate_openai_compatible_embeddings(
                texts, api_key, model, "https://open.bigmodel.cn/api/paas/v4/"
            )
        else:
            raise AIServiceException(f"Unsupported embedding provider: {provider}")
    except Exception as e:
        logger.error("Embedding generation failed", error=str(e), provider=provider)
        raise AIServiceException(f"Failed to generate embeddings: {str(e)}")


async def _generate_google_embeddings(
    texts: List[str], 
    api_key: str, 
    model: str = "models/embedding-001"
) -> List[List[float]]:
    """使用Google生成嵌入向量"""
    if not api_key:
        raise AIServiceException("Google API key is required for embeddings.")
    
    try:
        genai.configure(api_key=api_key)
        
        embeddings = []
        batch_size = 100  # Google API batch limit
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 使用异步处理
            batch_embeddings = await asyncio.to_thread(
                _generate_google_batch_embeddings, batch, model
            )
            embeddings.extend(batch_embeddings)
            
            # 添加延迟以避免API限制
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        return embeddings
    except Exception as e:
        logger.error("Google embeddings generation failed", error=str(e))
        raise AIServiceException(f"Google embeddings error: {str(e)}")


def _generate_google_batch_embeddings(texts: List[str], model: str) -> List[List[float]]:
    """Google批量嵌入生成的同步函数"""
    embeddings = []
    for text in texts:
        if not text.strip():
            # 空文本使用零向量
            embeddings.append([0.0] * 768)
            continue
            
        try:
            result = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        except Exception as e:
            logger.warning("Failed to generate embedding for text", error=str(e))
            # 失败时使用零向量
            embeddings.append([0.0] * 768)
    
    return embeddings


async def _generate_openai_embeddings(
    texts: List[str], 
    api_key: str, 
    model: str = "text-embedding-ada-002"
) -> List[List[float]]:
    """使用OpenAI生成嵌入向量"""
    if not api_key:
        raise AIServiceException("OpenAI API key is required for embeddings.")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        # 清理文本
        clean_texts = [text.replace("\n", " ").strip() for text in texts]
        
        response = await client.embeddings.create(
            input=clean_texts,
            model=model
        )
        
        embeddings = [item.embedding for item in response.data]
        return embeddings
        
    except Exception as e:
        logger.error("OpenAI embeddings generation failed", error=str(e))
        raise AIServiceException(f"OpenAI embeddings error: {str(e)}")


async def _generate_openai_compatible_embeddings(
    texts: List[str], 
    api_key: str, 
    model: str,
    base_url: str
) -> List[List[float]]:
    """使用OpenAI兼容API生成嵌入向量（支持豆包、智谱、DeepSeek）"""
    if not api_key:
        raise AIServiceException(f"API key is required for embeddings with base URL: {base_url}")
    
    try:
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        # 清理文本
        clean_texts = [text.replace("\n", " ").strip() for text in texts]
        
        response = await client.embeddings.create(
            input=clean_texts,
            model=model
        )
        
        embeddings = [item.embedding for item in response.data]
        return embeddings
        
    except Exception as e:
        logger.error("OpenAI-compatible embeddings generation failed", 
                    error=str(e), base_url=base_url)
        raise AIServiceException(f"OpenAI-compatible embeddings error: {str(e)}")


# --- 嵌入相似度计算 ---
def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    计算两个嵌入向量的余弦相似度
    
    Args:
        embedding1: 第一个向量
        embedding2: 第二个向量
    
    Returns:
        相似度分数 (0-1)
    """
    try:
        # 转换为numpy数组
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # 确保结果在0-1范围内
        return max(0.0, min(1.0, (similarity + 1) / 2))
        
    except Exception as e:
        logger.error("Similarity calculation failed", error=str(e))
        return 0.0


# --- 智能搜索功能 ---
async def semantic_search(
    query: str,
    documents: List[Dict[str, Any]],
    api_key: str,
    provider: str = "google",
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    优化的语义搜索功能
    
    Args:
        query: 搜索查询
        documents: 文档列表，每个文档需包含'content'和'embedding'字段
        api_key: API密钥
        provider: 服务提供商
        top_k: 返回最相关的文档数量
    
    Returns:
        按相关性排序的文档列表
    """
    try:
        import time
        start_time = time.time()
        
        # 生成查询的嵌入向量
        query_embeddings = await generate_embeddings_batch([query], api_key, provider)
        query_embedding = query_embeddings[0]
        
        # 优化：过滤掉没有嵌入向量的文档
        valid_documents = [(i, doc) for i, doc in enumerate(documents) 
                          if 'embedding' in doc and doc['embedding']]
        
        # 如果文档数量很大，考虑分批处理
        if len(valid_documents) > 1000:
            logger.info(f"Large document set detected: {len(valid_documents)} documents")
        
        # 计算与所有文档的相似度
        similarities = []
        threshold = 0.1  # 相似度阈值，低于此值的结果将被过滤
        
        for i, doc in valid_documents:
            similarity = calculate_similarity(query_embedding, doc['embedding'])
            # 只保留相似度高于阈值的结果
            if similarity >= threshold:
                similarities.append((i, similarity, doc))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k个结果
        results = []
        for i, similarity, doc in similarities[:top_k]:
            result_doc = doc.copy()
            result_doc['similarity_score'] = similarity
            results.append(result_doc)
        
        processing_time = time.time() - start_time
        logger.info(f"Semantic search completed", 
                   query_length=len(query),
                   total_docs=len(documents),
                   valid_docs=len(valid_documents),
                   filtered_results=len(similarities),
                   final_results=len(results),
                   processing_time=f"{processing_time:.3f}s")
        
        return results
        
    except Exception as e:
        logger.error("Semantic search failed", error=str(e), query=query)
        raise AIServiceException(f"Semantic search error: {str(e)}")


# === 高级RAG系统 ===
# 基于最新研究实现的增强型RAG系统

from dataclasses import dataclass

@dataclass
class RAGConfig:
    """RAG配置 - 优化性能"""
    max_retrieved_passages: int = 15  # 减少检索数量提高速度
    min_retrieved_passages: int = 3
    similarity_threshold: float = 0.5  # 降低阈值以获得更多结果
    rerank_top_k: int = 8
    use_multi_query: bool = False  # 默认关闭多查询以提高速度
    use_query_decomposition: bool = False  # 默认关闭查询分解以提高速度
    use_context_pruning: bool = False  # 默认关闭上下文剪枝以提高速度
    compression_ratio: float = 0.5  # 增加压缩比率


class AdvancedRAGProcessor:
    """增强型RAG处理器 - 集成在AI服务中"""
    
    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        
    async def enhanced_rag_query(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        api_key: str,
        provider: str = "google",
        max_passages: Optional[int] = None,
        fast_mode: bool = False
    ) -> Dict[str, Any]:
        """
        增强型RAG查询处理
        
        集成多查询并行、重排序、上下文剪枝等最新技术
        支持快速模式以提高响应速度
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # 快速模式：直接进行简单的语义搜索
            if fast_mode:
                logger.info("Using fast mode for RAG query")
                simple_results = await semantic_search(
                    query=query,
                    documents=documents,
                    api_key=api_key,
                    provider=provider,
                    top_k=max_passages or self.config.min_retrieved_passages
                )
                
                # 生成简单回答
                if simple_results:
                    context = "\n\n".join([doc.get('content', '') for doc in simple_results[:3]])
                    simple_answer = await self._generate_simple_answer(
                        query, context, api_key, provider
                    )
                else:
                    simple_answer = "抱歉，没有找到相关信息。"
                
                processing_time = asyncio.get_event_loop().time() - start_time
                return {
                    "answer": simple_answer,
                    "passages": simple_results,
                    "metadata": {
                        "total_passages": len(simple_results),
                        "processing_time": processing_time,
                        "mode": "fast"
                    }
                }
            
            # 1. 查询优化和分解 (RQ-RAG)
            optimized_queries = await self._refine_and_decompose_query(
                query, api_key, provider
            )
            
            # 2. 多查询并行检索 (RAG-R1)
            retrieval_results = await self._parallel_multi_query_retrieval(
                optimized_queries, documents, api_key, provider
            )
            
            # 3. 混合检索结果融合
            fused_results = await self._fuse_retrieval_results(retrieval_results)
            
            # 4. 检索重排序
            reranked_passages = await self._rerank_passages(
                query, fused_results, api_key, provider
            )
            
            # 5. 注意力引导的上下文剪枝
            if self.config.use_context_pruning:
                pruned_passages = await self._attention_guided_pruning(
                    query, reranked_passages, api_key, provider
                )
            else:
                pruned_passages = reranked_passages
            
            # 6. 生成最终回答
            final_answer = await self._generate_enhanced_answer(
                query, pruned_passages, api_key, provider
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "answer": final_answer,
                "source_passages": pruned_passages[:5],
                "query_analysis": {
                    "original_query": query,
                    "optimized_queries": optimized_queries,
                    "total_passages_retrieved": len(fused_results),
                    "passages_after_pruning": len(pruned_passages)
                },
                "performance_metrics": {
                    "processing_time": processing_time,
                    "compression_ratio": len(pruned_passages) / len(fused_results) if fused_results else 0
                }
            }
            
        except Exception as e:
            logger.error("Enhanced RAG query failed", error=str(e))
            raise AIServiceException(f"Enhanced RAG processing failed: {str(e)}")
    
    async def _refine_and_decompose_query(
        self, 
        query: str, 
        api_key: str, 
        provider: str
    ) -> List[str]:
        """查询优化和分解 (基于RQ-RAG)"""
        if not self.config.use_query_decomposition:
            return [query]
            
        try:
            ai_service = get_ai_service(provider)
            
            system_prompt = """你是一个查询优化专家。分析用户查询并生成2-4个优化的检索查询。

返回JSON格式：{"queries": ["查询1", "查询2", "查询3"]}"""

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=f"优化查询：{query}")
            ]
            
            response = await ai_service.chat_completion(
                messages=messages,
                api_key=api_key,
                temperature=0.3
            )
            
            try:
                import json
                result = json.loads(response.content)
                optimized_queries = result.get("queries", [query])
            except:
                optimized_queries = [query]
            
            if query not in optimized_queries:
                optimized_queries.insert(0, query)
                
            return optimized_queries[:4]
            
        except Exception as e:
            logger.warning("Query refinement failed", error=str(e))
            return [query]
    
    async def _parallel_multi_query_retrieval(
        self,
        queries: List[str],
        documents: List[Dict[str, Any]],
        api_key: str,
        provider: str
    ) -> List[Dict[str, Any]]:
        """多查询并行检索"""
        if not self.config.use_multi_query:
            # 单查询模式
            results = await semantic_search(
                query=queries[0],
                documents=documents,
                api_key=api_key,
                provider=provider,
                top_k=self.config.max_retrieved_passages
            )
            return [{"passages": results, "query": queries[0]}]
        
        async def single_query_retrieval(query: str):
            results = await semantic_search(
                query=query,
                documents=documents,
                api_key=api_key,
                provider=provider,
                top_k=self.config.max_retrieved_passages
            )
            return {"passages": results, "query": query}
        
        # 并行执行所有查询
        tasks = [single_query_retrieval(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = [r for r in results if isinstance(r, dict)]
        
        logger.info(
            "Multi-query retrieval completed",
            total_queries=len(queries),
            successful_queries=len(valid_results)
        )
        
        return valid_results
    
    async def _fuse_retrieval_results(
        self, 
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """融合多个检索结果"""
        if not results:
            return []
        
        seen_passages = set()
        fused_passages = []
        
        for result in results:
            for passage in result["passages"]:
                content_hash = hash(passage.get('content', ''))
                
                if content_hash not in seen_passages:
                    seen_passages.add(content_hash)
                    enhanced_passage = passage.copy()
                    enhanced_passage['source_query'] = result["query"]
                    fused_passages.append(enhanced_passage)
        
        # 按相似度分数排序
        fused_passages.sort(key=lambda x: x.get('similarity_score', 0.0), reverse=True)
        
        return fused_passages[:self.config.max_retrieved_passages]
    
    async def _rerank_passages(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        api_key: str,
        provider: str
    ) -> List[Dict[str, Any]]:
        """检索重排序"""
        if len(passages) <= self.config.rerank_top_k:
            return passages
        
        try:
            ai_service = get_ai_service(provider)
            
            # 简化的重排序：使用AI对前N个段落进行评分
            top_passages = passages[:self.config.rerank_top_k]
            
            passages_text = "\n".join([
                f"段落{i+1}: {p.get('content', '')[:200]}..."
                for i, p in enumerate(top_passages)
            ])
            
            rerank_prompt = f"""评估以下段落与查询的相关性（0-10分）。
查询："{query}"

{passages_text}

返回JSON格式：{{"scores": [分数1, 分数2, ...]}}"""

            messages = [ChatMessage(role="user", content=rerank_prompt)]
            
            response = await ai_service.chat_completion(
                messages=messages,
                api_key=api_key,
                temperature=0.1
            )
            
            try:
                import json
                scores_data = json.loads(response.content)
                scores = scores_data.get("scores", [])
                
                # 更新段落分数
                for i, passage in enumerate(top_passages):
                    if i < len(scores):
                        passage['rerank_score'] = scores[i] / 10.0
                    else:
                        passage['rerank_score'] = passage.get('similarity_score', 0.0)
                
                # 排序
                top_passages.sort(key=lambda x: x.get('rerank_score', 0.0), reverse=True)
                
                # 合并剩余段落
                return top_passages + passages[self.config.rerank_top_k:]
                
            except:
                return passages
                
        except Exception as e:
            logger.warning("Passage reranking failed", error=str(e))
            return passages
    
    async def _attention_guided_pruning(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        api_key: str,
        provider: str
    ) -> List[Dict[str, Any]]:
        """注意力引导的上下文剪枝"""
        target_count = max(
            self.config.min_retrieved_passages,
            int(len(passages) * self.config.compression_ratio)
        )
        
        if len(passages) <= target_count:
            return passages
        
        try:
            # 计算查询-段落注意力分数
            query_embeddings = await generate_embeddings_batch(
                [query], api_key, provider
            )
            query_embedding = query_embeddings[0]
            
            attention_scores = []
            for passage in passages:
                if 'embedding' in passage and passage['embedding']:
                    score = calculate_similarity(query_embedding, passage['embedding'])
                else:
                    # 动态生成嵌入
                    content = passage.get('content', '')
                    if content:
                        embeddings = await generate_embeddings_batch([content], api_key, provider)
                        score = calculate_similarity(query_embedding, embeddings[0])
                    else:
                        score = 0.0
                attention_scores.append(score)
            
            # 根据注意力分数选择段落
            scored_passages = list(zip(passages, attention_scores))
            scored_passages.sort(key=lambda x: x[1], reverse=True)
            
            selected_passages = [p for p, _ in scored_passages[:target_count]]
            
            logger.info(
                "Context pruning completed",
                original_count=len(passages),
                pruned_count=len(selected_passages)
            )
            
            return selected_passages
            
        except Exception as e:
            logger.warning("Context pruning failed", error=str(e))
            return passages[:target_count]
    
    async def _generate_enhanced_answer(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        api_key: str,
        provider: str
    ) -> str:
        """生成增强的回答"""
        try:
            ai_service = get_ai_service(provider)
            
            # 构建上下文
            context = ""
            for i, passage in enumerate(passages[:10]):
                content = passage.get('content', '')
                context += f"段落{i+1}: {content}\n\n"
            
            system_prompt = """你是一个专业的AI助手，基于提供的上下文回答问题。

原则：
1. 仔细阅读所有段落
2. 生成准确、全面的回答
3. 引用相关段落
4. 保持逻辑性和结构性"""

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(
                    role="user", 
                    content=f"上下文：\n{context}\n\n问题：{query}\n\n请回答："
                )
            ]
            
            response = await ai_service.chat_completion(
                messages=messages,
                api_key=api_key,
                temperature=0.7
            )
            
            return response.content
            
        except Exception as e:
            logger.error("Enhanced answer generation failed", error=str(e))
            return "抱歉，生成回答时遇到了问题。请稍后重试。"

    async def _generate_simple_answer(
        self,
        query: str,
        context: str,
        api_key: str,
        provider: str
    ) -> str:
        """生成简单回答（快速模式）"""
        try:
            prompt = f"""基于以下上下文回答问题，保持简洁准确：

上下文：
{context}

问题：{query}

回答："""
            
            # 使用AI服务生成回答
            ai_service = get_ai_service(provider)
            response = await ai_service.chat([
                {"role": "user", "content": prompt}
            ], api_key=api_key)
            
            return response.get('content', '抱歉，无法生成回答。')
            
        except Exception as e:
            logger.error("Simple answer generation failed", error=str(e))
            return "抱歉，回答生成失败。"


# 全局高级RAG实例
_advanced_rag_processor = None

def get_advanced_rag_service(config: RAGConfig = None) -> AdvancedRAGProcessor:
    """获取高级RAG服务实例"""
    global _advanced_rag_processor
    if _advanced_rag_processor is None:
        _advanced_rag_processor = AdvancedRAGProcessor(config)
    return _advanced_rag_processor
