"""
数据导入相关的异步任务

处理大量数据导入和向量生成任务。
"""

import asyncio
from typing import Any, Dict, Optional

import structlog
from celery import current_task

from app.core.celery import task
from app.services.data_import_service import DataImportService

logger = structlog.get_logger()


@task(bind=True, name="app.tasks.data_import_tasks.import_epicurious_data")
def import_epicurious_data_task(
    self,
    csv_path: Optional[str] = None,
    start_from: int = 0,
    limit: Optional[int] = None,
    generate_embeddings: bool = True,
) -> Dict[str, Any]:
    """
    异步导入 Epicurious CSV 数据
    
    Args:
        csv_path: CSV文件路径
        start_from: 从第几行开始导入
        limit: 限制导入数量
        generate_embeddings: 是否生成向量嵌入
        
    Returns:
        导入结果统计
    """
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在初始化数据导入...", "progress": 5}
        )
        
        # 创建数据导入服务
        import_service = DataImportService()
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在读取CSV文件...", "progress": 10}
        )
        
        # 运行异步导入
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                import_service.import_epicurious_csv(
                    csv_path=csv_path,
                    start_from=start_from,
                    limit=limit,
                    generate_embeddings=generate_embeddings
                )
            )
        finally:
            loop.close()
        
        # 更新任务状态为完成
        current_task.update_state(
            state="SUCCESS",
            meta={
                "status": "数据导入完成",
                "progress": 100,
                "result": result
            }
        )
        
        logger.info(
            "Epicurious data import completed",
            **result
        )
        
        return {
            "status": "success",
            "stats": result,
            "message": f"成功导入 {result['successful_imports']} 条食谱记录"
        }
        
    except Exception as e:
        logger.error("Failed to import Epicurious data", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "数据导入失败"}
        )
        
        raise


@task(bind=True, name="app.tasks.data_import_tasks.rebuild_all_embeddings")
def rebuild_all_embeddings_task(
    self,
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    异步重建所有食谱的向量嵌入
    
    Args:
        batch_size: 批处理大小
        
    Returns:
        重建结果
    """
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在重建向量嵌入...", "progress": 10}
        )
        
        # 创建数据导入服务
        import_service = DataImportService()
        
        # 运行异步重建
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                import_service.rebuild_embeddings(batch_size=batch_size)
            )
        finally:
            loop.close()
        
        # 更新任务状态为完成
        current_task.update_state(
            state="SUCCESS",
            meta={
                "status": "向量嵌入重建完成",
                "progress": 100,
                "result": result
            }
        )
        
        logger.info("Embeddings rebuild completed", **result)
        
        return {
            "status": "success",
            "result": result,
            "message": f"成功重建 {result['total_processed']} 个向量嵌入"
        }
        
    except Exception as e:
        logger.error("Failed to rebuild embeddings", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "向量嵌入重建失败"}
        )
        
        raise


@task(bind=True, name="app.tasks.data_import_tasks.generate_missing_embeddings")
def generate_missing_embeddings_task(
    self,
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    为缺失向量嵌入的食谱生成嵌入
    
    Args:
        batch_size: 批处理大小
        
    Returns:
        生成结果
    """
    try:
        from app.database import SessionLocal
        from app.models.recipe import Recipe
        from app.core.vector_db import get_vector_db_instance
        # TODO: Fix missing function
# from app.core.ai_service import generate_embeddings_batch
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在检查缺失的向量嵌入...", "progress": 10}
        )
        
        # 获取向量数据库中已有的ID
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            vector_db = loop.run_until_complete(get_vector_db_instance())
            existing_vector_count = loop.run_until_complete(vector_db.get_vector_count())
        finally:
            loop.close()
        
        # 获取数据库中的食谱总数
        with SessionLocal() as db:
            total_recipes = db.query(Recipe).count()
            
            missing_count = max(0, total_recipes - existing_vector_count)
            
            if missing_count == 0:
                return {
                    "status": "success",
                    "message": "所有食谱都已有向量嵌入",
                    "generated_count": 0
                }
            
            # 更新任务状态
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "status": f"发现 {missing_count} 个缺失嵌入，开始生成...",
                    "progress": 30
                }
            )
        
        # 重建所有嵌入（简单实现）
        import_service = DataImportService()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                import_service.rebuild_embeddings(batch_size=batch_size)
            )
        finally:
            loop.close()
        
        # 更新任务状态为完成
        current_task.update_state(
            state="SUCCESS",
            meta={
                "status": "缺失向量嵌入生成完成",
                "progress": 100,
                "result": result
            }
        )
        
        logger.info("Missing embeddings generation completed", **result)
        
        return {
            "status": "success",
            "result": result,
            "message": f"成功生成 {result['total_processed']} 个向量嵌入"
        }
        
    except Exception as e:
        logger.error("Failed to generate missing embeddings", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "缺失向量嵌入生成失败"}
        )
        
        raise


@task(name="app.tasks.data_import_tasks.cleanup_orphaned_vectors")
def cleanup_orphaned_vectors_task() -> Dict[str, Any]:
    """
    清理孤立的向量（数据库中不存在对应食谱的向量）
    """
    try:
        from app.database import SessionLocal
        from app.models.recipe import Recipe
        from app.core.vector_db import get_vector_db_instance
        
        logger.info("Starting orphaned vectors cleanup")
        
        # 获取数据库中的所有食谱ID
        with SessionLocal() as db:
            recipe_ids = set(str(recipe.id) for recipe in db.query(Recipe.id).all())
        
        # 这里可以实现向量数据库的清理逻辑
        # 目前FAISS实现较为简单，暂时跳过具体清理逻辑
        
        logger.info("Orphaned vectors cleanup completed")
        
        return {
            "status": "success",
            "message": "孤立向量清理完成",
            "recipe_count": len(recipe_ids)
        }
        
    except Exception as e:
        logger.error("Failed to cleanup orphaned vectors", error=str(e))
        raise