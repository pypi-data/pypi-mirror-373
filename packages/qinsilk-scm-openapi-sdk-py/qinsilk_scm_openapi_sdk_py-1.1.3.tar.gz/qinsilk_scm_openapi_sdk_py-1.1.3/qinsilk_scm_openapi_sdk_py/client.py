import logging
import time
import json
from dataclasses import dataclass, asdict, is_dataclass
from typing import Tuple, Any

import requests
from requests.exceptions import Timeout

from .exceptions import OpenException, ErrorCode
from .models.token import ClientTokenRequest, ClientTokenResponse
from .signing import sign_top_request, SIGN_METHOD_HMAC_SHA256
from .utils.serialization import (
    CustomJSONEncoder,
    convert_dict_keys_to_snake_case,
    convert_dict_keys_to_camel_case,
    remove_none_values
)
from .utils.dataclass_helper import instantiate_dataclass_from_dict

logger = logging.getLogger(__name__)


@dataclass
class OpenConfig:
    client_id: str
    client_secret: str
    server_url: str
    connect_timeout: int = 3  # seconds
    read_timeout: int = 10  # seconds
    access_token: str = None
    verify_ssl: bool = False  # 默认禁用SSL证书验证，避免自签名证书问题


class OpenClient:
    def __init__(self, open_config: OpenConfig):
        self.open_config = open_config
        self.http_session = requests.Session()
        # 配置SSL证书验证设置
        self.http_session.verify = open_config.verify_ssl
        # 如果禁用SSL验证，关闭警告信息
        if not open_config.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def execute(self, request) -> Tuple[requests.Request, Any]:
        """
        执行请求 - 完全按照Java版本的逻辑实现
        
        Args:
            request: 请求对象
            
        Returns:
            Tuple[Request, Response]: 请求对象和响应对象的元组
        """
        # 1. 准备公共参数（设置时间戳等）
        if not hasattr(request, 'timestamp') or request.timestamp is None:
            if hasattr(request, '__dict__'):
                request.timestamp = int(time.time() * 1000)
            else:
                # 对于dataclass，直接设置属性
                request.timestamp = int(time.time() * 1000)

        # 2. 如果需要token，设置访问令牌
        if request.is_need_token():
            # 检查 request 中是否已经有 access_token
            existing_token = getattr(request, 'access_token', None)
            if existing_token:
                # 如果 request 中已经有 token，直接使用
                access_token = existing_token
            else:
                # 如果没有 token，才申请新的 token
                access_token = self.get_client_token()
                
            # 确保 request 对象有 access_token 属性
            if hasattr(request, 'access_token'):
                request.access_token = access_token
            else:
                setattr(request, 'access_token', access_token)

        # 3. 构建参数字典 - 模拟Java的JSON序列化去除null值的行为
        if is_dataclass(request):
            params_dict = asdict(request)
        else:
            # 对于普通类，优先使用get_request_body方法
            if hasattr(request, 'get_request_body') and callable(getattr(request, 'get_request_body')):
                business_params = request.get_request_body()
                # 合并公共参数和业务参数
                params_dict = {
                    'timestamp': getattr(request, 'timestamp', None),
                    'version': getattr(request, 'version', None),
                    'access_token': getattr(request, 'access_token', None)
                }
                # 添加业务参数
                if business_params:
                    params_dict.update(business_params)
            else:
                # 兼容旧的逻辑：直接收集所有非私有属性
                params_dict = {}
                for k, v in request.__dict__.items():
                    if not k.startswith('_'):
                        # 如果属性值是DTO对象且有to_dict方法，则转换为字典
                        if hasattr(v, 'to_dict') and callable(getattr(v, 'to_dict')):
                            params_dict[k] = v.to_dict()
                        else:
                            params_dict[k] = v

        # 移除None值，模拟Java的JSON序列化行为
        params = remove_none_values(params_dict)

        # 将Python的下划线字段转换为Java期望的驼峰字段
        # 注意：ClientTokenRequest是特殊情况，Java版本本身就使用下划线命名，不需要转换
        from .models.token import ClientTokenRequest
        if not isinstance(request, ClientTokenRequest):
            params = convert_dict_keys_to_camel_case(params)

        # 4. 准备搜索参数
        search_params = {}

        # 5. 参数签名
        sign = sign_top_request(params, self.open_config.client_secret, SIGN_METHOD_HMAC_SHA256)
        search_params["sign"] = sign
        search_params["sign_method"] = SIGN_METHOD_HMAC_SHA256
        search_params["access_token"] = params.get("accessToken") or params.get("access_token")

        print(f"构建的请求参数: {params}")
        print(f"生成的签名: {sign}")

        # 6. 构建HTTP请求
        http_request = None

        if request.get_request_type() == "GET":
            # GET请求：所有参数都放在URL中
            params.update(search_params)
            url = self.build_request_url(request.get_api_url(), params)
            print(f"完整请求URL: {url}")
            http_request = requests.Request(method="GET", url=url)

        elif request.get_request_type() == "POST":
            # POST请求：search_params放在URL中，完整的params作为JSON body
            # 注意：与Java版本保持一致，access_token应该同时存在于URL和请求体中
            url = self.build_request_url(request.get_api_url(), search_params)
            
            # 使用自定义JSON编码器处理datetime等特殊类型
            json_data = json.dumps(params, cls=CustomJSONEncoder, ensure_ascii=False)
            
            http_request = requests.Request(
                method="POST",
                url=url,
                data=json_data,
                headers={"Content-Type": "application/json"}
            )

        if http_request is None:
            raise OpenException(ErrorCode.UNKNOWN_ERROR)

        # 7. 执行请求
        prepared_request = self.http_session.prepare_request(http_request)

        try:
            http_response = self.http_session.send(
                prepared_request,
                timeout=(self.open_config.connect_timeout, self.open_config.read_timeout)
            )

            if not http_response.ok:
                raise OpenException(ErrorCode.CONNECT_TIMEOUT)

            response_body = http_response.json()

            # 8. 反序列化响应 - 直接使用原始响应数据，模型中的__init__方法会处理蛇形命名转换
            # snake_case_response = convert_dict_keys_to_snake_case(response_body)

            # 获取响应类
            if hasattr(request, 'response_class'):
                if callable(request.response_class):
                    response_cls = request.response_class()  # 调用方法获取响应类型
                else:
                    response_cls = request.response_class   # 直接使用响应类型
            else:
                # 默认响应类
                from .models.base import BaseResponse
                response_cls = BaseResponse

            # 实例化响应对象
            if is_dataclass(response_cls):
                response_obj = instantiate_dataclass_from_dict(response_cls, response_body)
            else:
                response_obj = response_cls(response_body)

            return prepared_request, response_obj

        except Timeout:
            raise OpenException(ErrorCode.READ_TIMEOUT)
        except requests.exceptions.ConnectionError:
            raise OpenException(ErrorCode.CONNECT_TIMEOUT)
        except requests.exceptions.RequestException as e:
            print(f"HTTP请求失败: {e}")
            raise OpenException(ErrorCode.UNKNOWN_ERROR, exception=e)

    def get_client_token(self) -> str:
        """获得客户端令牌"""
        client_token_request = ClientTokenRequest(
            client_id=self.open_config.client_id,
            client_secret=self.open_config.client_secret
        )
        _, response = self.execute(client_token_request)

        if response.is_success() and hasattr(response, 'client_token') and response.client_token:
            self.open_config.access_token = response.client_token
            return response.client_token
        else:
            raise OpenException(ErrorCode.INVALID_RESPONSE, exception=response)

    def build_request_url(self, api_method: str, params: dict) -> str:
        """
        辅助方法：构建请求URL - 完全按照Java版本实现
        """
        base_url = self.open_config.server_url
        url_builder = base_url.rstrip('/') + '/'
        url_builder += api_method.lstrip('/') + '?'

        # 拼接参数
        param_parts = []
        for key, value in params.items():
            param_parts.append(f"{key}={value}")

        url_builder += "&".join(param_parts)
        return url_builder.rstrip('&')  # 去掉最后的&


