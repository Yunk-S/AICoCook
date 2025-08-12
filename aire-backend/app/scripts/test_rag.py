#!/usr/bin/env python3
"""
RAG系统测试脚本
==============

测试新的RAG检索增强生成系统。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['EMBEDDINGS_DIR'] = str(project_root / 'data' / 'embeddings')
os.environ['DATABASE_URL'] = 'sqlite:///./data/aire_local.db'
os.environ['VECTOR_DB_TYPE'] = 'faiss'

import structlog
from app.services.rag_service import get_rag_service
from app.core.config import get_settings

logger = structlog.get_logger()


async def test_rag_system():
    """测试RAG系统"""
    try:
        logger.info("开始测试RAG系统...")
        
        # 获取RAG服务
        rag_service = get_rag_service()
        
        # 测试查询
        test_queries = [
            "川菜有什么特色菜？",
            "如何做红烧肉？",
            "素食有哪些推荐？",
            "快手菜推荐",
            "适合减肥的菜谱"
        ]
        
        for query in test_queries:
            logger.info(f"测试查询: {query}")
            
            try:
                # 测试查询扩展
                expanded_query = await rag_service.query_expansion(query)
                logger.info(f"扩展查询: {expanded_query[:100]}...")
                
                # 测试混合检索
                results = await rag_service.hybrid_retrieval(query, top_k=3)
                logger.info(f"检索到 {len(results)} 个结果")
                
                # 测试完整RAG回答
                response = await rag_service.generate_rag_response(query, max_results=3)
                logger.info(f"生成回答: {response['answer'][:100]}...")
                
                print(f"\n=== 查询: {query} ===")
                print(f"回答: {response['answer']}")
                print(f"检索结果数: {response['total_results']}")
                print(f"处理时间: {response['processing_time']:.2f}秒")
                print("-" * 50)
                
            except Exception as e:
                logger.error(f"查询 '{query}' 测试失败: {e}")
        
        logger.info("RAG系统测试完成")
        
    except Exception as e:
        logger.error(f"RAG测试失败: {e}")
        raise


async def test_simple_retrieval():
    """测试简单检索功能"""
    try:
        logger.info("测试简单检索功能...")
        
        rag_service = get_rag_service()
        
        # 测试关键词搜索
        query = "鸡肉"
        results = await rag_service._keyword_search(query, 5)
        logger.info(f"关键词搜索 '{query}' 返回 {len(results)} 个结果")
        
        for result in results[:3]:
            print(f"- {result['title']}: {result['content'][:50]}...")
        
    except Exception as e:
        logger.error(f"简单检索测试失败: {e}")


async def main():
    """主函数"""
    logger.info("开始RAG系统综合测试...")
    
    try:
        # 基本检索测试
        await test_simple_retrieval()
        
        # 完整RAG测试
        await test_rag_system()
        
        logger.info("所有测试完成！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # 配置日志
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)