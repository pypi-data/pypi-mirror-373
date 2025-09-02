"""
测试基础工具类
提供通用的测试方法和断言
"""
import random
import time
from typing import Any, Dict

from qinsilk_scm_openapi_sdk_py.client import OpenClient, OpenConfig
from qinsilk_scm_openapi_sdk_py.exceptions import OpenException
from .constant import API_URL, CLIENT_ID, CLIENT_SECRET


class TestBase:
    """测试基础类，提供通用的测试设置和方法"""
    
    def __init__(self):
        self.open_client = None
        self.setup_client()
    
    def setup_client(self):
        """设置OpenClient - 对应Java版本的@BeforeEach init()方法"""
        open_config = OpenConfig(
            server_url=API_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        self.open_client = OpenClient(open_config)
    
    def get_client_id(self) -> str:
        """获取客户端ID"""
        return CLIENT_ID
    
    def get_client_secret(self) -> str:
        """获取客户端密钥"""
        return CLIENT_SECRET
    
    @staticmethod
    def generate_random_number(min_val: int = 1000, max_val: int = 9999) -> int:
        """生成随机数 - 对应Java版本的RandomUtils.nextInt()"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def generate_timestamp() -> int:
        """生成时间戳"""
        return int(time.time() * 1000)
    
    def execute_request(self, request: Any) -> tuple:
        """执行请求并返回结果 - 对应Java版本的openClient.execute()"""
        try:
            # 返回的是 Pair<Request, Response> 的Python等价物
            return self.open_client.execute(request)
        except OpenException as e:
            raise AssertionError(f"请求执行失败: {e}")
    
    def get_response(self, execute_result: tuple) -> Any:
        """从执行结果中获取响应 - 对应Java版本的execute.getRight()"""
        if execute_result and len(execute_result) >= 2:
            return execute_result[1]  # 第二个元素是响应
        return None
    
    def assert_success(self, response: Any, message: str = "请求失败"):
        """断言响应成功 - 对应Java版本的Assert.isTrue()"""
        if response is None:
            raise AssertionError(f"{message}: 响应为空")
        
        # 检查是否有is_success方法
        if hasattr(response, 'is_success') and callable(getattr(response, 'is_success')):
            if not response.is_success():
                code = getattr(response, 'code', 'unknown')
                error_message = getattr(response, 'message', 'unknown')
                raise AssertionError(f"{message}: code={code}, message={error_message}")
        else:
            # 如果没有is_success方法，直接检查code字段
            code = getattr(response, 'code', None)
            if code != "0":
                error_message = getattr(response, 'message', 'unknown')
                raise AssertionError(f"{message}: code={code}, message={error_message}")
    
    def assert_response_code(self, response: Any, expected_code: str = "0"):
        """断言响应码"""
        if response is None:
            raise AssertionError(f"响应为空，无法获取响应码")
        
        actual_code = getattr(response, 'code', None)
        message = getattr(response, 'message', 'unknown')
        
        if actual_code != expected_code:
            # 获取更多调试信息
            data = getattr(response, 'data', None)
            raise AssertionError(
                f"期望响应码: {expected_code}, 实际响应码: {actual_code}, "
                f"错误消息: {message}, 响应数据: {data}"
            )
    
    def assert_true(self, condition: bool, message: str = "断言失败"):
        """断言为真 - 对应Java版本的Assert.isTrue()"""
        assert condition, message
    
    def assert_equals(self, expected, actual, message: str = "值不相等"):
        """断言相等 - 对应Java版本的Assert.assertEquals()"""
        assert expected == actual, f"{message}: expected={expected}, actual={actual}"


def generate_test_goods_sn(prefix: str = "test-open-add-goods") -> str:
    """生成测试商品货号"""
    num = TestBase.generate_random_number()
    return f"{prefix}{num}"


def generate_test_sku_barcode(prefix: str = "1234567890123") -> str:
    """生成测试SKU条码"""
    num = TestBase.generate_random_number()
    return f"{prefix}{num}"