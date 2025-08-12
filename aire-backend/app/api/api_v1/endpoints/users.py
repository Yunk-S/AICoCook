"""
用户管理 API 端点

提供用户信息管理、资料更新等功能。
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取用户列表
    
    需要超级用户权限。
    """
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit, search=search)
    return users


@router.post("/", response_model=UserResponse, summary="创建用户")
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新用户
    
    需要超级用户权限。
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
    
    user = user_service.create_user(user_create)
    return user


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新当前用户信息
    """
    user_service = UserService(db)
    
    # 如果要更新邮箱，检查是否已存在
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_service.get_user_by_email(user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
            )
    
    # 如果要更新用户名，检查是否已存在
    if user_update.username and user_update.username != current_user.username:
        existing_user = user_service.get_user_by_username(user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被其他用户使用"
            )
    
    user = user_service.update_user(current_user.id, user_update)
    return user


@router.get("/{user_id}", response_model=UserResponse, summary="获取指定用户信息")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取指定用户信息
    
    普通用户只能查看自己的信息，超级用户可以查看任何用户的信息。
    """
    user_service = UserService(db)
    
    # 检查权限
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他用户的信息"
        )
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新指定用户信息")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新指定用户信息
    
    需要超级用户权限。
    """
    user_service = UserService(db)
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果要更新邮箱，检查是否已存在
    if user_update.email and user_update.email != user.email:
        existing_user = user_service.get_user_by_email(user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
            )
    
    # 如果要更新用户名，检查是否已存在
    if user_update.username and user_update.username != user.username:
        existing_user = user_service.get_user_by_username(user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被其他用户使用"
            )
    
    updated_user = user_service.update_user(user_id, user_update)
    return updated_user


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除用户
    
    需要超级用户权限。
    """
    user_service = UserService(db)
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除超级用户
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除超级用户"
        )
    
    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user_service.delete_user(user_id)
    return {"message": "用户已删除"}


@router.post("/{user_id}/activate", response_model=UserResponse, summary="激活用户")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    激活用户
    
    需要超级用户权限。
    """
    user_service = UserService(db)
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_update = UserUpdate(is_active=True)
    updated_user = user_service.update_user(user_id, user_update)
    return updated_user


@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="停用用户")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    停用用户
    
    需要超级用户权限。
    """
    user_service = UserService(db)
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许停用超级用户
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用超级用户"
        )
    
    # 不允许停用自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用自己"
        )
    
    user_update = UserUpdate(is_active=False)
    updated_user = user_service.update_user(user_id, user_update)
    return updated_user