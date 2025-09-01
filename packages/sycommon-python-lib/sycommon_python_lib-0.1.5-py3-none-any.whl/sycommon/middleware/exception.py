from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import traceback


def setup_exception_handler(app, config: dict):
    # 设置上传文件大小限制为 MaxBytes
    app.config = {'MAX_CONTENT_LENGTH': config.get('MaxBytes', 209715200)}

    # 1. 处理文件大小超限异常
    @app.exception_handler(413)
    async def request_entity_too_large(request: Request, exc):
        MaxBytes = config.get('MaxBytes', 209715200)
        int_MaxBytes = int(MaxBytes) / 1024 / 1024
        return JSONResponse(
            content={
                'code': 413, 'error': f'File size exceeds the allowed limit of {int_MaxBytes}MB.'},
            status_code=413
        )

    # 2. 处理 HTTP 异常
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path)
            }
        )

    # 3. 处理 Pydantic 验证错误
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "参数验证失败",
                "details": exc.errors()
            }
        )

    # 4. 自定义业务异常
    class BusinessException(Exception):
        def __init__(self, code: int, message: str):
            self.code = code
            self.message = message

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "message": exc.message
            }
        )

    # 5. 全局异常处理器（捕获所有未处理的异常）
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 记录详细错误信息
        error_msg = f"请求路径: {request.url}\n"
        error_msg += f"错误类型: {type(exc).__name__}\n"
        error_msg += f"错误信息: {str(exc)}\n"
        error_msg += f"堆栈信息: {traceback.format_exc()}"

        # 使用你的日志服务记录错误
        from sycommon.logging.kafka_log import SYLogger
        SYLogger.error(error_msg)

        # 返回统一格式的错误响应（生产环境可选择不返回详细信息）
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误，请稍后重试",
                "detail": str(exc) if config.get('DEBUG', False) else "Internal Server Error"
            }
        )

    return app
