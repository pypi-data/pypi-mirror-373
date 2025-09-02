"""
品牌详情和列表测试
对应Java版本：BlandDetailRequestTest.java 和 BlandListRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.brand import (
    BrandSaveRequest, BrandDetailRequest, BrandListRequest, BrandSaveDTO
)
from .test_base import TestBase


class TestBrandDetail(unittest.TestCase, TestBase):
    """品牌详情测试类"""
    
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
    
    def test_get_brand_detail(self):
        """
        测试获取品牌详情
        对应Java版本：testGetBlandDetail()方法
        """
        # 先保存一个品牌
        brand_id = self.do_save()
        
        # 创建品牌详情请求
        request = BrandDetailRequest()
        request.brand_id = brand_id
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        print(f"品牌详情测试完成，品牌ID: {brand_id}")


class TestBrandList(unittest.TestCase, TestBase):
    """品牌列表测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_get_brand_list(self):
        """
        测试获取品牌列表
        对应Java版本：testGetBlandList()方法
        """
        # 创建品牌列表请求
        request = BrandListRequest()
        request.name = "测试"
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        print(f"品牌列表测试完成，返回数据量: {len(getattr(response.data, 'list', []))}")


if __name__ == '__main__':
    unittest.main()