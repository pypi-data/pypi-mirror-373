"""
季节详情查询测试
对应Java版本：SeasonDetailRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.season import SeasonSaveRequest, SeasonSaveDTO, SeasonDetailRequest
from tests.test_base import TestBase


class TestSeasonDetail(unittest.TestCase, TestBase):
    """季节详情查询测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_get_season_detail(self):
        """
        测试获取季节详情
        对应Java版本：testGetSeasonDetail()方法
        """
        # 先创建一个季节用于查询
        save_request = SeasonSaveRequest()
        season_save_dto = SeasonSaveDTO()
        num = self.generate_random_number()
        season_save_dto.name = f"查询测试季节{num}"
        season_save_dto.code = f"QUERY_TEST{num}"
        season_save_dto.is_enable = 1
        season_save_dto.remark = "用于查询测试的季节"
        season_save_dto.show_order = 100
        save_request.season_save_dto = season_save_dto
        
        # 执行保存请求
        save_http_request, save_response = self.execute_request(save_request)
        
        # 断言保存成功
        self.assert_response_code(save_response, "0")
        
        # 查询季节详情
        request = SeasonDetailRequest()
        request.season_id = save_response.data.id
        
        # 执行查询请求
        http_request, response = self.execute_request(request)
        
        # 断言查询成功
        self.assert_response_code(response, "0")
        
        print(f"季节详情查询测试完成，季节ID: {request.season_id}")


if __name__ == '__main__':
    unittest.main()