from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from .base_util import BaseUtil

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    status: int
    message: str
    data: Optional[T] = None

    @classmethod
    def of_success(cls, status: int, data: T) -> "BaseResponse[T]":
        """성공 응답 생성"""
        return cls(status=status, message=BaseUtil.SUCCESS, data=data)
    
    @classmethod
    def of_fail(cls, status: int, message: str) -> "BaseResponse[T]":
        """실패 응답 생성"""
        return cls(status=status, message=message, data=None)
    
    @classmethod
    def of(cls, status: int, message: str, data: Optional[T] = None) -> "BaseResponse[T]":
        """일반 응답 생성"""
        return cls(status=status, message=message, data=data)
