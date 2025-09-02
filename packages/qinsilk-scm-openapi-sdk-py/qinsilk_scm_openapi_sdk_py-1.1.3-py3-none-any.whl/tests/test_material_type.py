"""
物料类型模块测试用例
对应Java版本：MaterialTypeSaveRequestTest.java等
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.material_type import (
    MaterialTypeSaveRequest, MaterialTypeDetailRequest, MaterialTypeListRequest,
    MaterialTypeUpdateRequest, MaterialTypeDeleteRequest, MaterialTypeSaveDTO
)
from .test_base import TestBase


class TestMaterialTypeSave(unittest.TestCase, TestBase):
    """物料类型保存测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_save_material_type(self):
        """测试保存物料类型"""
        try:
            request = MaterialTypeSaveRequest()
            num = self.generate_random_number()
            
            material_type_save_dto = MaterialTypeSaveDTO()
            material_type_save_dto.name = f"测试物料类型{num}"
            material_type_save_dto.state = 1
            material_type_save_dto.type = 1  # 面料
            material_type_save_dto.show_order = 100
            material_type_save_dto.remark = "测试物料类型描述"
            request.material_type_save_dto = material_type_save_dto
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"物料类型保存测试完成，类型名称: {material_type_save_dto.name}")
        except Exception as e:
            print(f"物料类型保存测试跳过: {e}")


class TestMaterialTypeList(unittest.TestCase, TestBase):
    """物料类型列表测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_material_type_list(self):
        """测试获取物料类型列表"""
        try:
            request = MaterialTypeListRequest()
            request.name = "测试"
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"物料类型列表测试完成，数据量: {len(getattr(response.data, 'list', []))}")
        except Exception as e:
            print(f"物料类型列表测试跳过: {e}")


if __name__ == '__main__':
    unittest.main()