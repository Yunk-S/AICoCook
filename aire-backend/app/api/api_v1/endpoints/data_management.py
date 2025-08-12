"""
数据管理 API 端点

提供数据导入、向量管理等功能的API接口。
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_superuser
from app.models.user import User
from app.services.data_import_service import DataImportService
from app.tasks.data_import_tasks import (
    import_epicurious_data_task,
    rebuild_all_embeddings_task,
    generate_missing_embeddings_task,
    cleanup_orphaned_vectors_task,
)

router = APIRouter()


class DataImportRequest(BaseModel):
    """数据导入请求模式"""
    csv_path: Optional[str] = Field(None, description="CSV文件路径，为空则使用默认路径")
    start_from: int = Field(0, ge=0, description="从第几行开始导入")
    limit: Optional[int] = Field(None, ge=1, le=50000, description="限制导入数量")
    generate_embeddings: bool = Field(True, description="是否生成向量嵌入")


class EmbeddingRebuildRequest(BaseModel):
    """向量重建请求模式"""
    batch_size: int = Field(100, ge=10, le=1000, description="批处理大小")


class UniversalImportRequest(BaseModel):
    """通用文件导入请求模式"""
    file_path: str = Field(..., description="文件路径")
    file_type: Optional[str] = Field(None, description="文件类型（自动检测）")
    column_mapping: Optional[Dict[str, str]] = Field(None, description="列名映射")
    generate_embeddings: bool = Field(True, description="是否生成向量嵌入")


class DirectoryImportRequest(BaseModel):
    """目录批量导入请求模式"""
    directory_path: str = Field(..., description="目录路径")
    pattern: str = Field("*", description="文件匹配模式")
    generate_embeddings: bool = Field(True, description="是否生成向量嵌入")


@router.get("/status", summary="获取数据导入状态")
async def get_import_status(
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    获取当前数据导入状态
    
    需要超级用户权限。
    """
    try:
        import_service = DataImportService()
        status = await import_service.get_import_status()
        
        return {
            "status": "success",
            "data": status,
            "message": "数据状态获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据状态失败: {str(e)}"
        )


@router.post("/import-epicurious", summary="导入Epicurious数据集")
async def import_epicurious_data(
    request: DataImportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    导入Epicurious CSV数据集
    
    这是一个异步操作，会返回任务ID用于查询进度。
    需要超级用户权限。
    """
    try:
        # 启动异步导入任务
        task = import_epicurious_data_task.delay(
            csv_path=request.csv_path,
            start_from=request.start_from,
            limit=request.limit,
            generate_embeddings=request.generate_embeddings,
        )
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "数据导入任务已启动",
            "estimated_time": "根据数据量，可能需要几分钟到几小时",
            "check_progress_url": f"/api/v1/ai/task/{task.id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动数据导入失败: {str(e)}"
        )


@router.post("/rebuild-embeddings", summary="重建所有向量嵌入")
async def rebuild_embeddings(
    request: EmbeddingRebuildRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    重建所有食谱的向量嵌入
    
    这是一个异步操作，会重新生成所有食谱的向量嵌入。
    需要超级用户权限。
    """
    try:
        # 启动异步重建任务
        task = rebuild_all_embeddings_task.delay(
            batch_size=request.batch_size
        )
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "向量嵌入重建任务已启动",
            "estimated_time": "根据数据量，可能需要几分钟到几小时",
            "check_progress_url": f"/api/v1/ai/task/{task.id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动向量重建失败: {str(e)}"
        )


@router.post("/generate-missing-embeddings", summary="生成缺失的向量嵌入")
async def generate_missing_embeddings(
    request: EmbeddingRebuildRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    为缺失向量嵌入的食谱生成嵌入
    
    检查哪些食谱缺少向量嵌入，并为它们生成。
    需要超级用户权限。
    """
    try:
        # 启动异步生成任务
        task = generate_missing_embeddings_task.delay(
            batch_size=request.batch_size
        )
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "缺失向量嵌入生成任务已启动",
            "estimated_time": "根据缺失数量，可能需要几分钟",
            "check_progress_url": f"/api/v1/ai/task/{task.id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动缺失向量生成失败: {str(e)}"
        )


@router.post("/cleanup-vectors", summary="清理孤立向量")
async def cleanup_orphaned_vectors(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    清理孤立的向量数据
    
    删除数据库中不存在对应食谱的向量嵌入。
    需要超级用户权限。
    """
    try:
        # 启动异步清理任务
        task = cleanup_orphaned_vectors_task.delay()
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "孤立向量清理任务已启动",
            "estimated_time": "通常几分钟内完成",
            "check_progress_url": f"/api/v1/ai/task/{task.id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动向量清理失败: {str(e)}"
        )


