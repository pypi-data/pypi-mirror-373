"""
Token相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class ClientTokenRequest(BaseRequest):
    """获得客户端token请求"""
    
    def __init__(self, client_id=None, client_secret=None):
        super().__init__()
        self.grant_type = "client_credentials"  # 固定值
        self.client_id = client_id  # 客户端id（必填）
        self.client_secret = client_secret  # 客户端秘钥（必填）

    def get_api_url(self):
        return "api/oauth2/client_token"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ClientTokenResponse

    def get_request_type(self):
        """GET请求"""
        return "GET"
    
    def is_need_token(self):
        """不需要token"""
        return False

    def get_request_body(self):
        return {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }


class ClientTokenDetail:
    """客户端token详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.token_type = data.get('tokenType')
        self.client_token = data.get('clientToken')
        self.expires_in = data.get('expiresIn')


class ClientTokenResponse(BaseResponse):
    """客户端token响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data:
            # 直接从响应数据中获取字段，与Java版本保持一致
            self.token_type = response_data.get('token_type') or response_data.get('tokenType')
            self.client_token = response_data.get('client_token') or response_data.get('clientToken')
            self.expires_in = response_data.get('expires_in') or response_data.get('expiresIn')
            # 保持data字段兼容性
            self.data = ClientTokenDetail(response_data)
        else:
            self.token_type = None
            self.client_token = None
            self.expires_in = None
            self.data = None