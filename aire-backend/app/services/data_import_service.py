"""
数据导入服务

支持多种格式的数据导入，包括CSV、PDF、Word、JSON等，并生成向量嵌入。
基于现代RAG系统最佳实践设计。
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import structlog
from sqlalchemy.orm import Session

# 文档处理库

try:
    from unstructured.partition.auto import partition
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.docx import partition_docx
    from unstructured.partition.csv import partition_csv
    from unstructured.partition.text import partition_text
    UNSTRUCTURED_AVAILABLE = True
    logger = structlog.get_logger()
    logger.info("unstructured库已成功加载，支持多种文件格式导入")
except (ImportError, Exception) as e:
    UNSTRUCTURED_AVAILABLE = False
    logger = structlog.get_logger()
    logger.warning(f"unstructured库不可用: {e}")
    logger.warning("仅支持CSV格式导入。要支持更多格式，请安装: pip install unstructured[local-inference]")
    logger.info("如需支持PDF等格式，请确保已安装所需依赖包")

from app.core.config import get_settings
from app.core.ai_service import generate_embeddings_batch
from app.core.exceptions import ValidationException
from app.core.vector_db import get_vector_db_instance
from app.database import SessionLocal
from app.models.recipe import Recipe, RecipeCategory, RecipeIngredient

logger = structlog.get_logger()
settings = get_settings()


class DataImportService:
    """数据导入服务类 - 支持多种格式"""
    
    SUPPORTED_FORMATS = {
        # 结构化数据
        '.csv': 'csv',
        '.xlsx': 'excel', 
        '.xls': 'excel',
        '.json': 'json',
        
        # 半结构化数据
        '.pdf': 'pdf',
        '.docx': 'word',
        '.doc': 'word',
        '.html': 'html',
        '.xml': 'xml',
        
        # 非结构化数据
        '.txt': 'text',
        '.md': 'markdown',
    }
    
    def __init__(self):
        self.data_dir = Path(settings.EMBEDDINGS_DIR).parent / "raw"
        self.batch_size = 100  # 批量处理大小
        
        # 尝试初始化unstructured库（如果需要）
        self._ensure_unstructured_available()
    
    def _ensure_unstructured_available(self):
        """确保unstructured库可用"""
        global UNSTRUCTURED_AVAILABLE
        if not UNSTRUCTURED_AVAILABLE:
            logger.info("尝试修复并重新加载unstructured库...")
            try:
                # 先尝试修复NLTK数据
                try:
                    import nltk
                    nltk.download('punkt', quiet=True)
                    nltk_fixed = True
                except:
                    nltk_fixed = False
                    
                if nltk_fixed:
                    # 重新导入
                    from unstructured.partition.auto import partition
                    from unstructured.partition.pdf import partition_pdf
                    from unstructured.partition.docx import partition_docx
                    from unstructured.partition.csv import partition_csv
                    from unstructured.partition.text import partition_text
                    UNSTRUCTURED_AVAILABLE = True
                    logger.info("unstructured库修复成功！现已支持多种文件格式")
                    
                    # 更新全局变量
                    globals().update({
                        'partition': partition,
                        'partition_pdf': partition_pdf,
                        'partition_docx': partition_docx,
                        'partition_csv': partition_csv,
                        'partition_text': partition_text
                    })
            except Exception as e:
                logger.warning(f"无法修复unstructured库: {e}")
    
    def get_supported_formats(self):
        """获取当前支持的文件格式"""
        if UNSTRUCTURED_AVAILABLE:
            return self.SUPPORTED_FORMATS
        else:
            # 只返回CSV和基础格式
            return {
                '.csv': 'csv',
                '.json': 'json'
            }
        
    async def import_epicurious_csv(
        self,
        csv_path: Optional[str] = None,
        start_from: int = 0,
        limit: Optional[int] = None,
        generate_embeddings: bool = True,
        embedding_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导入 Epicurious CSV 数据
        
        Args:
            csv_path: CSV文件路径，默认使用data/raw/epi_r.csv
            start_from: 从第几行开始导入
            limit: 限制导入数量
            generate_embeddings: 是否生成向量嵌入
            embedding_provider: 嵌入服务提供商（google, openai, doubao, zhipu, deepseek）
            
        Returns:
            导入统计信息
        """
        if csv_path is None:
            csv_path = self.data_dir / "epi_r.csv"
        
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV文件未找到: {csv_path}")
        
        logger.info(
            "开始导入Epicurious数据",
            csv_path=str(csv_path),
            start_from=start_from,
            limit=limit
        )
        
        stats = {
            "total_processed": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "embeddings_generated": 0,
            "errors": []
        }
        
        try:
            # 读取CSV文件
            logger.info("读取CSV文件...")
            
            # 分块读取大文件
            chunk_size = 1000
            chunks = []
            
            for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
                chunks.append(chunk)
                if limit and len(chunks) * chunk_size >= limit + start_from:
                    break
            
            # 合并所有块
            df = pd.concat(chunks, ignore_index=True)
            
            # 应用开始位置和限制
            if start_from > 0:
                df = df.iloc[start_from:]
            if limit:
                df = df.head(limit)
            
            logger.info(f"CSV文件读取完成，共{len(df)}条记录")
            
            # 数据清理和预处理
            df = self._clean_data(df)
            
            # 批量导入到数据库
            with SessionLocal() as db:
                for i in range(0, len(df), self.batch_size):
                    batch = df.iloc[i:i + self.batch_size]
                    batch_stats = await self._import_batch(db, batch, generate_embeddings, embedding_provider)
                    
                    stats["total_processed"] += batch_stats["processed"]
                    stats["successful_imports"] += batch_stats["successful"]
                    stats["failed_imports"] += batch_stats["failed"]
                    stats["embeddings_generated"] += batch_stats["embeddings"]
                    stats["errors"].extend(batch_stats["errors"])
                    
                    logger.info(
                        f"批次导入完成 {i//self.batch_size + 1}/{(len(df)-1)//self.batch_size + 1}",
                        processed=stats["total_processed"],
                        successful=stats["successful_imports"]
                    )
                    
                    # 提交批次
                    db.commit()
            
            logger.info("数据导入完成", **stats)
            return stats
            
        except Exception as e:
            logger.error("数据导入失败", error=str(e))
            stats["errors"].append(f"导入失败: {str(e)}")
            raise
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理和预处理数据"""
        logger.info("开始数据清理...")
        
        # 删除空标题的记录
        df = df.dropna(subset=['title'])
        
        # 清理标题
        df['title'] = df['title'].astype(str).str.strip()
        
        # 处理食材列表
        if 'ingredients' in df.columns:
            df['ingredients'] = df['ingredients'].apply(self._process_ingredients)
        
        # 处理制作步骤
        if 'directions' in df.columns:
            df['directions'] = df['directions'].apply(self._process_directions)
        
        # 清理数值字段
        numeric_columns = ['calories', 'protein', 'fat', 'sodium', 'rating']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理分类
        if 'categories' in df.columns:
            df['categories'] = df['categories'].apply(self._process_categories)
        
        logger.info(f"数据清理完成，剩余{len(df)}条记录")
        return df
    
    def _process_ingredients(self, ingredients_str: Any) -> List[str]:
        """处理食材字符串"""
        if pd.isna(ingredients_str):
            return []
        
        try:
            # 尝试解析JSON格式
            if isinstance(ingredients_str, str):
                # 如果是JSON字符串
                if ingredients_str.startswith('['):
                    return json.loads(ingredients_str)
                else:
                    # 如果是逗号分隔的字符串
                    return [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]
            elif isinstance(ingredients_str, list):
                return ingredients_str
            else:
                return []
        except:
            return []
    
    def _process_directions(self, directions_str: Any) -> List[str]:
        """处理制作步骤字符串"""
        if pd.isna(directions_str):
            return []
        
        try:
            if isinstance(directions_str, str):
                # 如果是JSON字符串
                if directions_str.startswith('['):
                    return json.loads(directions_str)
                else:
                    # 按句号或数字序号分割步骤
                    steps = re.split(r'\d+\.\s*|\.(?:\s|$)', directions_str)
                    return [step.strip() for step in steps if step.strip()]
            elif isinstance(directions_str, list):
                return directions_str
            else:
                return []
        except:
            return [str(directions_str)] if directions_str else []
    
    def _process_categories(self, categories_str: Any) -> List[str]:
        """处理分类字符串"""
        if pd.isna(categories_str):
            return []
        
        try:
            if isinstance(categories_str, str):
                if categories_str.startswith('['):
                    return json.loads(categories_str)
                else:
                    return [cat.strip() for cat in categories_str.split(',') if cat.strip()]
            elif isinstance(categories_str, list):
                return categories_str
            else:
                return []
        except:
            return []
    
    async def _import_batch(
        self,
        db: Session,
        batch_df: pd.DataFrame,
        generate_embeddings: bool = True,
        embedding_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """导入一批数据"""
        batch_stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "embeddings": 0,
            "errors": []
        }
        
        recipes_for_embedding = []
        
        for _, row in batch_df.iterrows():
            batch_stats["processed"] += 1
            
            try:
                # 检查是否已存在相同标题的食谱
                existing = db.query(Recipe).filter(Recipe.title == row['title']).first()
                if existing:
                    continue
                
                # 创建食谱对象
                recipe_data = self._create_recipe_data(row)
                recipe = Recipe(**recipe_data)
                
                db.add(recipe)
                db.flush()  # 获取ID但不提交
                
                # 添加食材详情
                if recipe_data.get('ingredients'):
                    for idx, ingredient_name in enumerate(recipe_data['ingredients']):
                        ingredient = RecipeIngredient(
                            recipe_id=recipe.id,
                            name=ingredient_name,
                            order_index=idx
                        )
                        db.add(ingredient)
                
                # 准备向量嵌入数据
                if generate_embeddings:
                    embedding_text = self._create_embedding_text(recipe_data)
                    recipes_for_embedding.append({
                        'id': recipe.id,
                        'text': embedding_text,
                        'metadata': {
                            'title': recipe.title,
                            'description': recipe.description,
                            'calories': recipe.calories,
                            'rating': recipe.rating,
                            'difficulty': recipe.difficulty,
                            'total_time': recipe.total_time,
                            'categories': recipe_data.get('categories', []),
                        }
                    })
                
                batch_stats["successful"] += 1
                
            except Exception as e:
                batch_stats["failed"] += 1
                batch_stats["errors"].append(f"导入食谱失败 '{row.get('title', 'Unknown')}': {str(e)}")
                logger.error("导入食谱失败", title=row.get('title'), error=str(e))
        
        # 生成向量嵌入
        if generate_embeddings and recipes_for_embedding:
            try:
                await self._generate_embeddings(recipes_for_embedding, embedding_provider)
                batch_stats["embeddings"] = len(recipes_for_embedding)
            except Exception as e:
                batch_stats["errors"].append(f"生成向量嵌入失败: {str(e)}")
                logger.error("生成向量嵌入失败", error=str(e))
        
        return batch_stats
    
    def _create_recipe_data(self, row: pd.Series) -> Dict[str, Any]:
        """从CSV行创建食谱数据"""
        ingredients = row.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = self._process_ingredients(ingredients)
        
        directions = row.get('directions', [])
        if isinstance(directions, str):
            directions = self._process_directions(directions)
        
        categories = row.get('categories', [])
        if isinstance(categories, str):
            categories = self._process_categories(categories)
        
        # 生成用于嵌入的文本
        ingredients_text = ", ".join(ingredients) if ingredients else ""
        text_for_embedding = f"{row['title']}. 食材: {ingredients_text}"
        
        return {
            'title': row['title'],
            'description': row.get('desc', ''),
            'ingredients': ingredients,
            'directions': directions,
            'calories': row.get('calories') if pd.notna(row.get('calories')) else None,
            'protein': row.get('protein') if pd.notna(row.get('protein')) else None,
            'fat': row.get('fat') if pd.notna(row.get('fat')) else None,
            'sodium': row.get('sodium') if pd.notna(row.get('sodium')) else None,
            'rating': row.get('rating') if pd.notna(row.get('rating')) else None,
            'source': 'epicurious',
            'text_for_embedding': text_for_embedding,
            'is_public': True,
            'is_verified': True,
        }
    
    def _create_embedding_text(self, recipe_data: Dict[str, Any]) -> str:
        """创建用于向量嵌入的文本"""
        parts = [recipe_data['title']]
        
        if recipe_data.get('description'):
            parts.append(recipe_data['description'])
        
        if recipe_data.get('ingredients'):
            ingredients_text = ", ".join(recipe_data['ingredients'])
            parts.append(f"食材: {ingredients_text}")
        
        return ". ".join(parts)
    
    async def _generate_embeddings(self, recipes_data: List[Dict], provider: str = None) -> None:
        """为食谱生成向量嵌入"""
        if not recipes_data:
            return
        
        logger.info(f"开始生成{len(recipes_data)}个食谱的向量嵌入")
        
        # 提取文本
        texts = [recipe['text'] for recipe in recipes_data]
        
        # 生成嵌入向量
        try:
            settings = get_settings()
            
            # 确定使用的服务商
            if provider is None:
                provider = settings.EMBEDDING_PROVIDER
            
            # 获取对应的API密钥和模型
            api_key = settings.get_embedding_api_key(provider)
            model = settings.get_embedding_model(provider)
            
            if api_key:
                logger.info(f"使用{provider.upper()}服务生成向量嵌入，模型: {model}")
                embeddings = await generate_embeddings_batch(
                    texts=texts, 
                    api_key=api_key, 
                    provider=provider,
                    model=model
                )
                logger.info(f"成功生成{len(embeddings)}个嵌入向量")
            else:
                logger.warning(f"未配置{provider.upper()}服务的API密钥，跳过嵌入向量生成")
                logger.warning(f"请在配置文件中设置{provider.upper()}_API_KEY或DEFAULT_AI_API_KEY以启用向量生成功能")
                embeddings = []
                
        except Exception as e:
            logger.error("嵌入向量生成失败", error=str(e), provider=provider)
            # 如果当前提供商失败，尝试使用Google作为备选方案
            if provider != "google":
                logger.info("尝试使用Google作为备选嵌入服务")
                try:
                    google_api_key = settings.get_embedding_api_key("google")
                    if google_api_key:
                        embeddings = await generate_embeddings_batch(
                            texts=texts,
                            api_key=google_api_key,
                            provider="google",
                            model=settings.get_embedding_model("google")
                        )
                        logger.info(f"备选方案成功生成{len(embeddings)}个嵌入向量")
                    else:
                        embeddings = []
                except Exception as backup_e:
                    logger.error("备选嵌入向量生成也失败", error=str(backup_e))
                    embeddings = []
            else:
                embeddings = []
        
        # 只有在有向量数据时才存储
        if embeddings:
            # 存储到向量数据库
            vector_db = await get_vector_db_instance()
            
            ids = [str(recipe['id']) for recipe in recipes_data]
            metadata = [recipe['metadata'] for recipe in recipes_data]
            
            await vector_db.add_vectors(
                vectors=embeddings,
                ids=ids,
                metadata=metadata
            )
            
            logger.info(f"向量嵌入生成完成，存储了{len(embeddings)}个向量")
        else:
            logger.warning("未生成任何向量嵌入，跳过存储")
    
    # 变更原有_generate_embeddings的签名以避免冲突
    async def _generate_embeddings_flexible(self, recipes_data: List[Dict], provider: str = None) -> None:
        """为食谱生成向量嵌入（灵活版本）"""
        # 使用主要的_generate_embeddings方法
        await self._generate_embeddings(recipes_data, provider)
    
    async def get_import_status(self) -> Dict[str, Any]:
        """获取导入状态"""
        with SessionLocal() as db:
            total_recipes = db.query(Recipe).count()
            epicurious_recipes = db.query(Recipe).filter(Recipe.source == 'epicurious').count()
            
            # 检查向量数据库状态
            try:
                vector_db = await get_vector_db_instance()
                vector_count = await vector_db.get_vector_count()
            except:
                vector_count = 0
            
            return {
                "total_recipes": total_recipes,
                "epicurious_recipes": epicurious_recipes,
                "vector_count": vector_count,
                "csv_file_exists": (self.data_dir / "epi_r.csv").exists(),
                "csv_file_size": (self.data_dir / "epi_r.csv").stat().st_size if (self.data_dir / "epi_r.csv").exists() else 0,
            }
    
    async def rebuild_embeddings(self, batch_size: int = 100) -> Dict[str, Any]:
        """重建所有食谱的向量嵌入"""
        logger.info("开始重建向量嵌入")
        
        with SessionLocal() as db:
            total_recipes = db.query(Recipe).count()
            processed = 0
            
            for offset in range(0, total_recipes, batch_size):
                recipes = db.query(Recipe).offset(offset).limit(batch_size).all()
                
                recipes_data = []
                for recipe in recipes:
                    embedding_text = self._create_embedding_text({
                        'title': recipe.title,
                        'description': recipe.description,
                        'ingredients': recipe.ingredients or []
                    })
                    
                    recipes_data.append({
                        'id': recipe.id,
                        'text': embedding_text,
                        'metadata': {
                            'title': recipe.title,
                            'description': recipe.description,
                            'calories': recipe.calories,
                            'rating': recipe.rating,
                            'difficulty': recipe.difficulty,
                            'total_time': recipe.total_time,
                        }
                    })
                
                if recipes_data:
                    await self._generate_embeddings(recipes_data)
                    processed += len(recipes_data)
                
                logger.info(f"重建进度: {processed}/{total_recipes}")
        
        return {
            "status": "completed",
            "total_processed": processed,
        }
    
    # ========== 通用文件导入功能 ==========
    
    async def import_file(
        self,
        file_path: Union[str, Path],
        file_type: Optional[str] = None,
        column_mapping: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通用文件导入接口
        
        Args:
            file_path: 文件路径
            file_type: 文件类型（可选，自动检测）
            column_mapping: 列名映射字典 {"target_field": "source_column"}
            **kwargs: 额外参数
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件未找到: {file_path}")
        
        # 自动检测文件类型
        if file_type is None:
            file_type = self._detect_file_type(file_path)
        
        if file_type not in self.SUPPORTED_FORMATS.values():
            if not UNSTRUCTURED_AVAILABLE and file_type != 'csv':
                raise ValueError(f"不支持的文件类型: {file_type}。请安装 unstructured 库以支持更多格式")
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        logger.info(f"开始导入文件", file_path=str(file_path), file_type=file_type)
        
        # 根据文件类型选择处理方法
        if file_type == 'csv':
            return await self._import_csv_flexible(file_path, column_mapping, **kwargs)
        elif file_type == 'excel':
            return await self._import_excel(file_path, column_mapping, **kwargs)
        elif file_type == 'json':
            return await self._import_json(file_path, column_mapping, **kwargs)
        elif file_type == 'pdf' and UNSTRUCTURED_AVAILABLE:
            return await self._import_pdf(file_path, **kwargs)
        elif file_type == 'word' and UNSTRUCTURED_AVAILABLE:
            return await self._import_word(file_path, **kwargs)
        elif file_type in ['text', 'markdown']:
            return await self._import_text(file_path, **kwargs)
        elif UNSTRUCTURED_AVAILABLE:
            # 使用unstructured库自动处理
            return await self._import_auto(file_path, **kwargs)
        else:
            raise ValueError(f"无法处理文件类型: {file_type}")
    
    def _detect_file_type(self, file_path: Path) -> str:
        """自动检测文件类型"""
        suffix = file_path.suffix.lower()
        return self.SUPPORTED_FORMATS.get(suffix, 'unknown')
    
    async def _import_csv_flexible(
        self, 
        file_path: Path, 
        column_mapping: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        灵活的CSV导入 - 支持不同列名映射
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 应用列名映射
            if column_mapping:
                df = df.rename(columns={v: k for k, v in column_mapping.items()})
            
            # 智能映射常见字段
            df = self._smart_column_mapping(df)
            
            # 数据清理和标准化
            df = self._clean_flexible_data(df)
            
            return await self._process_dataframe(df, source=f"csv_{file_path.stem}")
            
        except Exception as e:
            logger.error("CSV导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"CSV导入失败: {str(e)}")
    
    def _smart_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """智能列名映射 - 自动识别常见字段"""
        
        # 常见字段映射规则
        mapping_rules = {
            'title': ['name', 'recipe_name', 'dish_name', 'title', '菜名', '标题', '名称'],
            'description': ['desc', 'description', 'summary', 'intro', '描述', '简介'],
            'ingredients': ['ingredients', 'ingredient_list', 'materials', '食材', '配料'],
            'directions': ['directions', 'steps', 'instructions', 'method', '步骤', '做法', '制作方法'],
            'calories': ['calories', 'cal', 'energy', '卡路里', '热量'],
            'cooking_time': ['cook_time', 'time', 'duration', '烹饪时间', '时间'],
            'difficulty': ['difficulty', 'level', '难度'],
            'rating': ['rating', 'score', 'stars', '评分', '评级'],
            'category': ['category', 'type', 'cuisine', '分类', '菜系'],
        }
        
        # 执行映射
        column_mapping = {}
        df_columns_lower = [col.lower() for col in df.columns]
        
        for target_field, possible_names in mapping_rules.items():
            for possible_name in possible_names:
                if possible_name.lower() in df_columns_lower:
                    original_col = df.columns[df_columns_lower.index(possible_name.lower())]
                    column_mapping[original_col] = target_field
                    break
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            logger.info("应用智能列名映射", mapping=column_mapping)
        
        return df
    
    async def _import_excel(self, file_path: Path, column_mapping: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """导入Excel文件"""
        try:
            # 读取Excel文件（默认第一个sheet）
            df = pd.read_excel(file_path)
            
            # 应用列名映射
            if column_mapping:
                df = df.rename(columns={v: k for k, v in column_mapping.items()})
            
            # 智能映射和清理
            df = self._smart_column_mapping(df)
            df = self._clean_flexible_data(df)
            
            return await self._process_dataframe(df, source=f"excel_{file_path.stem}")
            
        except Exception as e:
            logger.error("Excel导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"Excel导入失败: {str(e)}")
    
    async def _import_json(self, file_path: Path, column_mapping: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """导入JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 根据JSON结构处理数据
            if isinstance(data, list):
                # JSON数组格式
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'recipes' in data:
                    # 嵌套格式 {"recipes": [...]}
                    df = pd.DataFrame(data['recipes'])
                else:
                    # 单个对象转为列表
                    df = pd.DataFrame([data])
            
            # 应用映射和清理
            if column_mapping:
                df = df.rename(columns={v: k for k, v in column_mapping.items()})
            df = self._smart_column_mapping(df)
            df = self._clean_flexible_data(df)
            
            return await self._process_dataframe(df, source=f"json_{file_path.stem}")
            
        except Exception as e:
            logger.error("JSON导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"JSON导入失败: {str(e)}")
    
    async def _import_pdf(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """导入PDF文档"""
        if not UNSTRUCTURED_AVAILABLE:
            raise ValidationException("PDF导入需要安装 unstructured 库")
        
        try:
            # 使用unstructured库解析PDF
            elements = partition_pdf(str(file_path))
            
            # 提取文本内容
            text_content = "\n".join([elem.text for elem in elements if hasattr(elem, 'text')])
            
            # 分析文档结构，尝试提取食谱信息
            recipes = self._extract_recipes_from_text(text_content, file_path.stem)
            
            return await self._process_recipe_list(recipes, source=f"pdf_{file_path.stem}")
            
        except Exception as e:
            logger.error("PDF导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"PDF导入失败: {str(e)}")
    
    async def _import_word(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """导入Word文档"""
        if not UNSTRUCTURED_AVAILABLE:
            raise ValidationException("Word导入需要安装 unstructured 库")
        
        try:
            # 使用unstructured库解析Word文档
            elements = partition_docx(str(file_path))
            
            # 提取文本内容
            text_content = "\n".join([elem.text for elem in elements if hasattr(elem, 'text')])
            
            # 分析文档结构，提取食谱信息
            recipes = self._extract_recipes_from_text(text_content, file_path.stem)
            
            return await self._process_recipe_list(recipes, source=f"word_{file_path.stem}")
            
        except Exception as e:
            logger.error("Word文档导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"Word文档导入失败: {str(e)}")
    
    async def _import_text(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """导入纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析文本结构，提取食谱信息
            recipes = self._extract_recipes_from_text(content, file_path.stem)
            
            return await self._process_recipe_list(recipes, source=f"text_{file_path.stem}")
            
        except Exception as e:
            logger.error("文本文件导入失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"文本文件导入失败: {str(e)}")
    
    async def _import_auto(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """使用unstructured库自动处理文件"""
        if not UNSTRUCTURED_AVAILABLE:
            raise ValidationException("自动文件处理需要安装 unstructured 库")
        
        try:
            # 自动识别和处理文件
            elements = partition(str(file_path))
            
            # 提取文本内容
            text_content = "\n".join([elem.text for elem in elements if hasattr(elem, 'text')])
            
            # 分析内容，提取食谱信息
            recipes = self._extract_recipes_from_text(text_content, file_path.stem)
            
            return await self._process_recipe_list(recipes, source=f"auto_{file_path.stem}")
            
        except Exception as e:
            logger.error("自动文件处理失败", error=str(e), file_path=str(file_path))
            raise ValidationException(f"自动文件处理失败: {str(e)}")
    
    def _extract_recipes_from_text(self, text: str, source_name: str) -> List[Dict[str, Any]]:
        """从文本中提取食谱信息"""
        recipes = []
        
        # 简单的食谱提取逻辑
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_recipe = {}
        for para in paragraphs:
            if self._looks_like_title(para):
                if current_recipe and 'title' in current_recipe:
                    recipes.append(current_recipe)
                current_recipe = {'title': para.strip()}
            elif self._looks_like_ingredients(para):
                current_recipe['ingredients'] = self._parse_ingredients_text(para)
            elif self._looks_like_directions(para):
                current_recipe['directions'] = self._parse_directions_text(para)
            else:
                # 其他内容作为描述
                if 'description' not in current_recipe:
                    current_recipe['description'] = para
                else:
                    current_recipe['description'] += ' ' + para
        
        # 添加最后一个食谱
        if current_recipe and 'title' in current_recipe:
            recipes.append(current_recipe)
        
        # 如果没有找到结构化食谱，将整个文本作为一个食谱
        if not recipes:
            recipes = [{
                'title': source_name or "提取的食谱",
                'description': text[:500] + "..." if len(text) > 500 else text,
                'content': text
            }]
        
        return recipes
    
    def _looks_like_title(self, text: str) -> bool:
        """判断文本是否像标题"""
        return (len(text) < 100 and 
                not text.startswith(('•', '-', '1.', '2.')) and
                not any(keyword in text.lower() for keyword in ['食材', 'ingredients', '步骤', 'directions']))
    
    def _looks_like_ingredients(self, text: str) -> bool:
        """判断文本是否像食材列表"""
        return any(keyword in text.lower() for keyword in ['食材', 'ingredients', '材料', '配料'])
    
    def _looks_like_directions(self, text: str) -> bool:
        """判断文本是否像制作步骤"""
        return any(keyword in text.lower() for keyword in ['步骤', 'directions', '做法', '制作', 'instructions'])
    
    def _parse_ingredients_text(self, text: str) -> List[str]:
        """解析食材文本"""
        # 移除标题行
        lines = text.split('\n')
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['食材', 'ingredients']):
                # 移除编号和符号
                line = re.sub(r'^[\d\.\-•\*\s]+', '', line)
                if line:
                    ingredients.append(line)
        
        return ingredients
    
    def _parse_directions_text(self, text: str) -> List[str]:
        """解析制作步骤文本"""
        # 移除标题行
        lines = text.split('\n')
        directions = []
        
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['步骤', 'directions', '做法']):
                # 移除编号
                line = re.sub(r'^[\d\.\-•\*\s]+', '', line)
                if line:
                    directions.append(line)
        
        return directions
    
    def _clean_flexible_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """灵活的数据清理"""
        # 删除完全空的行
        df = df.dropna(how='all')
        
        # 确保有标题字段
        if 'title' not in df.columns:
            # 尝试使用第一个文本列作为标题
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                df['title'] = df[text_columns[0]]
        
        # 清理标题
        if 'title' in df.columns:
            df = df.dropna(subset=['title'])
            df['title'] = df['title'].astype(str).str.strip()
        
        return df
    
    async def _process_dataframe(self, df: pd.DataFrame, source: str) -> Dict[str, Any]:
        """处理DataFrame数据"""
        stats = {
            "total_processed": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "embeddings_generated": 0,
            "errors": []
        }
        
        recipes_for_embedding = []
        
        with SessionLocal() as db:
            for _, row in df.iterrows():
                stats["total_processed"] += 1
                
                try:
                    # 创建食谱数据
                    recipe_data = self._create_flexible_recipe_data(row, source)
                    recipe = Recipe(**recipe_data)
                    
                    db.add(recipe)
                    db.flush()
                    
                    # 准备向量嵌入
                    embedding_text = self._create_embedding_text(recipe_data)
                    recipes_for_embedding.append({
                        'id': recipe.id,
                        'text': embedding_text,
                        'metadata': {
                            'title': recipe.title,
                            'source': source,
                        }
                    })
                    
                    stats["successful_imports"] += 1
                    
                except Exception as e:
                    stats["failed_imports"] += 1
                    stats["errors"].append(f"导入失败: {str(e)}")
                    logger.error("导入记录失败", error=str(e))
            
            db.commit()
        
        # 生成向量嵌入
        if recipes_for_embedding:
            try:
                await self._generate_embeddings_flexible(recipes_for_embedding)
                stats["embeddings_generated"] = len(recipes_for_embedding)
            except Exception as e:
                stats["errors"].append(f"向量嵌入生成失败: {str(e)}")
        
        return stats
    
    async def _process_recipe_list(self, recipes: List[Dict], source: str) -> Dict[str, Any]:
        """处理食谱列表"""
        df = pd.DataFrame(recipes)
        return await self._process_dataframe(df, source)
    
    def _create_flexible_recipe_data(self, row: pd.Series, source: str) -> Dict[str, Any]:
        """灵活创建食谱数据"""
        # 基本字段映射
        title = str(row.get('title', 'Unknown Recipe'))
        description = str(row.get('description', ''))
        
        # 处理食材
        ingredients = row.get('ingredients', [])
        if isinstance(ingredients, str):
            if ingredients.startswith('['):
                try:
                    ingredients = json.loads(ingredients)
                except:
                    ingredients = [ing.strip() for ing in ingredients.split(',')]
            else:
                ingredients = [ing.strip() for ing in ingredients.split(',')]
        elif not isinstance(ingredients, list):
            ingredients = []
        
        # 处理步骤
        directions = row.get('directions', [])
        if isinstance(directions, str):
            if directions.startswith('['):
                try:
                    directions = json.loads(directions)
                except:
                    directions = [directions]
            else:
                directions = [directions]
        elif not isinstance(directions, list):
            directions = []
        
        return {
            'title': title,
            'description': description,
            'ingredients': ingredients,
            'directions': directions,
            'calories': self._safe_numeric(row.get('calories')),
            'protein': self._safe_numeric(row.get('protein')),
            'fat': self._safe_numeric(row.get('fat')),
            'sodium': self._safe_numeric(row.get('sodium')),
            'rating': self._safe_numeric(row.get('rating')),
            'cooking_time': self._safe_numeric(row.get('cooking_time')),
            'difficulty': str(row.get('difficulty', '')),
            'category': str(row.get('category', '')),
            'source': source,
            'is_public': True,
            'is_verified': False,
        }
    
    def _safe_numeric(self, value) -> Optional[float]:
        """安全的数值转换"""
        if pd.isna(value) or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    # 批量导入功能
    async def import_directory(
        self, 
        directory_path: str, 
        pattern: str = "*", 
        **kwargs
    ) -> Dict[str, Any]:
        """批量导入目录中的文件"""
        directory = Path(directory_path)
        results = []
        
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    result = await self.import_file(file_path, **kwargs)
                    results.append({"file": str(file_path), "result": result})
                except Exception as e:
                    results.append({"file": str(file_path), "error": str(e)})
        
        return {
            "total_files": len(results),
            "results": results
        }