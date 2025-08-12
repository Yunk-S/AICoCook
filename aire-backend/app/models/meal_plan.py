"""
膳食计划模型

定义膳食计划相关的数据库模型。
"""

from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, Column, DateTime, Date, Float, ForeignKey, Integer, 
    String, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base

if TYPE_CHECKING:
    from .user import User
    from .recipe import Recipe


class MealType(enum.Enum):
    """餐次类型"""
    BREAKFAST = "breakfast"  # 早餐
    LUNCH = "lunch"  # 午餐
    DINNER = "dinner"  # 晚餐
    SNACK = "snack"  # 加餐/零食


class MealPlanStatus(enum.Enum):
    """膳食计划状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 活跃
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


class MealPlan(Base):
    """
    膳食计划模型
    """
    
    __tablename__ = "meal_plans"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 计划信息
    name = Column(String(255), nullable=False)  # 计划名称
    description = Column(Text, nullable=True)  # 计划描述
    
    # 时间范围
    start_date = Column(Date, nullable=False)  # 开始日期
    end_date = Column(Date, nullable=False)  # 结束日期
    
    # 目标设置
    target_calories = Column(Float, nullable=True)  # 目标卡路里
    target_protein = Column(Float, nullable=True)  # 目标蛋白质 (g)
    target_fat = Column(Float, nullable=True)  # 目标脂肪 (g)
    target_carbs = Column(Float, nullable=True)  # 目标碳水化合物 (g)
    
    # 计划配置
    meals_per_day = Column(Integer, default=3)  # 每日餐次数
    include_snacks = Column(Boolean, default=False)  # 是否包含零食
    
    # 生成设置
    generation_params = Column(JSON, nullable=True)  # AI 生成参数
    diet_profile_id = Column(Integer, nullable=True)  # 关联的饮食档案 ID
    
    # 状态
    status = Column(SQLEnum(MealPlanStatus), default=MealPlanStatus.DRAFT)
    is_template = Column(Boolean, default=False)  # 是否为模板
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 统计信息
    total_recipes = Column(Integer, default=0)  # 总食谱数
    completed_meals = Column(Integer, default=0)  # 已完成餐次
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="meal_plans")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<MealPlan(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @property
    def duration_days(self) -> int:
        """计划持续天数"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_current(self) -> bool:
        """是否为当前计划"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def progress_percentage(self) -> float:
        """完成进度百分比"""
        if self.total_recipes == 0:
            return 0.0
        return (self.completed_meals / self.total_recipes) * 100


class MealPlanRecipe(Base):
    """
    膳食计划食谱关联模型
    
    记录膳食计划中的具体食谱安排。
    """
    
    __tablename__ = "meal_plan_recipes"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    # 餐次信息
    meal_date = Column(Date, nullable=False)  # 用餐日期
    meal_type = Column(SQLEnum(MealType), nullable=False)  # 餐次类型
    meal_order = Column(Integer, default=0)  # 同一餐次内的顺序
    
    # 份量信息
    servings = Column(Float, default=1.0)  # 份数
    portion_multiplier = Column(Float, default=1.0)  # 份量倍数
    
    # 自定义信息
    custom_notes = Column(Text, nullable=True)  # 自定义备注
    substitutions = Column(JSON, nullable=True)  # 食材替换
    
    # 状态
    is_completed = Column(Boolean, default=False)  # 是否已完成
    is_skipped = Column(Boolean, default=False)  # 是否跳过
    
    # 完成信息
    completed_at = Column(DateTime(timezone=True), nullable=True)  # 完成时间
    actual_servings = Column(Float, nullable=True)  # 实际份数
    satisfaction_rating = Column(Float, nullable=True)  # 满意度评分 (1-5)
    feedback = Column(Text, nullable=True)  # 反馈
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    meal_plan = relationship("MealPlan", back_populates="meal_plan_recipes")
    recipe = relationship("Recipe", back_populates="meal_plan_recipes")
    
    def __repr__(self) -> str:
        return f"<MealPlanRecipe(id={self.id}, meal_plan_id={self.meal_plan_id}, recipe_id={self.recipe_id}, meal_type='{self.meal_type.value}')>"
    
    @property
    def calculated_nutrition(self) -> dict:
        """计算营养信息（考虑份量）"""
        if not self.recipe:
            return {}
        
        multiplier = self.servings * self.portion_multiplier
        
        return {
            "calories": (self.recipe.calories or 0) * multiplier,
            "protein": (self.recipe.protein or 0) * multiplier,
            "fat": (self.recipe.fat or 0) * multiplier,
            "carbohydrates": (self.recipe.carbohydrates or 0) * multiplier,
            "fiber": (self.recipe.fiber or 0) * multiplier,
            "sodium": (self.recipe.sodium or 0) * multiplier,
        }
    
    @property
    def meal_type_display(self) -> str:
        """餐次类型显示名称"""
        meal_type_names = {
            MealType.BREAKFAST: "早餐",
            MealType.LUNCH: "午餐", 
            MealType.DINNER: "晚餐",
            MealType.SNACK: "加餐"
        }
        return meal_type_names.get(self.meal_type, self.meal_type.value)