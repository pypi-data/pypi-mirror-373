"""
季节更新测试
对应Java版本：SeasonUpdateRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.season import SeasonSaveRequest, SeasonSaveDTO, SeasonUpdateRequest, SeasonUpdateDTO
from tests.test_base import TestBase


class TestSeasonUpdate(unittest.TestCase, TestBase):
    """季节更新测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_update_season(self):
        """
        测试更新季节
        对应Java版本：testUpdateSeason()方法
        """
        # 先创建一个季节用于更新
        save_request = SeasonSaveRequest()
        season_save_dto = SeasonSaveDTO()
        num = self.generate_random_number()
        season_save_dto.name = f"待更新季节{num}"
        season_save_dto.code = f"TO_UPDATE{num}"
        season_save_dto.is_enable = 1
        season_save_dto.remark = "待更新的季节"
        season_save_dto.show_order = 100
        save_request.season_save_dto = season_save_dto
        
        # 执行保存请求
        save_http_request, save_response = self.execute_request(save_request)
        
        # 断言保存成功
        self.assert_response_code(save_response, "0")
        
        # 更新季节信息
        request = SeasonUpdateRequest()
        season_update_dto = SeasonUpdateDTO()
        season_update_dto.id = save_response.data.id
        season_update_dto.name = f"已更新季节{num}"
        season_update_dto.remark = "这是一个更新后的季节"
        season_update_dto.is_enable = 0
        request.season_update_dto = season_update_dto
        
        # 执行更新请求
        http_request, response = self.execute_request(request)
        
        # 断言更新成功
        self.assert_response_code(response, "0")
        
        print(f"季节更新测试完成，季节ID: {season_update_dto.id}")


if __name__ == '__main__':
    unittest.main()