@router.get("/vector-stats", summary="获取向量数据库统计")
async def get_vector_stats() -> Dict[str, Any]:
    """
    获取向量数据库的统计信息
    
    公开端点，无需特殊权限。
    """
    try:
        # 导入必要的模块，如果失败则返回默认值
        try:
            from app.core.vector_db import get_vector_db_instance
            from app.database import SessionLocal
            from app.models.recipe import Recipe
        except ImportError as ie:
            return {
                "status": "error",
                "error": f"模块导入失败: {str(ie)}",
                "data": {
                    "vector_database": {"total_vectors": 0, "type": "FAISS"},
                    "recipe_database": {"total_recipes": 0, "epicurious_recipes": 0, "verified_recipes": 0, "coverage_percentage": 0}
                }
            }
        
        # 获取向量数据库统计
        vector_count = 0
        try:
            vector_db = await get_vector_db_instance()
            vector_count = await vector_db.get_vector_count()
        except Exception as ve:
            print(f"向量数据库连接失败: {ve}")
            
        # 获取食谱数据库统计
        total_recipes = 0
        epicurious_recipes = 0
        verified_recipes = 0
        
        try:
            with SessionLocal() as db:
                total_recipes = db.query(Recipe).count()
                epicurious_recipes = db.query(Recipe).filter(Recipe.source == 'epicurious').count()
                verified_recipes = db.query(Recipe).filter(Recipe.is_verified == True).count()
        except Exception as de:
            print(f"数据库查询失败: {de}")
        
        return {
            "status": "success",
            "data": {
                "vector_database": {
                    "total_vectors": vector_count,
                    "type": "FAISS"
                },
                "recipe_database": {
                    "total_recipes": total_recipes,
                    "epicurious_recipes": epicurious_recipes,
                    "verified_recipes": verified_recipes,
                    "coverage_percentage": round((vector_count / total_recipes * 100) if total_recipes > 0 else 0, 2)
                }
            },
            "message": "向量数据库统计获取成功"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": {
                "vector_database": {"total_vectors": 0, "type": "FAISS"},
                "recipe_database": {"total_recipes": 0, "epicurious_recipes": 0, "verified_recipes": 0, "coverage_percentage": 0}
            },
            "message": "向量数据库统计获取失败"
        }


