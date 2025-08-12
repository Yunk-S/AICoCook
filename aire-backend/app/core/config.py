"""
应用配置管理

使用 Pydantic Settings 管理环境变量和应用配置。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator


class Settings(BaseModel):
    """应用设置"""
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # 基础配置
    PROJECT_NAME: str = "AI Meal Coach"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # 数据库配置 - 动态计算绝对路径，保持可移植性
    @property 
    def DATABASE_URL(self) -> str:
        """动态计算数据库路径，基于当前文件位置"""
        # 获取当前文件的绝对路径 (aire-backend/app/core/config.py)
        current_file = Path(__file__).resolve()
        # 从当前文件向上找到 aire-backend 目录，然后找到项目根目录
        aire_backend_dir = current_file.parent.parent.parent  # 向上3级到aire-backend
        project_root = aire_backend_dir.parent  # 再向上1级到项目根目录
        
        # 构建数据库文件的绝对路径
        db_path = project_root / "data" / "aire_local.db"
        
        # 确保路径存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 返回SQLite URL格式的绝对路径
        return f"sqlite:///{db_path}"
    DATABASE_TEST_URL: Optional[str] = None

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TEST_URL: Optional[str] = None

    # AI 服务配置
    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: Optional[str] = None
    DOUBAO_API_KEY: Optional[str] = None
    ZHIPU_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEFAULT_AI_API_KEY: str = ""  # 默认AI API密钥，用于向量生成
    
    # 嵌入向量服务配置
    EMBEDDING_PROVIDER: str = "google"  # google, openai, doubao, zhipu, deepseek
    EMBEDDING_MODEL: str = "models/embedding-001"  # 默认嵌入模型
    EMBEDDING_BATCH_SIZE: int = 100  # 批量处理大小
    EMBEDDING_DIMENSION: int = 768  # 嵌入向量维度
    
    # 各服务商的嵌入模型配置
    GOOGLE_EMBEDDING_MODEL: str = "models/embedding-001"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"  # 更新为最新模型
    DOUBAO_EMBEDDING_MODEL: str = "text-embedding-3-small"  # 使用OpenAI兼容接口
    ZHIPU_EMBEDDING_MODEL: str = "embedding-2"
    DEEPSEEK_EMBEDDING_MODEL: str = "text-embedding-3-small"  # DeepSeek使用OpenAI兼容接口

    # 向量数据库配置
    VECTOR_DB_TYPE: str = "faiss"  # faiss, pinecone, weaviate
    EMBEDDINGS_DIR: str = "./data/embeddings"  # 向量嵌入存储目录
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    WEAVIATE_URL: Optional[str] = None
    WEAVIATE_API_KEY: Optional[str] = None

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"  # 主密钥
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"  # JWT算法
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件存储配置
    UPLOAD_DIR: str = "./data/uploads"
    EMBEDDINGS_DIR: str = "./data/embeddings"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AWS S3 配置
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # 缓存配置
    CACHE_TTL: int = 3600  # 1 hour
    EMBEDDING_CACHE_TTL: int = 86400  # 24 hours
    
    # 数据导入配置
    AUTO_IMPORT_ON_STARTUP: bool = True  # 是否在启动时自动导入数据
    AUTO_IMPORT_LIMIT: Optional[int] = None  # 启动时导入数量限制，None为全部导入
    AUTO_GENERATE_EMBEDDINGS: bool = False  # 启动时是否生成向量嵌入

    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "./logs/app.log"

    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None

    # 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None

    # Celery 配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_TEST_URL", mode="before")
    @classmethod
    def assemble_test_db_url(cls, v: Optional[str]) -> str:
        if v:
            return v
        # 注意：在Pydantic v2中，我们不能直接访问其他字段的值
        # 这个逻辑需要在应用初始化时处理
        return ""

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod  
    def assemble_celery_broker_url(cls, v: Optional[str]) -> str:
        # 如果没有设置，将在初始化后使用REDIS_URL填充
        return v or ""

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_result_backend(cls, v: Optional[str]) -> str:
        # 如果没有设置，将在初始化后使用REDIS_URL填充
        return v or ""

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.ENVIRONMENT.lower() == "testing"
    
    def get_embedding_api_key(self, provider: Optional[str] = None) -> str:
        """
        根据嵌入服务提供商获取对应的API密钥
        
        Args:
            provider: 服务提供商，如不指定则使用EMBEDDING_PROVIDER
            
        Returns:
            API密钥字符串
        """
        if provider is None:
            provider = self.EMBEDDING_PROVIDER
        
        provider = provider.lower()
        
        # 首先尝试使用默认API密钥
        if self.DEFAULT_AI_API_KEY:
            return self.DEFAULT_AI_API_KEY
            
        # 根据服务商返回对应的API密钥
        if provider == "google":
            return self.GOOGLE_API_KEY
        elif provider == "openai":
            return self.OPENAI_API_KEY or ""
        elif provider == "doubao":
            return self.DOUBAO_API_KEY or ""
        elif provider == "zhipu":
            return self.ZHIPU_API_KEY or ""
        elif provider == "deepseek":
            return self.DEEPSEEK_API_KEY or ""
        else:
            # 如果不支持的提供商，返回默认密钥
            return self.DEFAULT_AI_API_KEY
    
    def get_embedding_model(self, provider: Optional[str] = None) -> str:
        """
        根据嵌入服务提供商获取对应的模型名称
        
        Args:
            provider: 服务提供商，如不指定则使用EMBEDDING_PROVIDER
            
        Returns:
            模型名称字符串
        """
        if provider is None:
            provider = self.EMBEDDING_PROVIDER
        
        provider = provider.lower()
        
        if provider == "google":
            return self.GOOGLE_EMBEDDING_MODEL
        elif provider == "openai":
            return self.OPENAI_EMBEDDING_MODEL
        elif provider == "doubao":
            return self.DOUBAO_EMBEDDING_MODEL
        elif provider == "zhipu":
            return self.ZHIPU_EMBEDDING_MODEL
        elif provider == "deepseek":
            return self.DEEPSEEK_EMBEDDING_MODEL
        else:
            # 默认返回通用嵌入模型
            return self.EMBEDDING_MODEL
    
    def get_supported_embedding_providers(self) -> List[str]:
        """获取支持的嵌入服务提供商列表"""
        return ["google", "openai", "doubao", "zhipu", "deepseek"]
    
    def model_post_init(self, __context):
        """模型初始化后的处理"""
        # 处理依赖字段的默认值
        if not self.DATABASE_TEST_URL and self.DATABASE_URL:
            object.__setattr__(self, 'DATABASE_TEST_URL', 
                               self.DATABASE_URL.replace("/aire_db", "/aire_test_db"))
        
        if not self.CELERY_BROKER_URL and self.REDIS_URL:
            object.__setattr__(self, 'CELERY_BROKER_URL', self.REDIS_URL)
            
        if not self.CELERY_RESULT_BACKEND and self.REDIS_URL:
            object.__setattr__(self, 'CELERY_RESULT_BACKEND', self.REDIS_URL)
    
    # @field_validator("JWT_SECRET_KEY")
    # @classmethod
    # def validate_jwt_secret_key(cls, v: str) -> str:
    #     """验证JWT密钥"""
    #     if v == "your-secret-key-change-in-production":
    #         raise ValueError("请更改默认的JWT密钥")
    #     if len(v) < 32:
    #         raise ValueError("JWT密钥长度应至少为32个字符")
    #     return v

# 配置已移至 model_config


# 创建全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取应用设置"""
    return settings