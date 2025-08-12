"""
异常处理模块

定义自定义异常类和全局异常处理器。
"""

from typing import Any, Dict, Optional

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger()


class APIException(Exception):
    """
    自定义 API 异常基类
    """
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """验证异常"""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class AuthenticationException(APIException):
    """认证异常"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(APIException):
    """授权异常"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundException(APIException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(APIException):
    """资源冲突异常"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class RateLimitException(APIException):
    """限流异常"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class ExternalServiceException(APIException):
    """外部服务异常"""
    
    def __init__(self, message: str = "External service error", service_name: str = ""):
        details = {"service": service_name} if service_name else {}
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)


class VectorDBException(ExternalServiceException):
    """向量数据库异常"""
    
    def __init__(self, message: str = "Vector database error"):
        super().__init__(message, "vector_db")


class AIServiceException(ExternalServiceException):
    """AI 服务异常"""
    
    def __init__(self, message: str = "AI service error", service_name: str = "ai_service"):
        super().__init__(message, service_name)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    自定义 API 异常处理器
    """
    logger.error(
        "API exception occurred",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 异常处理器
    """
    logger.error(
        "HTTP exception occurred",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "HTTPException",
            }
        },
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Pydantic 验证异常处理器
    """
    logger.error(
        "Validation exception occurred",
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "type": "ValidationError",
                "details": {"validation_errors": exc.errors()},
            }
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    SQLAlchemy 异常处理器
    """
    logger.error(
        "Database exception occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=exc.__class__.__name__,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Database error occurred",
                "type": "DatabaseError",
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    """
    logger.error(
        "Unexpected exception occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=exc.__class__.__name__,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "type": "InternalServerError",
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置异常处理器
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)