@router.delete("/clear-all-data", summary="清空所有数据")
async def clear_all_data(
    confirm: str,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    清空所有食谱数据和向量嵌入
    
    ⚠️ 危险操作！这将删除所有食谱数据和向量嵌入。
    需要传入 confirm="CLEAR_ALL_DATA" 来确认操作。
    需要超级用户权限。
    """
    if confirm != "CLEAR_ALL_DATA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须传入 confirm='CLEAR_ALL_DATA' 来确认清空操作"
        )
    
    try:
        from app.database import SessionLocal
        from app.models.recipe import Recipe, RecipeIngredient
        from app.core.vector_db import get_vector_db_instance
        import shutil
        from pathlib import Path
        
        # 清空数据库
        with SessionLocal() as db:
            # 删除食材
            db.query(RecipeIngredient).delete()
            # 删除食谱
            recipe_count = db.query(Recipe).count()
            db.query(Recipe).delete()
            db.commit()
        
        # 清空向量数据库文件
        from app.core.config import get_settings
        settings = get_settings()
        embeddings_dir = Path(settings.EMBEDDINGS_DIR)
        
        if embeddings_dir.exists():
            shutil.rmtree(embeddings_dir)
            embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "status": "success",
            "message": f"已清空所有数据，删除了 {recipe_count} 个食谱和对应的向量嵌入"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空数据失败: {str(e)}"
        )


@router.post("/import-file", summary="导入单个文件")
async def import_single_file(
    request: UniversalImportRequest,
    current_user: User = Depends(get_current_superuser),
) -> Dict[str, Any]:
    """
    导入单个文件（支持多种格式）
    
    支持的格式包括:
    - CSV, Excel (结构化数据)
    - PDF, Word (半结构化数据)
    - JSON, TXT, Markdown (非结构化数据)
    
    需要超级用户权限。
    """
    try:
        import_service = DataImportService()
        
        # 检查文件是否存在
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文件不存在: {request.file_path}"
            )
        
        # 检查文件类型支持
        file_type = request.file_type or import_service._detect_file_type(file_path)
        if file_type not in import_service.SUPPORTED_FORMATS.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file_type}"
            )
        
        # 执行导入
        result = await import_service.import_file(
            file_path=request.file_path,
            file_type=request.file_type,
            column_mapping=request.column_mapping,
            generate_embeddings=request.generate_embeddings
        )
        
        return {
            "status": "success",
            "file_path": request.file_path,
            "file_type": file_type,
            "result": result,
            "message": "文件导入成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件导入失败: {str(e)}"
        )


@router.post("/generate-vectors-with-user-key", summary="使用用户API密钥生成向量")
async def generate_vectors_with_user_key(
    x_api_provider: str = Header("google", description="AI服务提供商"),
    x_api_key: Optional[str] = Header(None, description="用户API密钥"),
) -> Dict[str, Any]:
    """
    使用用户提供的API密钥为所有缺失向量的食谱生成嵌入
    不需要超级用户权限，支持所有AI提供商
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"需要在 'X-API-Key' 头中提供 {x_api_provider} 的API密钥"
        )
    
    try:
        from app.services.data_import_service import DataImportService
        from app.database import SessionLocal
        from app.models.recipe import Recipe
        from app.core.ai_service import generate_embeddings_batch
        from app.core.vector_db import get_vector_db_instance
        
        # 获取没有向量的食谱
        with SessionLocal() as db:
            # 简单统计：假设如果向量数为0，则所有食谱都需要生成向量
            vector_db = await get_vector_db_instance()
            current_vector_count = await vector_db.get_vector_count()
            
            if current_vector_count > 0:
                return {
                    "status": "success",
                    "message": f"向量已存在 ({current_vector_count} 个)，无需重新生成",
                    "vector_count": current_vector_count
                }
            
            # 获取所有食谱
            recipes = db.query(Recipe).all()
            total_recipes = len(recipes)
            
            if total_recipes == 0:
                return {
                    "status": "success", 
                    "message": "数据库中没有食谱数据",
                    "vector_count": 0
                }
        
        # 准备向量生成数据
        recipes_data = []
        for recipe in recipes:
            # 构建文本内容
            text_parts = []
            if recipe.title:
                text_parts.append(f"标题: {recipe.title}")
            if recipe.description:
                text_parts.append(f"描述: {recipe.description}")
            if recipe.instructions:
                text_parts.append(f"制作方法: {recipe.instructions}")
                
            text_content = ". ".join(text_parts)
            
            recipes_data.append({
                'id': recipe.id,
                'text': text_content,
                'metadata': {
                    'recipe_id': recipe.id,
                    'title': recipe.title or "未知标题",
                    'source': 'user_generated'
                }
            })
        
        # 使用用户API密钥生成向量
        texts = [recipe['text'] for recipe in recipes_data]
        
        # 支持多个提供商
        embeddings = await generate_embeddings_batch(
            texts, 
            x_api_key, 
            provider=x_api_provider
        )
        
        # 存储向量
        ids = [str(recipe['id']) for recipe in recipes_data]
        metadata = [recipe['metadata'] for recipe in recipes_data]
        
        await vector_db.add_vectors(
            vectors=embeddings,
            ids=ids,
            metadata=metadata
        )
        
        return {
            "status": "success",
            "message": f"成功生成 {len(embeddings)} 个向量嵌入",
            "vector_count": len(embeddings),
            "recipes_processed": total_recipes,
            "provider": x_api_provider
        }
        
    except Exception as e:
        logger.error("用户向量生成失败", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"向量生成失败: {str(e)}"
        )


