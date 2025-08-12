"""
饮食档案数据模式

定义饮食档案相关的 API 请求和响应数据结构。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class DietProfileBase(BaseModel):
    """饮食档案基础模式"""
    name: str = Field(..., min_length=1, max_length=100)
    name_zh: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    description_zh: str = Field(..., min_length=1, max_length=1000)
    
    # 饮食配置
    restrictions: List[str] = []
    excluded_ingredients: List[str] = []
    preferences: List[str] = []
    
    # 营养目标
    nutrition_goals: Optional[Dict[str, Any]] = None
    
    # 状态
    is_active: bool = True


class DietProfileCreate(DietProfileBase):
    """创建饮食档案请求模式"""
    pass


class DietProfileUpdate(BaseModel):
    """更新饮食档案请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    description_zh: Optional[str] = Field(None, min_length=1, max_length=1000)
    
    # 饮食配置
    restrictions: Optional[List[str]] = None
    excluded_ingredients: Optional[List[str]] = None
    preferences: Optional[List[str]] = None
    
    # 营养目标
    nutrition_goals: Optional[Dict[str, Any]] = None
    
    # 状态
    is_active: Optional[bool] = None


class DietProfileInDB(DietProfileBase):
    """数据库中的饮食档案模式"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DietProfileResponse(DietProfileInDB):
    """饮食档案响应模式"""
    pass


# 用户饮食档案相关模式
class UserDietProfileBase(BaseModel):
    """用户饮食档案基础模式"""
    # 个性化配置
    custom_restrictions: List[str] = []
    custom_excluded_ingredients: List[str] = []
    custom_preferences: List[str] = []
    
    # 个人信息
    allergies: List[str] = []
    medical_conditions: List[str] = []
    
    # 营养目标
    daily_calories: Optional[int] = Field(None, ge=500, le=5000)
    nutrition_goals: Optional[Dict[str, Any]] = None
    
    # 状态
    is_primary: bool = False
    is_active: bool = True


class UserDietProfileCreate(UserDietProfileBase):
    """创建用户饮食档案请求模式"""
    diet_profile_id: int = Field(..., gt=0)


class UserDietProfileUpdate(BaseModel):
    """更新用户饮食档案请求模式"""
    # 个性化配置
    custom_restrictions: Optional[List[str]] = None
    custom_excluded_ingredients: Optional[List[str]] = None
    custom_preferences: Optional[List[str]] = None
    
    # 个人信息
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    
    # 营养目标
    daily_calories: Optional[int] = Field(None, ge=500, le=5000)
    nutrition_goals: Optional[Dict[str, Any]] = None
    
    # 状态
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class UserDietProfileInDB(UserDietProfileBase):
    """数据库中的用户饮食档案模式"""
    id: int
    user_id: int
    diet_profile_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDietProfileResponse(UserDietProfileInDB):
    """用户饮食档案响应模式"""
    diet_profile: Optional[DietProfileResponse] = None
    combined_restrictions: List[str] = []
    combined_excluded_ingredients: List[str] = []
    combined_preferences: List[str] = []