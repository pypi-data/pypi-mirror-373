from typing import TypeVar, Any, Generic
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status

# 修改泛型约束，支持任意类型（包括基础类型和BaseModel）
T = TypeVar('T')


class BaseResponseModel(BaseModel, Generic[T]):
    """基础响应模型，支持多种数据类型（包括字符串、字典和Pydantic模型）"""
    code: int = Field(default=0, description="业务响应码，成功0，失败非0")
    message: str = Field(default="success", description="业务响应信息")
    data: T | None = Field(default=None, description="业务响应数据，支持任意类型")
    traceId: str | None = Field(default=None, description="请求链路追踪ID")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


def build_response_content(
    data: T | Any = None,
    code: int = 0,
    message: str = "success"
) -> dict:
    """
    只构建响应内容的字典部分

    Args:
        data: 响应数据（支持字符串、字典、Pydantic模型等）
        code: 业务响应码
        message: 响应信息

    Returns:
        响应内容字典，格式为{"code": int, "message": str, "data": Any}
    """
    response = BaseResponseModel(
        code=code,
        message=message,
        data=data
    )

    if isinstance(response.data, BaseModel):
        return {
            "code": response.code,
            "message": response.message,
            "data": response.data.model_dump()
        }
    else:
        return response.model_dump()


def create_response(
    data: T | Any = None,
    code: int = 0,
    message: str = "success",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """创建完整的JSONResponse响应"""
    content = build_response_content(data=data, code=code, message=message)
    return JSONResponse(
        content=content,
        status_code=status_code
    )


def success_response(data: T | Any = None, message: str = "success") -> JSONResponse:
    """快捷创建成功响应"""
    return create_response(data=data, message=message)


def error_response(
    message: str = "error",
    code: int = 1,
    data: T | Any = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
    """快捷创建错误响应"""
    return create_response(
        data=data,
        code=code,
        message=message,
        status_code=status_code
    )


def success_content(data: T | Any = None, message: str = "success") -> dict:
    """只构建成功响应的内容字典"""
    return build_response_content(data=data, message=message)


def error_content(
    message: str = "error",
    code: int = 1,
    data: T | Any = None
) -> dict:
    """只构建错误响应的内容字典"""
    return build_response_content(data=data, code=code, message=message)
