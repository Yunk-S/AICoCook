"""
用户相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    language: str = Field("zh-CN", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    timezone: str = Field("Asia/Shanghai", max_length=50)


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with underscores and hyphens allowed)')
        return v


class UserRegister(UserCreate):
    """用户注册模式"""
    accept_terms: bool = Field(..., description="Must accept terms and conditions")
    
    @validator('accept_terms')
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError('Must accept terms and conditions')
        return v


class UserLogin(BaseModel):
    """用户登录模式"""
    username_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    remember_me: bool = False


class UserUpdate(BaseModel):
    """用户更新模式"""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, pattern=r"^[a-z]{2}-[A-Z]{2}$")
    timezone: Optional[str] = Field(None, max_length=50)


class UserPasswordUpdate(BaseModel):
    """用户密码更新模式"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    language: str
    timezone: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """用户公开资料模式"""
    id: int
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token 模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token 数据模式"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    scopes: list[str] = []


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求模式"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """密码重置请求模式"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """密码重置确认模式"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求模式"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """邮箱验证确认模式"""
    token: str


class UserStats(BaseModel):
    """用户统计信息模式"""
    total_recipes: int
    favorite_recipes: int
    meal_plans: int
    active_meal_plans: int
    recipes_made: int
    
    class Config:
        from_attributes = True