@router.get("/service-status", summary="获取服务连接状态")
async def get_service_status() -> Dict[str, Any]:
    """
    获取RAG和LLM服务的连接状态
    """
    try:
        # 尝试导入必要模块
        try:
            from app.core.ai_service import get_ai_service
            from app.core.vector_db import get_vector_db_instance
            from app.core.config import get_settings
        except ImportError as ie:
            return {
                "status": "error",
                "overall_status": "error",
                "error": f"模块导入失败: {str(ie)}",
                "message": "服务模块不可用"
            }
        
        settings = get_settings()
        status_info = {
            "vector_db": {
                "status": "unknown",
                "type": "FAISS",
                "error": None
            },
            "ai_services": {
                "available_providers": ["google", "deepseek"],
                "default_provider": "google",
                "api_key_configured": False,
                "error": None
            },
            "embedding_service": {
                "status": "unknown",
                "provider": "google",
                "error": None
            }
        }
        
        # 检查向量数据库状态
        try:
            vector_db = await get_vector_db_instance()
            vector_count = await vector_db.get_vector_count()
            status_info["vector_db"]["status"] = "connected"
            status_info["vector_db"]["vector_count"] = vector_count
        except Exception as e:
            status_info["vector_db"]["status"] = "error"
            status_info["vector_db"]["error"] = str(e)
        
        # 检查AI服务状态
        try:
            # 检查是否配置了API密钥
            api_key = getattr(settings, 'DEFAULT_AI_API_KEY', '') or getattr(settings, 'GOOGLE_API_KEY', '')
            status_info["ai_services"]["api_key_configured"] = bool(api_key)
            
            if api_key:
                # 尝试获取AI服务实例
                ai_service = get_ai_service("google")
                status_info["ai_services"]["status"] = "configured"
                status_info["embedding_service"]["status"] = "configured"
            else:
                status_info["ai_services"]["status"] = "not_configured"
                status_info["embedding_service"]["status"] = "not_configured"
                
        except Exception as e:
            status_info["ai_services"]["status"] = "error"
            status_info["ai_services"]["error"] = str(e)
            status_info["embedding_service"]["status"] = "error"
            status_info["embedding_service"]["error"] = str(e)
        
        # 整体状态评估
        overall_status = "healthy"
        if (status_info["vector_db"]["status"] == "error" or 
            status_info["ai_services"]["status"] == "error"):
            overall_status = "error"
        elif (status_info["vector_db"]["status"] == "unknown" or 
              status_info["ai_services"]["status"] in ["not_configured", "unknown"]):
            overall_status = "partial"
        
        return {
            "status": "success",
            "overall_status": overall_status,
            "services": status_info,
            "timestamp": "2025-01-27T12:00:00",
            "message": "服务状态检查完成"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "overall_status": "error",
            "error": str(e),
            "message": "服务状态检查失败"
        }


@router.get("/supported-formats", summary="获取支持的文件格式")
async def get_supported_formats() -> Dict[str, Any]:
    """
    获取系统支持的文件格式列表
    """
    import_service = DataImportService()
    
    # 按类型分组格式
    formats_by_type = {
        "结构化数据": {
            "csv": "逗号分隔值文件",
            "excel": "Excel电子表格 (.xlsx, .xls)",
            "json": "JSON数据文件"
        },
        "半结构化数据": {
            "pdf": "PDF文档",
            "word": "Word文档 (.docx, .doc)",
            "html": "HTML网页",
            "xml": "XML文件"
        },
        "非结构化数据": {
            "text": "纯文本文件 (.txt)",
            "markdown": "Markdown文档 (.md)"
        }
    }
    
    # 检查unstructured库可用性
    from app.services.data_import_service import UNSTRUCTURED_AVAILABLE
    
    availability_notes = []
    if not UNSTRUCTURED_AVAILABLE:
        availability_notes.append("注意: 未安装 unstructured 库，只支持 CSV, Excel, JSON, TXT 格式")
    
    return {
        "status": "success",
        "formats": formats_by_type,
        "total_formats": len(import_service.SUPPORTED_FORMATS),
        "extension_mapping": import_service.SUPPORTED_FORMATS,
        "unstructured_available": UNSTRUCTURED_AVAILABLE,
        "notes": availability_notes
    }



