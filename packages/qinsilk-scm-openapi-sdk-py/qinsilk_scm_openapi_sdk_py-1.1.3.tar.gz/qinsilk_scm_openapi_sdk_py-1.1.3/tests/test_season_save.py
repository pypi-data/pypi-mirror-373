"""
季节保存测试
对应Java版本：SeasonSaveRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.season import SeasonSaveRequest, SeasonSaveDTO
from tests.test_base import TestBase


class TestSeasonSave(unittest.TestCase, TestBase):
    """季节保存测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_add_season(self):
        """
        测试添加季节
        对应Java版本：testAddSeason()方法
        """
        # 创建季节保存请求
        request = SeasonSaveRequest()
        
        # 生成随机数用于测试数据
        num = self.generate_random_number()
        
        # 设置季节保存DTO
        season_save_dto = SeasonSaveDTO()
        season_save_dto.name = f"测试季节{num}"
        season_save_dto.code = f"TEST{num}"
        season_save_dto.is_enable = 1
        season_save_dto.remark = "测试季节描述"
        season_save_dto.show_order = 100
        request.season_save_dto = season_save_dto
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        # 生成新的随机数进行二次测试（对应Java版本的行为）
        num = self.generate_random_number()
        season_save_dto.name = f"测试季节{num}"
        season_save_dto.code = f"TEST{num}"
        
        print(f"季节保存测试完成，季节代码: {season_save_dto.code}")


if __name__ == '__main__':
    unittest.main()