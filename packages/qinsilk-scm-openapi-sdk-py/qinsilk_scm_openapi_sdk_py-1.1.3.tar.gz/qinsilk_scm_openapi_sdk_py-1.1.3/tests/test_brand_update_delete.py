"""
品牌更新和删除测试
对应Java版本：BlandUpdateRequestTest.java 和 BlandDeleteRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.brand import (
    BrandSaveRequest, BrandUpdateRequest, BrandDeleteRequest, BrandSaveDTO, BrandUpdateDTO
)
from .test_base import TestBase


class TestBrandUpdate(unittest.TestCase, TestBase):
    """品牌更新测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_update_brand(self):
        """
        测试更新品牌
        对应Java版本：testUpdateBland()方法
        """
        # 先保存一个品牌
        save_request = BrandSaveRequest()
        num = self.generate_random_number()
        
        brand_save_dto = BrandSaveDTO()
        brand_save_dto.name = f"测试品牌{num}"
        brand_save_dto.bland_code = f"TEST{num}"
        brand_save_dto.logo_url = "https://example.com/logo.png"
        brand_save_dto.description = "测试品牌描述"
        brand_save_dto.url = "https://example.com"
        brand_save_dto.show_order = 100
        brand_save_dto.is_show = 1
        brand_save_dto.is_default = 0
        save_request.brand_save_dto = brand_save_dto
        
        http_request, save_response = self.execute_request(save_request)
        self.assert_response_code(save_response, "0")
        
        brand_id = save_response.data.id
        
        # 创建品牌更新请求
        update_request = BrandUpdateRequest()
        num = self.generate_random_number()
        
        brand_update_dto = BrandUpdateDTO()
        brand_update_dto.id = brand_id
        brand_update_dto.name = f"更新品牌{num}"
        brand_update_dto.bland_code = f"UPDATED{num}"
        brand_update_dto.logo_url = "https://example.com/updated-logo.png"
        brand_update_dto.description = "更新品牌描述"
        brand_update_dto.url = "https://updated-example.com"
        brand_update_dto.show_order = 200
        brand_update_dto.is_show = 1
        brand_update_dto.is_default = 0
        update_request.brand_update_dto = brand_update_dto
        
        # 执行更新请求
        http_request, update_response = self.execute_request(update_request)
        
        # 断言请求成功
        self.assert_response_code(update_response, "0")
        
        print(f"品牌更新测试完成，品牌ID: {brand_id}")


class TestBrandDelete(unittest.TestCase, TestBase):
    """品牌删除测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def do_save(self) -> int:
        """
        先保存一个品牌，返回品牌ID
        对应Java版本：doSave()方法
        """
        request = BrandSaveRequest()
        num = self.generate_random_number()
        
        brand_save_dto = BrandSaveDTO()
        brand_save_dto.name = f"测试品牌{num}"
        brand_save_dto.bland_code = f"TEST{num}"
        brand_save_dto.logo_url = "https://example.com/logo.png"
        brand_save_dto.description = "测试品牌描述"
        brand_save_dto.url = "https://example.com"
        brand_save_dto.show_order = 100
        brand_save_dto.is_show = 1
        brand_save_dto.is_default = 0
        request.brand_save_dto = brand_save_dto
        
        http_request, response = self.execute_request(request)
        self.assert_response_code(response, "0")
        
        return response.data.id
    
    def test_delete_brand(self):
        """
        测试删除品牌
        对应Java版本：testDeleteBland()方法
        """
        # 先保存一个品牌
        brand_id = self.do_save()
        
        # 创建品牌删除请求
        request = BrandDeleteRequest()
        request.ids = [brand_id]  # 对应Java版本的Lists.newArrayList(id)
        
        # 执行删除请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        print(f"品牌删除测试完成，删除品牌ID: {brand_id}")


if __name__ == '__main__':
    unittest.main()