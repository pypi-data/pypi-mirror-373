"""
颜色保存请求测试
对应Java版本的 com.qinsilk.scm.openapi.sdk.biz.color.base.ColorSaveRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.color import (
    ColorBaseSaveRequest, ColorBaseSaveDTO, ColorBaseDetailResponse
)
from tests.test_base import TestBase


class TestColorSaveRequest(TestBase):
    """颜色保存请求测试类"""
    
    def test_add_color(self):
        """
        测试新增颜色
        对应Java版本的 testAddColor() 方法
        """
        # 创建颜色保存请求
        request = ColorBaseSaveRequest()
        
        # 创建颜色保存DTO - 对应Java版本的ColorSaveDTO
        num = self.generate_random_number()
        color_save_dto = ColorBaseSaveDTO(
            name=f"测试颜色{num}",
            color_value="#FF0000",  # 红色
            color_group_id=1512  # 对应Java版本的1512L
        )
        request.color_save_dto = color_save_dto
        
        # 执行请求 - 对应Java版本的openClient.execute()
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证响应 - 对应Java版本的Assert.isTrue("0".equals(execute.getRight().getCode()), "请求失败")
        assert "0" == response.code, "请求失败"
        
        # 重新设置数据（为了生成文档，不是测试逻辑） - 对应Java版本的第二部分
        num = self.generate_random_number()
        color_save_dto.name = f"测试颜色{num}"
        color_save_dto.color_value = "#FF0000"
        color_save_dto.color_group_id = 1512
        # 注意：Java版本这里没有再次执行请求，只是为了生成API文档


@pytest.fixture
def color_save_test():
    """提供颜色保存测试实例的fixture"""
    return TestColorSaveRequest()


def test_color_save_integration(color_save_test):
    """集成测试：颜色保存完整流程"""
    color_save_test.test_add_color()


if __name__ == "__main__":
    # 直接运行测试
    test_instance = TestColorSaveRequest()
    test_instance.test_add_color()
    print("✅ 颜色保存测试通过")