@router.get("/imported-files", summary="获取已导入文件列表")
async def get_imported_files() -> Dict[str, Any]:
    """
    获取RAG数据库中已导入的文件列表
    
    返回按数据源分组的文件统计信息，包括记录数量和最后导入时间。
    """
    try:
        # 尝试导入必要模块
        try:
            from app.database import SessionLocal
            from app.models.recipe import Recipe
            from sqlalchemy import func
        except ImportError as ie:
            return {
                "status": "error",
                "error": f"模块导入失败: {str(ie)}",
                "data": {"files": [], "total_files": 0, "total_recipes": 0},
                "message": "数据库模块不可用"
            }
        
        with SessionLocal() as db:
            # 查询按数据源分组的食谱统计
            source_stats = db.query(
                Recipe.source,
                func.count(Recipe.id).label('count'),
                func.max(Recipe.created_at).label('last_imported')
            ).group_by(Recipe.source).all()
            
            files = []
            for source, count, last_imported in source_stats:
                files.append({
                    "source": source or "unknown",
                    "count": count,
                    "last_imported": last_imported.isoformat() if last_imported else None
                })
            
            return {
                "status": "success",
                "data": {
                    "files": files,
                    "total_files": len(files),
                    "total_recipes": sum(f["count"] for f in files)
                },
                "message": "已导入文件列表获取成功"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "获取文件列表失败"
        }


@router.get("/import-status", summary="获取数据导入状态")
async def get_import_status() -> Dict[str, Any]:
    """
    获取数据导入状态，显示所有已导入的文件
    即使向量未生成也要显示文件信息
    """
    try:
        from app.database import SessionLocal
        from app.models.recipe import Recipe
        
        db = SessionLocal()
        
        try:
            # 获取数据库中的记录统计
            total_recipes = db.query(Recipe).count()
            
            # 检查源文件
            import os
            from pathlib import Path
            
            # 获取当前文件路径，找到项目根目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent  # 到达项目根目录
            csv_file_path = project_root / "aire-backend" / "data" / "raw" / "epi_r.csv"
            
            files_info = []
            
            # 检查CSV文件
            if csv_file_path.exists():
                file_size = csv_file_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                
                # 读取文件行数（采样估算）
                try:
                    line_count = 0
                    with open(csv_file_path, 'r', encoding='utf-8') as f:
                        for i, _ in enumerate(f):
                            line_count = i + 1
                            if i >= 100:  # 采样前100行估算
                                # 根据文件大小估算总行数
                                sample_size = f.tell()
                                estimated_total = int((file_size / sample_size) * 100)
                                line_count = estimated_total
                                break
                except:
                    line_count = 20000  # 默认估计值
                
                files_info.append({
                    "name": "epi_r.csv",
                    "path": str(csv_file_path),
                    "size_mb": round(file_size_mb, 2),
                    "estimated_records": line_count,
                    "imported_records": total_recipes,
                    "status": "已导入" if total_recipes > 0 else "文件存在",
                    "import_percentage": round((total_recipes / line_count) * 100, 1) if line_count > 0 else 0,
                    "last_checked": "刚刚"
                })
            else:
                files_info.append({
                    "name": "epi_r.csv",
                    "path": str(csv_file_path),
                    "size_mb": 0,
                    "estimated_records": 0,
                    "imported_records": total_recipes,
                    "status": "文件未找到",
                    "import_percentage": 0,
                    "last_checked": "刚刚"
                })
            
            return {
                "status": "success",
                "files": files_info,
                "total_imported": total_recipes,
                "message": f"找到 {len(files_info)} 个数据文件，已导入 {total_recipes} 条记录"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error("获取导入状态失败", error=str(e), exc_info=True)
        
        # 即使出错也返回基本信息
        return {
            "status": "error",
            "files": [
                {
                    "name": "epi_r.csv",
                    "path": "aire-backend/data/raw/epi_r.csv", 
                    "size_mb": 0,
                    "estimated_records": 20000,
                    "imported_records": 0,
                    "status": "检查失败",
                    "import_percentage": 0,
                    "last_checked": "刚刚"
                }
            ],
            "total_imported": 0,
            "error": str(e),
            "message": "获取导入状态失败，显示默认信息"
        }