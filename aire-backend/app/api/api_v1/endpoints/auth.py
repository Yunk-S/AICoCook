"""
认证授权 API 端点

提供用户注册、登录、token验证等认证功能。
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户注册
    
    创建新用户账户。
    """
    user_service = UserService(db)
    
    # 检查邮箱是否已存在
    if user_service.get_user_by_email(user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查用户名是否已存在
    if user_service.get_user_by_username(user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )
    
    # 创建用户
    user = user_service.create_user(user_create)
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    用户登录
    
    验证用户凭据并返回访问令牌。
    """
    user_service = UserService(db)
    
    # 验证用户（支持邮箱或用户名登录）
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }


@router.post("/login/email", response_model=Token, summary="邮箱登录")
async def login_with_email(
    user_login: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    邮箱登录
    
    使用邮箱和密码进行登录。
    """
    user_service = UserService(db)
    
    # 验证用户
    user = user_service.authenticate_user(user_login.email, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }


@router.post("/refresh", response_model=Token, summary="刷新令牌")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    刷新访问令牌
    
    为当前用户生成新的访问令牌。
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": current_user
    }


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    用户登出
    
    注：由于JWT是无状态的，这里主要是告知客户端删除令牌。
    在生产环境中，可以将令牌加入黑名单。
    """
    return {"message": "成功登出，请删除本地存储的令牌"}


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息
    
    返回当前登录用户的详细信息。
    """
    return current_user


# 需要先创建依赖函数，这里先导入
from app.dependencies import get_current_user