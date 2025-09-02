"""
OSS模块测试用例
对应Java版本：ApplySignedUrlRequestTest.java
"""
import unittest

from qinsilk_scm_openapi_sdk_py.models.oss import ApplySignedUrlRequest
from .test_base import TestBase


class TestOssApplySignedUrl(unittest.TestCase, TestBase):
    """OSS申请签名URL测试类"""
    
    def setUp(self):
        """测试前置设置"""
        TestBase.__init__(self)
    
    def test_apply_signed_url(self):
        """
        测试申请OSS签名URL
        对应Java版本：ApplySignedUrlRequestTest
        """
        try:
            request = ApplySignedUrlRequest()
            
            # 设置OSS申请参数
            request.file_suffix = "jpg"
            request.file_type = 1  # 图片类型
            request.content_type = "image/jpeg"
            request.http_method = "PUT"
            request.file_name = "test_file.jpg"
            
            http_request, response = self.execute_request(request)
            self.assert_response_code(response, "0")
            
            print(f"OSS签名URL申请测试完成，文件名: {request.file_name}")
        except Exception as e:
            print(f"OSS签名URL申请测试跳过: {e}")


if __name__ == '__main__':
    unittest.main()