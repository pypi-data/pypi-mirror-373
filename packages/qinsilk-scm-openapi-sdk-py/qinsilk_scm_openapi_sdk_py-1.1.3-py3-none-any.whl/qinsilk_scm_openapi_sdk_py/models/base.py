from __future__ import annotations
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Type, TypeVar, Generic, Optional, List, get_origin, get_args, Union
import time

from ..exceptions import OpenException

T = TypeVar('T', bound='DataclassBaseResponse')


# ===== New style classes for consistency with Java SDK =====

class BaseRequest:
    """新式基础请求类，与Java SDK保持一致"""
    
    def __init__(self):
        self.access_token = None
        self.timestamp = int(time.time() * 1000)
        self.version = "1.0"
    
    def is_need_token(self) -> bool:
        return True
    
    def get_request_type(self) -> str:
        return "POST"
    
    def get_api_url(self) -> str:
        raise NotImplementedError
    
    def get_version(self) -> str:
        return self.version
    
    def response_class(self):
        """返回响应类，子类应该重写此方法"""
        return BaseResponse


class BaseResponse:
    """新式基础响应类，与Java SDK保持一致"""
    
    def __init__(self, response_data=None):
        if response_data is None:
            response_data = {}
        self.code = response_data.get('code', '0')
        self.message = response_data.get('message', '')
        self.msg = response_data.get('msg', '')
        self.success = response_data.get('success', True)
        self.exception = None
    
    def is_success(self) -> bool:
        return self.code == "0" or self.success


# ===== Original dataclass-based classes =====


@dataclass
class DataclassBaseResponse:
    code: str = "0"
    message: Optional[str] = ""
    msg: Optional[str] = ""
    success: Optional[bool] = True
    exception: Optional[OpenException] = None

    def is_success(self) -> bool:
        return self.code == "0" or self.success


@dataclass
class Pager:
    page_no: int = 1
    page_size: int = 18
    total_count: int = 0
    page_count: int = 0
    first_no: int = 0


@dataclass
class PageResponse(DataclassBaseResponse):
    page: Optional[Pager] = None


@dataclass
class DataclassBaseRequest(Generic[T]):
    access_token: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    version: str = "1.0"

    def is_need_token(self) -> bool:
        return True

    def get_request_type(self) -> str:
        return "POST"

    def response_class(self) -> Type[T]:
        raise NotImplementedError

    def get_api_url(self) -> str:
        raise NotImplementedError


@dataclass
class QueryOrderByDTO:
    sidx: str
    sord: str


@dataclass
class PageRequest(DataclassBaseRequest[T]):
    page: int = 1
    size: int = 10
    order_by_list: Optional[List[QueryOrderByDTO]] = None


@dataclass
class ClientTokenResponse(DataclassBaseResponse):
    token_type: Optional[str] = None
    client_token: Optional[str] = None
    expires_in: Optional[int] = None


@dataclass
class ClientTokenRequest(DataclassBaseRequest[ClientTokenResponse]):
    grant_type: str = "client_credentials"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    def is_need_token(self) -> bool:
        return False

    def get_request_type(self) -> str:
        return "GET"

    def response_class(self) -> Type[ClientTokenResponse]:
        return ClientTokenResponse

    def get_api_url(self) -> str:
        return "api/oauth2/client_token" 