# FastAPI Extensions
# pylint: disable=W0613

import logging
import sys
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 移除默认控制台日志器
logger.remove()

# 日志输出到控制台
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

# 日志输出到文件
logger.add(
    sink="logs/runtime.log",  # 日志文件
    rotation="10 MB",  # 文件达到 10MB 自动轮转
    retention="7 days",  # 保留 7 天日志
    compression="zip",  # 超过的日志自动压缩
    level="INFO",  # 记录等级
    encoding="utf-8",  # 文件编码
    enqueue=True,  # 多线程、多进程安全
    diagnose=True,  # 显示变量值
    backtrace=True,  # 捕获堆栈追踪
)


# --------------------------------------------------------------------------------------------------


def CORS(app):
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=["*"],
    )


def Response(code: int = 200, data: Any = None, message: str | None = None, status_code: int = 200):
    return JSONResponse(content={"code": code, "data": data, "message": message}, status_code=status_code)


def exceptions(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP Exception: {exc.detail}")
        return Response(status_code=exc.status_code, code=exc.status_code, message=exc.detail)

    # 参数验证错误
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request Validation Error: {exc.errors()}")
        return Response(code=422, data=exc.errors(), message="Request Validation Error")

    # 参数验证错误
    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"Pydantic Validation Error: {exc.errors()}")
        return Response(code=422, data=exc.errors(), message="Pydantic Validation Error")

    # 服务器内部错误
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled Exception")
        return Response(code=500, data=None, message="Server Internal Error")


# --------------------------------------------------------------------------------------------------


# 兼容 FastAPI/Uvicorn 的 logging（重要）
class InterceptHandler(logging.Handler):
    """Intercept Handler"""

    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

    def write(self, message: str):
        if message.strip():
            logger.info(message.strip())

    def flush(self):
        pass
