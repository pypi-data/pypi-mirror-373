"""
客户端Token相关请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.token.ClientTokenRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.token import (
    ClientTokenRequest, ClientTokenResponse
)
from tests.test_base import TestBase


class TestClientTokenRequest(TestBase):
    """客户端Token请求测试类"""
    
    def test_get_token(self):
        """
        测试获取客户端Token
        对应Java版本的 ClientTokenRequestTest.testGetToken() 方法
        """
        request = ClientTokenRequest()
        
        # 设置客户端信息 - 对应Java版本的Constant.CLIENT_ID和CLIENT_SECRET
        request.client_id = self.get_client_id()
        request.client_secret = self.get_client_secret()
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "客户端Token请求失败")
        
        # 验证Token信息
        assert response.client_token is not None, "client_token不能为空"
        assert response.token_type is not None, "token_type不能为空"
        assert response.expires_in is not None, "expires_in不能为空"
        
        # 验证响应类型
        assert isinstance(response, ClientTokenResponse), "响应类型不正确"
        
        print(f"✅ 客户端Token获取成功")
        print(f"Token类型: {response.token_type}")
        print(f"Token: {response.client_token}")
        print(f"过期时间(秒): {response.expires_in}")


# 提供测试实例的fixture
@pytest.fixture
def client_token_test():
    return TestClientTokenRequest()


# 集成测试函数
def test_client_token_integration(client_token_test):
    """集成测试：客户端Token完整流程"""
    client_token_test.test_get_token()


if __name__ == "__main__":
    # 直接运行测试
    print("开始客户端Token测试...")
    token_test = TestClientTokenRequest()
    token_test.test_get_token()
    
    print("\n✅ 客户端Token测试通过")