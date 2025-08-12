"""
日志配置模块

配置结构化日志，支持不同环境的日志格式和级别。
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    设置结构化日志
    """
    # 确保日志目录存在
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # 配置处理器
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="ISO"),
    ]
    
    if settings.LOG_FORMAT.lower() == "json":
        # JSON 格式（适用于生产环境）
        processors.append(structlog.processors.JSONRenderer())
    else:
        # 开发友好格式
        processors.append(structlog.dev.ConsoleRenderer())
    
    # 配置 structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # 配置第三方库的日志级别
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class JSONFormatter(jsonlogger.JsonFormatter):
    """
    自定义 JSON 日志格式化器
    """
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # 添加自定义字段
        log_record['service'] = settings.PROJECT_NAME
        log_record['version'] = settings.VERSION
        log_record['environment'] = settings.ENVIRONMENT
        
        # 格式化时间戳
        if 'timestamp' not in log_record:
            log_record['timestamp'] = record.created


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    获取结构化日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        结构化日志器实例
    """
    return structlog.get_logger(name)