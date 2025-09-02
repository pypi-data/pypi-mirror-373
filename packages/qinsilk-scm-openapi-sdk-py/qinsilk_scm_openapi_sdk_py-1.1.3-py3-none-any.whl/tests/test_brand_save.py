"""
品牌保存测试
对应Java版本：BlandSaveRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.brand import BrandSaveRequest, BrandSaveDTO
from .test_base import TestBase


class TestBrandSave(unittest.TestCase, TestBase):
    """品牌保存测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_add_brand(self):
        """
        测试添加品牌
        对应Java版本：testAddBland()方法
        """
        # 创建品牌保存请求
        request = BrandSaveRequest()
        
        # 生成随机数用于测试数据
        num = self.generate_random_number()
        
        # 设置品牌保存DTO
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
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        # 生成新的随机数进行二次测试（对应Java版本的行为）
        num = self.generate_random_number()
        brand_save_dto.name = f"测试品牌{num}"
        brand_save_dto.bland_code = f"TEST{num}"
        
        print(f"品牌保存测试完成，品牌代码: {brand_save_dto.bland_code}")


if __name__ == '__main__':
    unittest.main()