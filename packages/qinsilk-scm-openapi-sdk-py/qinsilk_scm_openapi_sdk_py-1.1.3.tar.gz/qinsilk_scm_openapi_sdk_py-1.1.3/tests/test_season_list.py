"""
季节列表查询测试
对应Java版本：SeasonListRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.season import SeasonListRequest
from tests.test_base import TestBase


class TestSeasonList(unittest.TestCase, TestBase):
    """季节列表查询测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_get_season_list(self):
        """
        测试获取季节列表
        对应Java版本：testGetSeasonList()方法
        """
        # 创建季节列表请求
        request = SeasonListRequest()
        request.name = "测试"
        request.page = 1
        request.size = 10
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        print(f"季节列表查询测试完成，返回数据条数: {len(response.data) if response.data else 0}")


if __name__ == '__main__':
    unittest.main()