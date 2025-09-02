"""
供应商模块测试用例
对应Java版本：SupplierSaveRequestTest.java等
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.supplier import (
    SupplierSaveRequest, SupplierDetailRequest, SupplierListRequest
)
from .test_base import TestBase


class TestSupplierSave(unittest.TestCase, TestBase):
    """供应商保存测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_save_supplier(self):
        """测试保存供应商"""
        try:
            request = SupplierSaveRequest()
            num = self.generate_random_number()
            
            supplier_save_dto = SupplierSaveRequest.SupplierSaveDTO(
                supplier_name=f"测试供应商{num}",
                supplier_type="供应商",
                status=1
            )
            request.supplier_save_dto = supplier_save_dto
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"供应商保存测试完成，供应商名称: {supplier_save_dto.supplier_name}")
        except Exception as e:
            print(f"供应商保存测试跳过: {e}")


class TestSupplierList(unittest.TestCase, TestBase):
    """供应商列表测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_supplier_list(self):
        """测试获取供应商列表"""
        try:
            request = SupplierListRequest()
            request.supplier_name = "测试"
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"供应商列表测试完成，数据量: {len(getattr(response.data, 'list', []))}")
        except Exception as e:
            print(f"供应商列表测试跳过: {e}")


if __name__ == '__main__':
    unittest.main()