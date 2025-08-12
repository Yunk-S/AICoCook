"""
食谱服务

提供食谱相关的业务逻辑处理。
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import structlog

from app.models.recipe import Recipe
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeSearch, 
    RecipeSearchResult, RecipeFilter
)

logger = structlog.get_logger()


class RecipeService:
    """食谱服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """根据ID获取食谱"""
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    def get_recipes(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[Recipe]:
        """获取食谱列表"""
        query = self.db.query(Recipe).filter(Recipe.is_public == True)
        
        if search:
            search_filter = or_(
                Recipe.title.contains(search),
                Recipe.title_zh.contains(search),
                Recipe.description.contains(search),
                Recipe.description_zh.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()
    
    def search_recipes(self, search_params: RecipeSearch) -> RecipeSearchResult:
        """搜索食谱"""
        query = self.db.query(Recipe).filter(Recipe.is_public == True)
        
        # 应用搜索条件
        if search_params.query:
            search_filter = or_(
                Recipe.title.contains(search_params.query),
                Recipe.title_zh.contains(search_params.query),
                Recipe.description.contains(search_params.query),
                Recipe.description_zh.contains(search_params.query)
            )
            query = query.filter(search_filter)
        
        if search_params.cuisine:
            query = query.filter(Recipe.cuisine == search_params.cuisine)
        
        if search_params.difficulty:
            query = query.filter(Recipe.difficulty == search_params.difficulty)
        
        if search_params.max_total_time:
            query = query.filter(Recipe.total_time <= search_params.max_total_time)
        
        if search_params.max_calories:
            query = query.filter(Recipe.calories <= search_params.max_calories)
        
        # 计算总数
        total = query.count()
        
        # 分页
        skip = (search_params.page - 1) * search_params.size
        recipes = query.offset(skip).limit(search_params.size).all()
        
        # 计算页数
        pages = (total + search_params.size - 1) // search_params.size
        
        return RecipeSearchResult(
            recipes=recipes,
            total=total,
            page=search_params.page,
            size=search_params.size,
            pages=pages
        )
    
    def create_recipe(self, recipe_create: RecipeCreate) -> Recipe:
        """创建新食谱"""
        # 创建食谱对象
        db_recipe = Recipe(
            title=recipe_create.title,
            title_zh=recipe_create.title_zh,
            description=recipe_create.description,
            description_zh=recipe_create.description_zh,
            ingredients=recipe_create.ingredients,
            directions=recipe_create.directions,
            calories=recipe_create.calories,
            protein=recipe_create.protein,
            fat=recipe_create.fat,
            carbohydrates=recipe_create.carbohydrates,
            fiber=recipe_create.fiber,
            sodium=recipe_create.sodium,
            prep_time=recipe_create.prep_time,
            cook_time=recipe_create.cook_time,
            total_time=recipe_create.total_time,
            servings=recipe_create.servings,
            difficulty=recipe_create.difficulty,
            cuisine=recipe_create.cuisine,
            tags=recipe_create.tags,
            is_public=True,
            view_count=0,
            rating_count=0
        )
        
        # 保存到数据库
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        
        logger.info("Recipe created", recipe_id=db_recipe.id, title=db_recipe.title)
        return db_recipe
    
    def update_recipe(self, recipe_id: int, recipe_update: RecipeUpdate) -> Optional[Recipe]:
        """更新食谱信息"""
        db_recipe = self.get_recipe(recipe_id)
        if not db_recipe:
            return None
        
        # 更新字段
        update_data = recipe_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_recipe, field, value)
        
        self.db.commit()
        self.db.refresh(db_recipe)
        
        logger.info("Recipe updated", recipe_id=recipe_id)
        return db_recipe
    
    def delete_recipe(self, recipe_id: int) -> bool:
        """删除食谱"""
        db_recipe = self.get_recipe(recipe_id)
        if not db_recipe:
            return False
        
        self.db.delete(db_recipe)
        self.db.commit()
        
        logger.info("Recipe deleted", recipe_id=recipe_id)
        return True
    
    def increment_view_count(self, recipe_id: int) -> bool:
        """增加查看次数"""
        db_recipe = self.get_recipe(recipe_id)
        if not db_recipe:
            return False
        
        db_recipe.view_count += 1
        self.db.commit()
        
        return True
    
    def rate_recipe(self, recipe_id: int, user_id: int, rating: float) -> bool:
        """给食谱评分（简化实现）"""
        db_recipe = self.get_recipe(recipe_id)
        if not db_recipe:
            return False
        
        # 简化实现：直接更新平均评分
        # 实际应用中需要创建评分表来存储每个用户的评分
        if db_recipe.rating_avg is None:
            db_recipe.rating_avg = rating
            db_recipe.rating_count = 1
        else:
            total_rating = db_recipe.rating_avg * db_recipe.rating_count
            db_recipe.rating_count += 1
            db_recipe.rating_avg = (total_rating + rating) / db_recipe.rating_count
        
        self.db.commit()
        
        logger.info("Recipe rated", recipe_id=recipe_id, user_id=user_id, rating=rating)
        return True
    
    def get_available_cuisines(self) -> List[str]:
        """获取所有可用的菜系"""
        result = self.db.query(Recipe.cuisine).filter(
            Recipe.cuisine.isnot(None),
            Recipe.is_public == True
        ).distinct().all()
        
        return [cuisine for (cuisine,) in result if cuisine]
    
    def get_available_tags(self) -> List[str]:
        """获取所有可用的标签"""
        # 简化实现：返回常见标签
        # 实际应用中需要解析所有食谱的tags字段
        return [
            "快手菜", "家常菜", "健康食谱", "减脂餐", 
            "素食", "高蛋白", "低卡路里", "儿童餐",
            "孕妇食谱", "老人食谱", "下饭菜", "汤羹"
        ]
    
    def recommend_recipes(
        self, 
        filter_params: RecipeFilter,
        user=None,
        limit: int = 10
    ) -> List[Recipe]:
        """推荐食谱"""
        query = self.db.query(Recipe).filter(Recipe.is_public == True)
        
        # 应用筛选条件
        if filter_params.cuisine:
            query = query.filter(Recipe.cuisine.in_(filter_params.cuisine))
        
        if filter_params.difficulty:
            query = query.filter(Recipe.difficulty.in_(filter_params.difficulty))
        
        if filter_params.max_time:
            query = query.filter(Recipe.total_time <= filter_params.max_time)
        
        if filter_params.max_calories:
            query = query.filter(Recipe.calories <= filter_params.max_calories)
        
        # 简化推荐：按评分和查看次数排序
        query = query.order_by(
            Recipe.rating_avg.desc().nullslast(),
            Recipe.view_count.desc()
        )
        
        return query.limit(limit).all()
    
    def import_recipes_from_csv(self, csv_path: str, overwrite: bool = False) -> dict:
        """从CSV文件导入食谱（简化实现）"""
        # 这是一个占位符实现
        # 实际应用中需要解析CSV文件并批量插入数据库
        
        logger.info("Recipe import requested", csv_path=csv_path, overwrite=overwrite)
        
        return {
            "message": "CSV导入功能正在开发中",
            "imported_count": 0,
            "skipped_count": 0,
            "error_count": 0
        }