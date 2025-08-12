"""
用户模型

定义用户相关的数据库模型。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .diet_profile import UserDietProfile
    from .meal_plan import MealPlan
    from .recipe import UserRecipe


class User(Base):
    """
    用户模型
    """
    
    __tablename__ = "users"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 个人信息
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # 状态字段
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 用户偏好设置
    language = Column(String(10), default="zh-CN")
    timezone = Column(String(50), default="Asia/Shanghai")
    
    # 关联关系
    diet_profiles = relationship("UserDietProfile", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    user_recipes = relationship("UserRecipe", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def is_authenticated(self) -> bool:
        """用户是否已认证"""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """用户是否匿名"""
        return False