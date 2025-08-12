"""
用户服务

提供用户相关的业务逻辑处理。
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import structlog

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

logger = structlog.get_logger()


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[User]:
        """获取用户列表"""
        query = self.db.query(User)
        
        if search:
            search_filter = or_(
                User.username.contains(search),
                User.email.contains(search),
                User.full_name.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建新用户"""
        # 创建用户对象
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
            is_active=True,
            is_verified=False,
            is_superuser=False
        )
        
        # 保存到数据库
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info("User created", user_id=db_user.id, username=db_user.username)
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        # 更新字段
        update_data = user_update.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info("User updated", user_id=user_id)
        return db_user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        
        logger.info("User deleted", user_id=user_id)
        return True
    
    def authenticate_user(self, email_or_username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        # 尝试通过邮箱或用户名查找用户
        user = self.get_user_by_email(email_or_username)
        if not user:
            user = self.get_user_by_username(email_or_username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def update_last_login(self, user_id: int) -> bool:
        """更新最后登录时间"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        db_user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        return True