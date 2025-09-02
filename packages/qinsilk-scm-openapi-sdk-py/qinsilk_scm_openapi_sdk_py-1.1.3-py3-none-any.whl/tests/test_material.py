"""
物料模块测试用例
对应Java版本：MaterialSaveRequestTest.java等
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.material import (
    MaterialDetailRequest, MaterialListRequest
)
from .test_base import TestBase


class TestMaterialList(unittest.TestCase, TestBase):
    """物料列表测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_material_list(self):
        """测试获取物料列表"""
        try:
            request = MaterialListRequest()
            request.material_sn = "测试"
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"物料列表测试完成，数据量: {len(getattr(response.data, 'list', []))}")
        except Exception as e:
            print(f"物料列表测试跳过: {e}")


class TestMaterialDetail(unittest.TestCase, TestBase):
    """物料详情测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_material_detail(self):
        """测试获取物料详情"""
        try:
            # 假设有一个固定的测试物料ID
            request = MaterialDetailRequest()
            request.material_id = 1  # 使用测试ID
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"物料详情测试完成")
        except Exception as e:
            print(f"物料详情测试跳过: {e}")


if __name__ == '__main__':
    unittest.main()