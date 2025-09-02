"""
颜色更新、删除、详情、列表请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.color.base.ColorUpdateRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.base.ColorDeleteRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.base.ColorDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.base.ColorListRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.color import (
    ColorBaseListRequest, ColorBaseListResponse,
    ColorBaseDetailRequest, ColorBaseDetailResponse,
    ColorBaseUpdateRequest, ColorBaseUpdateDTO,
    ColorBaseDeleteRequest,
    ColorBaseSaveRequest, ColorBaseSaveDTO
)
from qinsilk_scm_openapi_sdk_py.models.base import BaseResponse
from tests.test_base import TestBase


class TestColorUpdateRequest(TestBase):
    """颜色更新请求测试类"""
    
    def test_update_color(self):
        """
        测试更新颜色
        对应Java版本的 ColorUpdateRequestTest.testUpdateColor() 方法
        """
        # 首先获取颜色列表，找到要更新的颜色
        list_request = ColorBaseListRequest()
        list_request.page = 1
        list_request.size = 2
        
        list_execute_result = self.execute_request(list_request)
        list_response = self.get_response(list_execute_result)
        assert len(list_response.data) > 0, "No color to update"
        
        # 获取第二个颜色进行更新（对应Java版本的get(1)）
        color_detail = list_response.data[1] if len(list_response.data) > 1 else list_response.data[0]
        
        # 创建更新请求
        request = ColorBaseUpdateRequest()
        num = self.generate_random_number()
        
        # 创建更新DTO - 对应Java版本的ColorUpdateDTO
        # 确保必填字段有有效值，如果从列表获取的值为None，使用默认值
        color_update_dto = ColorBaseUpdateDTO(
            id=color_detail.id,
            name=f"测试颜色(修改){num}",
            color_value="#FF0001",
            color_group_id=color_detail.color_group_id if color_detail.color_group_id is not None else 1512,  # 提供默认颜色组ID
            is_default=color_detail.is_default if color_detail.is_default is not None else 0  # 提供默认值
        )
        request.color_update_dto = color_update_dto
        
        # 执行更新请求
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证响应（对应Java版本的Assertions.assertEquals("0", response.getCode(), "请求失败")）
        assert "0" == response.code, "请求失败"


class TestColorDeleteRequest(TestBase):
    """颜色删除请求测试类"""
    
    def test_delete_color(self):
        """
        测试删除颜色
        对应Java版本的 ColorDeleteRequestTest.testDeleteColor() 方法
        """
        # 首先创建一个颜色用于删除
        save_request = ColorBaseSaveRequest()
        num = self.generate_random_number()
        
        color_save_dto = ColorBaseSaveDTO(
            name=f"待删除颜色{num}",
            color_value="#FF0002",
            color_group_id=1512,
            is_default=0
        )
        save_request.color_save_dto = color_save_dto
        
        save_execute_result = self.execute_request(save_request)
        save_response = self.get_response(save_execute_result)
        assert "0" == save_response.code, "Create color failed"
        
        color_id = save_response.data.id
        
        # 删除颜色
        delete_request = ColorBaseDeleteRequest()
        delete_request.ids = [color_id]  # 对应Java版本的Collections.singletonList()
        
        delete_execute_result = self.execute_request(delete_request)
        delete_response = self.get_response(delete_execute_result)
        
        # 验证删除响应（对应Java版本的Assertions.assertEquals("0", deleteResponse.getCode(), "请求失败")）
        assert "0" == delete_response.code, "请求失败"


class TestColorDetailRequest(TestBase):
    """颜色详情请求测试类"""
    
    def test_color_detail_request(self):
        """
        测试颜色详情请求
        对应Java版本的 ColorDetailRequestTest.testColorDetailRequest() 方法
        """
        request = ColorBaseDetailRequest()
        request.color_id = 31252  # 对应Java版本的31252L
        
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证颜色ID正确（对应Java版本的Assert.isTrue(Objects.equal(31252L, execute.getRight().getData().getId()), "颜色id错误")）
        assert response.data.id == 31252, "颜色id错误"


class TestColorListRequest(TestBase):
    """颜色列表请求测试类"""
    
    def test_name_search(self):
        """
        测试按名称搜索颜色
        对应Java版本的 ColorListRequestTest.testName() 方法
        """
        request = ColorBaseListRequest()
        request.name = "测试颜色4394"
        
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证列表不为空（对应Java版本的Assert.isTrue(!execute.getRight().getData().isEmpty(), "颜色列表为空")）
        assert len(response.data) > 0, "颜色列表为空"
    
    def test_value_search(self):
        """
        测试按颜色值搜索颜色
        对应Java版本的 ColorListRequestTest.testValueSearch() 方法
        """
        request = ColorBaseListRequest()
        request.value = "1"
        
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证列表不为空（对应Java版本的Assert.isTrue(!execute.getRight().getData().isEmpty(), "颜色列表为空")）
        assert len(response.data) > 0, "颜色列表为空"


# 提供测试实例的fixtures
@pytest.fixture
def color_update_test():
    return TestColorUpdateRequest()

@pytest.fixture
def color_delete_test():
    return TestColorDeleteRequest()

@pytest.fixture
def color_detail_test():
    return TestColorDetailRequest()

@pytest.fixture
def color_list_test():
    return TestColorListRequest()


# 集成测试函数
def test_color_update_integration(color_update_test):
    """集成测试：颜色更新完整流程"""
    color_update_test.test_update_color()

def test_color_delete_integration(color_delete_test):
    """集成测试：颜色删除完整流程"""
    color_delete_test.test_delete_color()

def test_color_detail_integration(color_detail_test):
    """集成测试：颜色详情完整流程"""
    color_detail_test.test_color_detail_request()

def test_color_list_integration(color_list_test):
    """集成测试：颜色列表完整流程"""
    color_list_test.test_name_search()
    color_list_test.test_value_search()


if __name__ == "__main__":
    # 直接运行测试
    print("开始颜色更新测试...")
    update_test = TestColorUpdateRequest()
    update_test.test_update_color()
    
    print("\n开始颜色删除测试...")
    delete_test = TestColorDeleteRequest()
    delete_test.test_delete_color()
    
    print("\n开始颜色详情测试...")
    detail_test = TestColorDetailRequest()
    detail_test.test_color_detail_request()
    
    print("\n开始颜色列表测试...")
    list_test = TestColorListRequest()
    list_test.test_name_search()
    list_test.test_value_search()
    
    print("\n✅ 所有颜色测试通过")