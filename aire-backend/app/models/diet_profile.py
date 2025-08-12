"""
饮食档案模型

定义饮食档案相关的数据库模型。
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .user import User


class DietProfile(Base):
    """
    饮食档案模板
    
    预定义的饮食档案类型，如桥本氏病、糖尿病、素食等。
    """
    
    __tablename__ = "diet_profiles"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_zh = Column(String(100), nullable=False)  # 中文名称
    description = Column(Text, nullable=False)
    description_zh = Column(Text, nullable=False)  # 中文描述
    
    # 饮食配置
    restrictions = Column(JSON, nullable=False, default=list)  # 饮食限制
    excluded_ingredients = Column(JSON, nullable=False, default=list)  # 禁止食材
    preferences = Column(JSON, nullable=False, default=list)  # 饮食偏好
    
    # 营养目标
    nutrition_goals = Column(JSON, nullable=True)  # 营养目标
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user_profiles = relationship("UserDietProfile", back_populates="diet_profile")
    
    def __repr__(self) -> str:
        return f"<DietProfile(id={self.id}, name='{self.name}')>"


class UserDietProfile(Base):
    """
    用户饮食档案
    
    用户个性化的饮食档案，基于模板档案进行定制。
    """
    
    __tablename__ = "user_diet_profiles"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diet_profile_id = Column(Integer, ForeignKey("diet_profiles.id"), nullable=False)
    
    # 个性化配置
    custom_restrictions = Column(JSON, nullable=True, default=list)  # 自定义限制
    custom_excluded_ingredients = Column(JSON, nullable=True, default=list)  # 自定义禁止食材
    custom_preferences = Column(JSON, nullable=True, default=list)  # 自定义偏好
    
    # 个人信息
    allergies = Column(JSON, nullable=True, default=list)  # 过敏信息
    medical_conditions = Column(JSON, nullable=True, default=list)  # 健康状况
    
    # 营养目标
    daily_calories = Column(Integer, nullable=True)  # 每日卡路里目标
    nutrition_goals = Column(JSON, nullable=True)  # 营养目标
    
    # 状态
    is_primary = Column(Boolean, default=False)  # 是否为主要档案
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="diet_profiles")
    diet_profile = relationship("DietProfile", back_populates="user_profiles")
    
    def __repr__(self) -> str:
        return f"<UserDietProfile(id={self.id}, user_id={self.user_id}, diet_profile_id={self.diet_profile_id})>"
    
    @property
    def combined_restrictions(self) -> List[str]:
        """合并的饮食限制"""
        base_restrictions = self.diet_profile.restrictions if self.diet_profile else []
        custom_restrictions = self.custom_restrictions or []
        return list(set(base_restrictions + custom_restrictions))
    
    @property
    def combined_excluded_ingredients(self) -> List[str]:
        """合并的禁止食材"""
        base_excluded = self.diet_profile.excluded_ingredients if self.diet_profile else []
        custom_excluded = self.custom_excluded_ingredients or []
        return list(set(base_excluded + custom_excluded))
    
    @property
    def combined_preferences(self) -> List[str]:
        """合并的饮食偏好"""
        base_preferences = self.diet_profile.preferences if self.diet_profile else []
        custom_preferences = self.custom_preferences or []
        return list(set(base_preferences + custom_preferences))