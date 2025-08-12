"""
食谱数据模式

定义食谱相关的 API 请求和响应数据结构。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    """食谱基础模式"""
    title: str = Field(..., min_length=1, max_length=255)
    title_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    ingredients: List[str] = Field(..., min_items=1)
    directions: List[str] = Field(..., min_items=1)
    
    # 营养信息
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    
    # 时间信息
    prep_time: Optional[int] = Field(None, ge=0)  # 分钟
    cook_time: Optional[int] = Field(None, ge=0)  # 分钟
    total_time: Optional[int] = Field(None, ge=0)  # 分钟
    
    # 其他信息
    servings: int = Field(1, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    cuisine: Optional[str] = None
    tags: List[str] = []


class RecipeCreate(RecipeBase):
    """创建食谱请求模式"""
    pass


class RecipeUpdate(BaseModel):
    """更新食谱请求模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    title_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    ingredients: Optional[List[str]] = Field(None, min_items=1)
    directions: Optional[List[str]] = Field(None, min_items=1)
    
    # 营养信息
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    
    # 时间信息
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    total_time: Optional[int] = Field(None, ge=0)
    
    # 其他信息
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    cuisine: Optional[str] = None
    tags: Optional[List[str]] = None


class RecipeInDB(RecipeBase):
    """数据库中的食谱模式"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_public: bool = True
    view_count: int = 0
    rating_avg: Optional[float] = None
    rating_count: int = 0

    class Config:
        from_attributes = True


class RecipeResponse(RecipeInDB):
    """食谱响应模式"""
    pass


class RecipeSearch(BaseModel):
    """食谱搜索请求模式"""
    query: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    max_prep_time: Optional[int] = Field(None, ge=0)
    max_cook_time: Optional[int] = Field(None, ge=0)
    max_total_time: Optional[int] = Field(None, ge=0)
    max_calories: Optional[float] = Field(None, ge=0)
    ingredients: Optional[List[str]] = None
    exclude_ingredients: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    # 分页
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class RecipeSearchResult(BaseModel):
    """食谱搜索结果模式"""
    recipes: List[RecipeResponse]
    total: int
    page: int
    size: int
    pages: int


class RecipeFilter(BaseModel):
    """食谱筛选模式"""
    cuisine: Optional[List[str]] = None
    difficulty: Optional[List[str]] = None
    max_time: Optional[int] = None
    max_calories: Optional[float] = None
    dietary_restrictions: Optional[List[str]] = None
    available_ingredients: Optional[List[str]] = None