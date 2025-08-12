"""
现代化RAG检索增强生成服务
=========================

基于最新RAG技术实现的智能问答系统，支持：
1. 高级查询扩展和重写
2. 混合检索（向量+关键词）
3. 智能重排序
4. 上下文感知生成
"""

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import numpy as np
import structlog
from sqlalchemy.orm import Session

from app.core.ai_service import generate_embeddings_batch
from app.core.config import get_settings
from app.core.vector_db import get_vector_db_instance
from app.database import SessionLocal
from app.models.recipe import Recipe

logger = structlog.get_logger()
settings = get_settings()


class AdvancedRAGService:
    """现代化RAG服务类"""
    
    def __init__(self):
        self.vector_db = None
        self.settings = settings
        
    async def _ensure_initialized(self):
        """确保服务已初始化"""
        if self.vector_db is None:
            self.vector_db = await get_vector_db_instance()
        
    async def query_expansion(self, original_query: str) -> str:
        """
        查询扩展：通过LLM生成潜在答案来扩展原始查询
        基于RAG最佳实践的查询扩展技术
        """
        try:
            expansion_prompt = f"""你是一个专业的菜谱搜索助手。对于给定的查询，生成一个简洁但详细的回答，这个回答将用于扩展原始查询以提高搜索准确性。

原始查询: {original_query}

请生成一个1-2句话的专业回答，包含可能的相关关键词和概念："""

            messages = [
                {"role": "system", "content": "你是专业的菜谱搜索助手，专注于生成有用的查询扩展内容。"},
                {"role": "user", "content": expansion_prompt}
            ]
            
            from app.core.ai_service import get_ai_service
            
            # 使用配置的嵌入服务商进行查询扩展（优先使用Google，因为它更适合文本理解）
            provider = "google" if self.settings.get_embedding_api_key("google") else self.settings.EMBEDDING_PROVIDER
            ai_service = get_ai_service(provider)
            
            # 使用对应的API密钥
            api_key = self.settings.get_embedding_api_key(provider)
            
            response = await ai_service.chat_completion(
                messages=[
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in messages
                ],
                api_key=api_key,
                temperature=0.3
            )
            
            expanded_content = response.content.strip()
            
            # 组合原始查询和扩展内容
            expanded_query = f"{original_query} {expanded_content}"
            
            logger.info("查询扩展完成", 
                       original=original_query, 
                       expanded=expanded_query[:100] + "...")
            
            return expanded_query
            
        except Exception as e:
            logger.warning(f"查询扩展失败，使用原始查询: {e}")
            return original_query
    
    async def hybrid_retrieval(
        self, 
        query: str, 
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        混合检索：结合向量搜索和关键词搜索
        """
        try:
            await self._ensure_initialized()
            
            # 1. 向量检索
            vector_results = await self._vector_search(query, top_k)
            
            # 2. 关键词检索
            keyword_results = await self._keyword_search(query, top_k)
            
            # 3. 融合和去重
            combined_results = self._merge_search_results(
                vector_results, 
                keyword_results,
                similarity_threshold
            )
            
            # 4. 重排序
            reranked_results = await self._rerank_results(query, combined_results)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            # 降级到简单搜索
            return await self._simple_search(query, top_k)
    
    async def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """向量搜索"""
        try:
            # 使用配置中指定的嵌入服务商生成查询向量
            embedding_provider = self.settings.EMBEDDING_PROVIDER
            api_key = self.settings.get_embedding_api_key(embedding_provider)
            model = self.settings.get_embedding_model(embedding_provider)
            
            logger.info(f"使用{embedding_provider.upper()}服务生成查询向量，模型: {model}")
            query_embeddings = await generate_embeddings_batch(
                texts=[query], 
                api_key=api_key, 
                provider=embedding_provider,
                model=model
            )
            query_vector = np.array(query_embeddings[0])
            
            # 在向量数据库中搜索
            results = await self.vector_db.search(
                query_vector=query_vector,
                top_k=top_k
            )
            
            # 获取详细信息
            enriched_results = []
            with SessionLocal() as db:
                for result in results:
                    recipe_id = result.get("metadata", {}).get("recipe_id")
                    if recipe_id:
                        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
                        if recipe:
                            enriched_results.append({
                                "recipe_id": recipe.id,
                                "title": recipe.title,
                                "content": recipe.description,
                                "ingredients": recipe.ingredients,
                                "instructions": recipe.instructions,
                                "score": result.get("score", 0.0),
                                "search_type": "vector"
                            })
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    async def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """关键词搜索"""
        try:
            # 提取关键词
            keywords = self._extract_keywords(query)
            
            results = []
            with SessionLocal() as db:
                # 构建搜索条件
                search_filter = []
                for keyword in keywords:
                    search_filter.append(Recipe.title.contains(keyword))
                    search_filter.append(Recipe.description.contains(keyword))
                    search_filter.append(Recipe.ingredients.contains(keyword))
                
                if search_filter:
                    from sqlalchemy import or_
                    recipes = db.query(Recipe).filter(
                        or_(*search_filter)
                    ).limit(top_k).all()
                    
                    for recipe in recipes:
                        # 计算关键词匹配分数
                        score = self._calculate_keyword_score(query, recipe)
                        results.append({
                            "recipe_id": recipe.id,
                            "title": recipe.title,
                            "content": recipe.description,
                            "ingredients": recipe.ingredients,
                            "instructions": recipe.instructions,
                            "score": score,
                            "search_type": "keyword"
                        })
            
            return sorted(results, key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            logger.error(f"关键词搜索失败: {e}")
            return []
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        # 简单的关键词提取，实际项目中可以使用更高级的方法
        # 移除停用词，分词
        stopwords = {"的", "是", "在", "有", "和", "或", "与", "为", "了", "要", "做", "怎么", "如何"}
        words = re.findall(r'\w+', query.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 1]
        return keywords
    
    def _calculate_keyword_score(self, query: str, recipe: Recipe) -> float:
        """计算关键词匹配分数"""
        keywords = self._extract_keywords(query)
        if not keywords:
            return 0.0
        
        # 检查标题、描述、配料中的关键词匹配
        text_fields = [
            recipe.title or "",
            recipe.description or "",
            recipe.ingredients or ""
        ]
        
        total_matches = 0
        total_possible = len(keywords) * len(text_fields)
        
        for field in text_fields:
            field_lower = field.lower()
            for keyword in keywords:
                if keyword in field_lower:
                    total_matches += 1
        
        return total_matches / total_possible if total_possible > 0 else 0.0
    
    def _merge_search_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """合并和去重搜索结果"""
        merged = {}
        
        # 添加向量搜索结果
        for result in vector_results:
            recipe_id = result["recipe_id"]
            if result["score"] >= threshold:
                merged[recipe_id] = result
        
        # 添加关键词搜索结果，合并分数
        for result in keyword_results:
            recipe_id = result["recipe_id"]
            if recipe_id in merged:
                # 已存在，合并分数
                existing = merged[recipe_id]
                combined_score = (existing["score"] + result["score"]) / 2
                existing["score"] = combined_score
                existing["search_type"] = "hybrid"
            else:
                merged[recipe_id] = result
        
        return list(merged.values())
    
    async def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用LLM重新排序结果"""
        try:
            if len(results) <= 1:
                return results
            
            # 构建重排序prompt
            candidates_text = ""
            for i, result in enumerate(results):
                candidates_text += f"\n{i+1}. {result['title']}: {result['content'][:100]}..."
            
            rerank_prompt = f"""作为菜谱搜索专家，请根据用户查询对以下候选菜谱进行重新排序。

用户查询: {query}

候选菜谱:{candidates_text}

请按照相关性从高到低返回序号，格式：[1,3,2,4,5]"""

            messages = [
                {"role": "system", "content": "你是专业的菜谱搜索排序专家。"},
                {"role": "user", "content": rerank_prompt}
            ]
            
            from app.core.ai_service import get_dynamic_ai_service, AIServiceProvider
            ai_service = get_dynamic_ai_service(AIServiceProvider.GOOGLE)
            api_key = getattr(self.settings, 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))
            
            response = await ai_service.chat_completion(
                messages=[
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in messages
                ],
                api_key=api_key,
                temperature=0.1
            )
            
            # 解析排序结果
            rerank_order = self._parse_ranking(response.content)
            
            if rerank_order:
                reranked = []
                for idx in rerank_order:
                    if 0 <= idx < len(results):
                        reranked.append(results[idx])
                # 添加未排序的结果
                used_indices = set(rerank_order)
                for i, result in enumerate(results):
                    if i not in used_indices:
                        reranked.append(result)
                return reranked
            
        except Exception as e:
            logger.warning(f"重排序失败，使用原始排序: {e}")
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _parse_ranking(self, ranking_text: str) -> List[int]:
        """解析排序结果"""
        try:
            # 查找数字列表
            import re
            matches = re.findall(r'\[([0-9,\s]+)\]', ranking_text)
            if matches:
                numbers = [int(x.strip()) - 1 for x in matches[0].split(',') if x.strip().isdigit()]
                return numbers
        except:
            pass
        return []
    
    async def _simple_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """简单搜索（降级方案）"""
        try:
            results = []
            with SessionLocal() as db:
                recipes = db.query(Recipe).filter(
                    Recipe.title.contains(query)
                ).limit(top_k).all()
                
                for recipe in recipes:
                    results.append({
                        "recipe_id": recipe.id,
                        "title": recipe.title,
                        "content": recipe.description,
                        "ingredients": recipe.ingredients,
                        "instructions": recipe.instructions,
                        "score": 0.5,
                        "search_type": "simple"
                    })
            
            return results
        except Exception as e:
            logger.error(f"简单搜索失败: {e}")
            return []
    
    async def generate_rag_response(
        self, 
        query: str, 
        max_results: int = 5,
        include_search_details: bool = False
    ) -> Dict[str, Any]:
        """
        生成RAG增强回答
        """
        try:
            start_time = datetime.now()
            
            # 1. 查询扩展
            expanded_query = await self.query_expansion(query)
            
            # 2. 混合检索
            search_results = await self.hybrid_retrieval(expanded_query, max_results)
            
            # 3. 构建上下文
            context = self._build_context(search_results)
            
            # 4. 生成回答
            answer = await self._generate_contextualized_answer(query, context, search_results)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            response = {
                "answer": answer,
                "results": search_results,
                "query_expanded": expanded_query,
                "processing_time": processing_time,
                "total_results": len(search_results)
            }
            
            if include_search_details:
                response.update({
                    "search_context": context,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("RAG回答生成完成", 
                       query=query[:50], 
                       results_count=len(search_results),
                       processing_time=processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"RAG回答生成失败: {e}")
            return {
                "answer": "抱歉，我暂时无法为您提供回答。请稍后再试。",
                "results": [],
                "error": str(e)
            }
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """构建上下文"""
        if not search_results:
            return "没有找到相关的菜谱信息。"
        
        context_parts = []
        for i, result in enumerate(search_results[:5], 1):
            context_part = f"""
菜谱{i}: {result['title']}
描述: {result['content']}
配料: {result['ingredients']}
做法: {result['instructions'][:200]}...
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def _generate_contextualized_answer(
        self, 
        original_query: str, 
        context: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """基于上下文生成回答"""
        try:
            system_prompt = """你是专业的菜谱AI助手。基于提供的菜谱信息回答用户问题。

要求：
1. 回答要准确、有帮助
2. 如果有多个相关菜谱，可以推荐最相关的几个
3. 提供具体的制作建议
4. 保持友好和专业的语调
5. 如果信息不足，诚实说明"""

            user_prompt = f"""用户问题: {original_query}

相关菜谱信息:
{context}

请基于上述信息回答用户问题："""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            from app.core.ai_service import get_dynamic_ai_service, AIServiceProvider
            ai_service = get_dynamic_ai_service(AIServiceProvider.GOOGLE)
            api_key = getattr(self.settings, 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))
            
            response = await ai_service.chat_completion(
                messages=[
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in messages
                ],
                api_key=api_key,
                temperature=0.7
            )
            
            answer = response.content.strip()
            
            # 如果回答太短或通用，添加推荐信息
            if len(answer) < 100 and search_results:
                recommendations = self._generate_recommendations(search_results[:3])
                answer += f"\n\n{recommendations}"
            
            return answer
            
        except Exception as e:
            logger.error(f"生成上下文回答失败: {e}")
            return "抱歉，我暂时无法基于搜索结果生成回答。"
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> str:
        """生成菜谱推荐"""
        if not results:
            return ""
        
        recommendations = ["为您推荐以下菜谱："]
        for i, result in enumerate(results, 1):
            rec = f"{i}. **{result['title']}** - {result['content'][:50]}..."
            recommendations.append(rec)
        
        return "\n".join(recommendations)


# 全局实例
_rag_service: Optional[AdvancedRAGService] = None


def get_rag_service() -> AdvancedRAGService:
    """获取RAG服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = AdvancedRAGService()
    return _rag_service