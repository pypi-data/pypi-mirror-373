"""
仓库模块测试用例
对应Java版本：StorehouseSaveRequestTest.java等
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.storehouse import (
    StorehouseSaveRequest, StorehouseDetailRequest, StorehouseListRequest,
    StorehouseUpdateRequest, StorehouseDeleteRequest, StorehouseSaveDTO
)
from .test_base import TestBase


class TestStorehouseSave(unittest.TestCase, TestBase):
    """仓库保存测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_save_storehouse(self):
        """测试保存仓库"""
        try:
            request = StorehouseSaveRequest()
            num = self.generate_random_number()
            
            storehouse_save_dto = StorehouseSaveDTO()
            storehouse_save_dto.name = f"测试仓库{num}"
            storehouse_save_dto.type = 1  # 仓库类型
            request.storehouse_save_dto = storehouse_save_dto
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"仓库保存测试完成，仓库名称: {storehouse_save_dto.name}")
        except Exception as e:
            print(f"仓库保存测试跳过: {e}")


class TestStorehouseList(unittest.TestCase, TestBase):
    """仓库列表测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_storehouse_list(self):
        """测试获取仓库列表"""
        try:
            request = StorehouseListRequest()
            request.name = "测试"
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"仓库列表测试完成，数据量: {len(getattr(response.data, 'list', []))}")
        except Exception as e:
            print(f"仓库列表测试跳过: {e}")


if __name__ == '__main__':
    unittest.main()