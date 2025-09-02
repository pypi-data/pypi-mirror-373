"""
季节删除测试
对应Java版本：SeasonDeleteRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.season import SeasonSaveRequest, SeasonSaveDTO, SeasonDeleteRequest
from tests.test_base import TestBase


class TestSeasonDelete(unittest.TestCase, TestBase):
    """季节删除测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_delete_season(self):
        """
        测试删除季节
        对应Java版本：testDeleteSeason()方法
        """
        # 先创建一个季节用于删除
        save_request = SeasonSaveRequest()
        season_save_dto = SeasonSaveDTO()
        num = self.generate_random_number()
        season_save_dto.name = f"待删除季节{num}"
        season_save_dto.code = f"TO_DELETE{num}"
        season_save_dto.is_enable = 1
        season_save_dto.remark = "待删除的季节"
        season_save_dto.show_order = 100
        save_request.season_save_dto = season_save_dto
        
        # 执行保存请求
        save_http_request, save_response = self.execute_request(save_request)
        
        # 断言保存成功
        self.assert_response_code(save_response, "0")
        
        # 删除季节
        request = SeasonDeleteRequest()
        request.ids = [save_response.data.id]
        
        # 执行删除请求
        http_request, response = self.execute_request(request)
        
        # 断言删除成功
        self.assert_response_code(response, "0")
        
        print(f"季节删除测试完成，删除的季节ID: {save_response.data.id}")


if __name__ == '__main__':
    unittest.main()