"""
颜色组相关请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.color.group.ColorGroupSaveRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.group.ColorGroupUpdateRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.group.ColorGroupDeleteRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.group.ColorGroupDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.color.group.ColorGroupListRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.color import (
    ColorGroupSaveRequest, ColorGroupSaveDTO, ColorGroupDetailResponse,
    ColorGroupUpdateRequest, ColorGroupUpdateDTO,
    ColorGroupDeleteRequest,
    ColorGroupDetailRequest,
    ColorGroupListRequest, ColorGroupListResponse
)
from qinsilk_scm_openapi_sdk_py.models.base import BaseResponse
from tests.test_base import TestBase


class TestColorGroupSaveRequest(TestBase):
    """颜色组保存请求测试类"""
    
    def test_color_group_save_request(self):
        """
        测试颜色组保存请求
        对应Java版本的 ColorGroupSaveRequestTest.testColorGroupSaveRequest() 方法
        """
        request = ColorGroupSaveRequest()
        
        # 创建颜色组保存DTO - 对应Java版本的ColorGroupSaveDTO
        num = self.generate_random_number()
        dto = ColorGroupSaveDTO(name=f"测试分组{num}")
        request.color_group_save_dto = dto
        
        # 执行请求
        execute_result = self.execute_request(request)
        response = self.get_response(execute_result)
        
        # 验证保存的实体有ID（对应Java版本的Assert.notNull(response.getData().getId(), "Saved entity should have an ID")）
        assert response.data.id is not None, "Saved entity should have an ID"
        
        # 重新设置数据（为了生成文档，不是测试逻辑） - 对应Java版本的第二部分
        num = self.generate_random_number()
        dto.name = f"测试分组{num}"
        # 注意：Java版本这里没有再次执行请求，只是为了生成API文档


class TestColorGroupUpdateRequest(TestBase):
    """颜色组更新请求测试类"""
    
    def test_update_color_group(self):
        """
        测试更新颜色组
        对应Java版本的 ColorGroupUpdateRequestTest.testUpdateColorGroup() 方法
        """
        # 首先创建一个颜色组用于更新测试
        save_request = ColorGroupSaveRequest()
        num = self.generate_random_number()
        original_name = f"待更新颜色组{num}"
        
        save_dto = ColorGroupSaveDTO(name=original_name)
        save_request.color_group_save_dto = save_dto
        
        http_request, save_response = self.execute_request(save_request)
        self.assert_success(save_response, "创建测试颜色组失败")
        self.assert_response_code(save_response, "0")
        
        created_group_id = save_response.data.id
        print(f"创建测试颜色组成功，ID: {created_group_id}")
        
        # 创建更新请求
        request = ColorGroupUpdateRequest()
        update_num = self.generate_random_number()
        updated_name = f"测试颜色分组(修改){update_num}"
        
        # 创建更新DTO - 对应Java版本的ColorGroupUpdateDTO
        color_group_update_dto = ColorGroupUpdateDTO(
            id=created_group_id,
            name=updated_name
        )
        request.color_group_update_dto = color_group_update_dto
        
        # 执行更新请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "颜色组更新请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, ColorGroupDetailResponse), "响应类型不正确"
        
        # 验证更新效果
        assert response.data.id == created_group_id, "更新后ID不匹配"
        # 注意：根据Java版本的实现，API不返回名称字段，所以不验证名称
        
        print(f"✅ 颜色组更新成功，ID: {response.data.id}")


class TestColorGroupDeleteRequest(TestBase):
    """颜色组删除请求测试类"""
    
    def test_delete_color_group(self):
        """
        测试删除颜色组
        对应Java版本的 ColorGroupDeleteRequestTest.testDeleteColorGroup() 方法
        """
        # 首先创建一个颜色组用于删除
        save_request = ColorGroupSaveRequest()
        num = self.generate_random_number()
        
        save_dto = ColorGroupSaveDTO(name=f"待删除颜色分组{num}")
        save_request.color_group_save_dto = save_dto
        
        http_request, save_response = self.execute_request(save_request)
        self.assert_success(save_response, "Create color group failed")
        self.assert_response_code(save_response, "0")
        
        group_id = save_response.data.id
        print(f"创建待删除颜色组成功，ID: {group_id}")
        
        # 删除颜色组
        delete_request = ColorGroupDeleteRequest()
        delete_request.ids = [group_id]  # 对应Java版本的Collections.singletonList()
        
        http_request, delete_response = self.execute_request(delete_request)
        
        # 验证删除响应
        self.assert_success(delete_response, "颜色组删除请求失败")
        self.assert_response_code(delete_response, "0")
        
        # 验证响应类型
        assert isinstance(delete_response, BaseResponse), "响应类型不正确"
        
        print(f"✅ 颜色组删除成功，ID: {group_id}")


class TestColorGroupDetailRequest(TestBase):
    """颜色组详情请求测试类"""
    
    def test_color_group_detail_request(self):
        """
        测试颜色组详情请求
        对应Java版本的 ColorGroupDetailRequestTest.testColorGroupDetailRequest() 方法
        """
        # 首先获取一个存在的颜色组ID
        list_request = ColorGroupListRequest()
        list_request.page = 1
        list_request.size = 1
        
        http_request, list_response = self.execute_request(list_request)
        self.assert_success(list_response, "获取颜色组列表失败")
        
        if not list_response.data or len(list_response.data) == 0:
            print("⚠️ 没有找到颜色组数据，跳过详情测试")
            return
            
        # 使用第一个颜色组的ID进行详情查询
        test_color_group_id = list_response.data[0].id
        
        request = ColorGroupDetailRequest()
        request.color_group_id = test_color_group_id
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "颜色组详情请求失败")
        
        # 验证颜色组ID正确（对应Java版本的Assert.isTrue）
        assert response.data.id == test_color_group_id, "颜色分组id错误"
        
        # 验证响应类型
        assert isinstance(response, ColorGroupDetailResponse), "响应类型不正确"
        
        print(f"✅ 颜色组详情获取成功")
        print(f"颜色组ID: {response.data.id}")
        print(f"颜色组名称: {response.data.name}")


class TestColorGroupListRequest(TestBase):
    """颜色组列表请求测试类"""
    
    def test_color_group_list_request(self):
        """
        测试颜色组列表请求
        对应Java版本的 ColorGroupListRequestTest.testColorGroupListRequest() 方法
        注意：根据Java版本，这个测试不调用assert_success，只验证数据不为空
        """
        request = ColorGroupListRequest()
        # 不设置过滤条件，获取所有颜色组
        
        http_request, response = self.execute_request(request)
        
        # 验证响应数据不为空（对应Java版本的Assert.notNull）
        # 注意：Java版本没有调用assert_success，只检查数据不为空
        assert response.data is not None, "Response data should not be null"
        
        # 验证响应类型
        assert isinstance(response, ColorGroupListResponse), "响应类型不正确"
        
        print(f"✅ 颜色组列表获取成功，找到 {len(response.data)} 个结果")
        
    def test_color_group_list_with_filter(self):
        """
        测试带过滤条件的颜色组列表请求
        """
        # 首先创建一个测试颜色组用于过滤测试
        save_request = ColorGroupSaveRequest()
        num = self.generate_random_number()
        test_name = f"测试分组{num}"
        
        save_dto = ColorGroupSaveDTO(name=test_name)
        save_request.color_group_save_dto = save_dto
        
        http_request, save_response = self.execute_request(save_request)
        self.assert_success(save_response, "创建测试颜色组失败")
        
        # 使用创建的颜色组名称进行过滤查询
        list_request = ColorGroupListRequest()
        list_request.name = test_name
        
        http_request, list_response = self.execute_request(list_request)
        
        # 验证响应数据不为空
        assert list_response.data is not None, "Response data should not be null"
        assert len(list_response.data) > 0, "应该找到匹配的颜色组"
        
        # 验证过滤结果正确
        found_match = any(item.name == test_name for item in list_response.data)
        assert found_match, f"没有找到名称为 '{test_name}' 的颜色组"
        
        print(f"✅ 颜色组过滤查询成功，找到 {len(list_response.data)} 个匹配结果")


# 提供测试实例的fixtures
@pytest.fixture
def color_group_save_test():
    return TestColorGroupSaveRequest()

@pytest.fixture
def color_group_update_test():
    return TestColorGroupUpdateRequest()

@pytest.fixture
def color_group_delete_test():
    return TestColorGroupDeleteRequest()

@pytest.fixture
def color_group_detail_test():
    return TestColorGroupDetailRequest()

@pytest.fixture
def color_group_list_test():
    return TestColorGroupListRequest()


# 集成测试函数
def test_color_group_save_integration(color_group_save_test):
    """集成测试：颜色组保存完整流程"""
    color_group_save_test.test_color_group_save_request()

def test_color_group_update_integration(color_group_update_test):
    """集成测试：颜色组更新完整流程"""
    color_group_update_test.test_update_color_group()

def test_color_group_delete_integration(color_group_delete_test):
    """集成测试：颜色组删除完整流程"""
    color_group_delete_test.test_delete_color_group()

def test_color_group_detail_integration(color_group_detail_test):
    """集成测试：颜色组详情完整流程"""
    color_group_detail_test.test_color_group_detail_request()

def test_color_group_list_integration(color_group_list_test):
    """集成测试：颜色组列表完整流程"""
    color_group_list_test.test_color_group_list_request()

def test_color_group_list_filter_integration(color_group_list_test):
    """集成测试：颜色组列表过滤流程"""
    color_group_list_test.test_color_group_list_with_filter()


if __name__ == "__main__":
    # 直接运行测试
    print("开始颜色组保存测试...")
    save_test = TestColorGroupSaveRequest()
    save_test.test_color_group_save_request()
    
    print("\n开始颜色组更新测试...")
    update_test = TestColorGroupUpdateRequest()
    update_test.test_update_color_group()
    
    print("\n开始颜色组删除测试...")
    delete_test = TestColorGroupDeleteRequest()
    delete_test.test_delete_color_group()
    
    print("\n开始颜色组详情测试...")
    detail_test = TestColorGroupDetailRequest()
    detail_test.test_color_group_detail_request()
    
    print("\n开始颜色组列表测试...")
    list_test = TestColorGroupListRequest()
    list_test.test_color_group_list_request()
    
    print("开始颜色组过滤测试...")
    list_test.test_color_group_list_with_filter()
    
    print("\n✅ 所有颜色组测试通过")