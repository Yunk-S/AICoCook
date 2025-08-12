"""
膳食计划数据模式

定义膳食计划相关的 API 请求和响应数据结构。
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field

from .recipe import RecipeResponse


class MealTypeEnum(str, Enum):
    """餐次类型枚举"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealPlanStatusEnum(str, Enum):
    """膳食计划状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MealPlanBase(BaseModel):
    """膳食计划基础模式"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    start_date: date
    end_date: date
    
    # 目标设置
    target_calories: Optional[float] = Field(None, ge=0)
    target_protein: Optional[float] = Field(None, ge=0)
    target_fat: Optional[float] = Field(None, ge=0)
    target_carbs: Optional[float] = Field(None, ge=0)
    
    # 计划配置
    meals_per_day: int = Field(3, ge=1, le=6)
    include_snacks: bool = False
    
    # 生成设置
    generation_params: Optional[Dict[str, Any]] = None
    diet_profile_id: Optional[int] = None
    
    # 状态
    is_template: bool = False
    is_public: bool = False


class MealPlanCreate(MealPlanBase):
    """创建膳食计划请求模式"""
    pass


class MealPlanUpdate(BaseModel):
    """更新膳食计划请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # 目标设置
    target_calories: Optional[float] = Field(None, ge=0)
    target_protein: Optional[float] = Field(None, ge=0)
    target_fat: Optional[float] = Field(None, ge=0)
    target_carbs: Optional[float] = Field(None, ge=0)
    
    # 计划配置
    meals_per_day: Optional[int] = Field(None, ge=1, le=6)
    include_snacks: Optional[bool] = None
    
    # 生成设置
    generation_params: Optional[Dict[str, Any]] = None
    diet_profile_id: Optional[int] = None
    
    # 状态
    status: Optional[MealPlanStatusEnum] = None
    is_template: Optional[bool] = None
    is_public: Optional[bool] = None


class MealPlanInDB(MealPlanBase):
    """数据库中的膳食计划模式"""
    id: int
    user_id: int
    status: MealPlanStatusEnum = MealPlanStatusEnum.DRAFT
    total_recipes: int = 0
    completed_meals: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MealPlanResponse(MealPlanInDB):
    """膳食计划响应模式"""
    progress_percentage: Optional[float] = None


# 膳食计划食谱相关模式
class MealPlanRecipeBase(BaseModel):
    """膳食计划食谱基础模式"""
    meal_date: date
    meal_type: MealTypeEnum
    meal_order: int = Field(0, ge=0)
    servings: float = Field(1.0, gt=0)
    portion_multiplier: float = Field(1.0, gt=0)
    custom_notes: Optional[str] = Field(None, max_length=500)
    substitutions: Optional[Dict[str, Any]] = None


class MealPlanRecipeCreate(MealPlanRecipeBase):
    """创建膳食计划食谱请求模式"""
    recipe_id: int = Field(..., gt=0)


class MealPlanRecipeUpdate(BaseModel):
    """更新膳食计划食谱请求模式"""
    meal_date: Optional[date] = None
    meal_type: Optional[MealTypeEnum] = None
    meal_order: Optional[int] = Field(None, ge=0)
    servings: Optional[float] = Field(None, gt=0)
    portion_multiplier: Optional[float] = Field(None, gt=0)
    custom_notes: Optional[str] = Field(None, max_length=500)
    substitutions: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None
    is_skipped: Optional[bool] = None
    actual_servings: Optional[float] = Field(None, gt=0)
    satisfaction_rating: Optional[float] = Field(None, ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=500)


class MealPlanRecipeInDB(MealPlanRecipeBase):
    """数据库中的膳食计划食谱模式"""
    id: int
    meal_plan_id: int
    recipe_id: int
    is_completed: bool = False
    is_skipped: bool = False
    completed_at: Optional[datetime] = None
    actual_servings: Optional[float] = None
    satisfaction_rating: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MealPlanRecipeResponse(MealPlanRecipeInDB):
    """膳食计划食谱响应模式"""
    recipe: Optional[RecipeResponse] = None
    calculated_nutrition: Optional[Dict[str, float]] = None


# 膳食计划详细信息
class MealPlanDetail(MealPlanResponse):
    """膳食计划详细信息模式"""
    meal_plan_recipes: List[MealPlanRecipeResponse] = []


# 膳食计划生成请求
class MealPlanGenerateRequest(BaseModel):
    """膳食计划生成请求模式"""
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date
    target_calories: Optional[float] = Field(None, ge=0)
    diet_profile_id: Optional[int] = None
    cuisine_preferences: List[str] = []
    excluded_ingredients: List[str] = []
    meal_types: List[MealTypeEnum] = [MealTypeEnum.BREAKFAST, MealTypeEnum.LUNCH, MealTypeEnum.DINNER]
    include_snacks: bool = False