from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

# 定义通用响应模型
T = TypeVar("T")  # 泛型类型


class ResponseModel(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None
    total: Optional[int] = None


def success() -> ResponseModel[T]:
    return ResponseModel(code=200, message='success')


def error(error_code: int, message: str) -> ResponseModel[T]:
    return ResponseModel(code=error_code, message=message)


def result(data) -> ResponseModel[T]:
    return ResponseModel(code=200, message='success', data=data)


def result_page(data, total) -> ResponseModel[T]:
    return ResponseModel(code=200, message='success', data=data, total=total)
