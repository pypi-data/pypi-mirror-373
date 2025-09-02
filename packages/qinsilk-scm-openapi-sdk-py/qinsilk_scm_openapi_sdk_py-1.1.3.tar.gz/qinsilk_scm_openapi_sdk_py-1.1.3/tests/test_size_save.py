"""
尺码保存请求测试
对应Java版本的 com.qinsilk.scm.openapi.sdk.biz.size.base.SizeSaveRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.size import (
    SizeSaveRequest, SizeSaveDTO, SizeDetailResponse
)
from tests.test_base import TestBase


class TestSizeSaveRequest(TestBase):
    """尺码保存请求测试类"""
    
    def test_add_size(self):
        """
        测试新增尺码
        对应Java版本的 testAddSize() 方法
        """
        # 创建尺码保存请求
        request = SizeSaveRequest()
        
        # 创建尺码保存DTO - 对应Java版本的SizeSaveDTO
        num = self.generate_random_number()
        size_save_dto = SizeSaveDTO(
            name=f"测试尺码{num}",
            size_group_id=757,  # 对应Java版本的757L
            is_default=0  # 必填字段
        )
        request.size_save_dto = size_save_dto
        
        # 执行请求 - 对应Java版本的openClient.execute()
        http_request, response = self.execute_request(request)
        
        # 验证响应 - 对应Java版本的Assert.isTrue()
        self.assert_success(response, "尺码保存请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, SizeDetailResponse), "响应类型不正确"
        
        # 验证返回的尺码数据
        if response.data:
            assert response.data.id is not None, "尺码ID不能为空"
            print(f"✅ 尺码保存成功，ID: {response.data.id}")
            print(f"尺码名称: {response.data.name}")
            print(f"尺码分组ID: {response.data.size_group_id}")
        
        # 测试第二次保存（生成新的随机数）- 对应Java版本的第二部分
        num2 = self.generate_random_number()
        size_save_dto.name = f"测试尺码{num2}"
        
        # 再次执行请求验证
        http_request2, response2 = self.execute_request(request)
        self.assert_success(response2, "第二次尺码保存请求失败")


@pytest.fixture
def size_save_test():
    """提供尺码保存测试实例的fixture"""
    return TestSizeSaveRequest()


def test_size_save_integration(size_save_test):
    """集成测试：尺码保存完整流程"""
    size_save_test.test_add_size()


if __name__ == "__main__":
    # 直接运行测试
    test_instance = TestSizeSaveRequest()
    test_instance.test_add_size()
    print("✅ 尺码保存测试通过")