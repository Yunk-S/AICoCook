"""
食谱模型

定义食谱相关的数据库模型。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, Table, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .user import User
    from .meal_plan import MealPlanRecipe


# 食谱和分类的多对多关联表
recipe_category_association = Table(
    'recipe_category_association',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('category_id', Integer, ForeignKey('recipe_categories.id'))
)


class Recipe(Base):
    """
    食谱模型
    """
    
    __tablename__ = "recipes"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    title_zh = Column(String(255), nullable=True)  # 中文标题
    description = Column(Text, nullable=True)
    description_zh = Column(Text, nullable=True)  # 中文描述
    
    # 食谱内容
    ingredients = Column(JSON, nullable=False)  # 食材列表
    directions = Column(JSON, nullable=False)  # 制作步骤
    
    # 营养信息
    calories = Column(Float, nullable=True)  # 卡路里
    protein = Column(Float, nullable=True)  # 蛋白质 (g)
    fat = Column(Float, nullable=True)  # 脂肪 (g)
    carbohydrates = Column(Float, nullable=True)  # 碳水化合物 (g)
    fiber = Column(Float, nullable=True)  # 纤维 (g)
    sodium = Column(Float, nullable=True)  # 钠 (mg)
    
    # 时间信息
    prep_time = Column(Integer, nullable=True)  # 准备时间（分钟）
    cook_time = Column(Integer, nullable=True)  # 烹饪时间（分钟）
    total_time = Column(Integer, nullable=True)  # 总时间（分钟）
    
    # 其他信息
    servings = Column(Integer, nullable=False, default=1)  # 份数
    difficulty = Column(String(20), nullable=True)  # 难度：easy, medium, hard
    rating = Column(Float, nullable=True)  # 评分 (1-5)
    
    # 图片和媒体
    image_url = Column(String(500), nullable=True)
    images = Column(JSON, nullable=True, default=list)  # 多张图片
    
    # 来源信息
    source = Column(String(100), nullable=True)  # 来源：epicurious, user_generated, etc.
    source_url = Column(String(500), nullable=True)  # 原始链接
    
    # 向量化信息
    embedding_vector = Column(JSON, nullable=True)  # 向量嵌入
    text_for_embedding = Column(Text, nullable=True)  # 用于向量化的文本
    
    # 状态
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 是否经过验证
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    categories = relationship(
        "RecipeCategory",
        secondary=recipe_category_association,
        back_populates="recipes"
    )
    ingredients_detail = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    user_recipes = relationship("UserRecipe", back_populates="recipe")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="recipe")
    
    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title='{self.title}')>"
    
    @property
    def total_nutrition(self) -> dict:
        """获取总营养信息"""
        return {
            "calories": self.calories or 0,
            "protein": self.protein or 0,
            "fat": self.fat or 0,
            "carbohydrates": self.carbohydrates or 0,
            "fiber": self.fiber or 0,
            "sodium": self.sodium or 0,
        }


class RecipeCategory(Base):
    """
    食谱分类模型
    """
    
    __tablename__ = "recipe_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_zh = Column(String(100), nullable=True)  # 中文名称
    description = Column(Text, nullable=True)
    description_zh = Column(Text, nullable=True)  # 中文描述
    
    # 分类层级
    parent_id = Column(Integer, ForeignKey("recipe_categories.id"), nullable=True)
    level = Column(Integer, default=0)  # 层级深度
    
    # 显示信息
    icon = Column(String(100), nullable=True)  # 图标
    color = Column(String(20), nullable=True)  # 颜色
    sort_order = Column(Integer, default=0)  # 排序
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    recipes = relationship(
        "Recipe",
        secondary=recipe_category_association,
        back_populates="categories"
    )
    parent = relationship("RecipeCategory", remote_side=[id], back_populates="children")
    children = relationship("RecipeCategory", back_populates="parent")
    
    def __repr__(self) -> str:
        return f"<RecipeCategory(id={self.id}, name='{self.name}')>"


class RecipeIngredient(Base):
    """
    食谱食材详情模型
    """
    
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    # 食材信息
    name = Column(String(200), nullable=False)  # 食材名称
    name_zh = Column(String(200), nullable=True)  # 中文名称
    amount = Column(Float, nullable=True)  # 数量
    unit = Column(String(50), nullable=True)  # 单位
    notes = Column(String(500), nullable=True)  # 备注
    
    # 营养信息（可选）
    calories_per_unit = Column(Float, nullable=True)
    
    # 顺序
    order_index = Column(Integer, default=0)
    
    # 关联关系
    recipe = relationship("Recipe", back_populates="ingredients_detail")
    
    def __repr__(self) -> str:
        return f"<RecipeIngredient(id={self.id}, name='{self.name}', amount={self.amount}, unit='{self.unit}')>"


class UserRecipe(Base):
    """
    用户食谱关联模型
    
    记录用户与食谱的关系，包括收藏、评分、自定义等。
    """
    
    __tablename__ = "user_recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    # 用户操作
    is_favorite = Column(Boolean, default=False)  # 是否收藏
    user_rating = Column(Float, nullable=True)  # 用户评分 (1-5)
    user_notes = Column(Text, nullable=True)  # 用户备注
    
    # 自定义修改
    custom_servings = Column(Integer, nullable=True)  # 自定义份数
    custom_ingredients = Column(JSON, nullable=True)  # 自定义食材
    custom_directions = Column(JSON, nullable=True)  # 自定义步骤
    
    # 制作记录
    made_count = Column(Integer, default=0)  # 制作次数
    last_made_at = Column(DateTime(timezone=True), nullable=True)  # 最后制作时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="user_recipes")
    recipe = relationship("Recipe", back_populates="user_recipes")
    
    def __repr__(self) -> str:
        return f"<UserRecipe(id={self.id}, user_id={self.user_id}, recipe_id={self.recipe_id})>"