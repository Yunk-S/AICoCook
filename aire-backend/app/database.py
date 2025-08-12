"""
数据库连接和会话管理

配置 SQLAlchemy 数据库连接，包括连接池、会话管理等。
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

# 创建数据库引擎
if settings.is_testing:
    # 测试环境使用内存数据库或测试数据库
    DATABASE_URL = settings.DATABASE_TEST_URL or "sqlite:///./test.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
        echo=settings.DEBUG,
    )
else:
    # 生产/开发环境使用 PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    
    这个函数将被用作 FastAPI 的依赖注入，确保每个请求都有一个独立的数据库会话，
    并在请求结束后正确关闭会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    
    创建所有表格（如果不存在的话）
    """
    # 导入所有模型，确保它们被注册到 Base.metadata
    from app.models import user, recipe, diet_profile, meal_plan  # noqa
    
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    删除所有数据库表（主要用于测试）
    """
    Base.metadata.drop_all(bind=engine)