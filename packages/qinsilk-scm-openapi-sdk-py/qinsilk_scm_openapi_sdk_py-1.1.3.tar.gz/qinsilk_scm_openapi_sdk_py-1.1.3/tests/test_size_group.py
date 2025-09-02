"""
尺码组相关请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.size.group.SizeGroupSaveRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.group.SizeGroupUpdateRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.group.SizeGroupDeleteRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.group.SizeGroupDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.group.SizeGroupListRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.size import (
    SizeGroupSaveRequest, SizeGroupSaveDTO, SizeGroupDetailResponse,
    SizeGroupUpdateRequest, SizeGroupUpdateDTO,
    SizeGroupDeleteRequest,
    SizeGroupDetailRequest,
    SizeGroupListRequest, SizeGroupListResponse
)
from qinsilk_scm_openapi_sdk_py.models.base import BaseResponse
from tests.test_base import TestBase


class TestSizeGroupSaveRequest(TestBase):
    """尺码组保存请求测试类"""
    
    def test_size_group_save_request(self):
        """
        测试尺码组保存请求
        对应Java版本的 SizeGroupSaveRequestTest.testSizeGroupSaveRequest() 方法
        """
        request = SizeGroupSaveRequest()
        
        # 创建尺码组保存DTO
        num = self.generate_random_number()
        dto = SizeGroupSaveDTO(name=f"测试尺码组{num}")
        request.size_group_save_dto = dto
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "尺码组保存请求失败")
        
        # 验证保存的实体有ID
        assert response.data.id is not None, "Saved entity should have an ID"
        
        # 验证响应类型
        assert isinstance(response, SizeGroupDetailResponse), "响应类型不正确"
        
        print(f"✅ 尺码组保存成功，ID: {response.data.id}")
        print(f"尺码组名称: {response.data.name}")


class TestSizeGroupUpdateRequest(TestBase):
    """尺码组更新请求测试类"""
    
    def test_update_size_group(self):
        """
        测试更新尺码组
        对应Java版本的 SizeGroupUpdateRequestTest.testUpdateSizeGroup() 方法
        """
        # 首先获取尺码组列表，找到要更新的尺码组
        list_request = SizeGroupListRequest()
        list_request.page = 1
        list_request.size = 1
        
        http_request, list_response = self.execute_request(list_request)
        self.assert_success(list_response, "获取尺码组列表失败")
        assert len(list_response.data) > 0, "No size group to update"
        
        # 获取第一个尺码组进行更新
        size_group_detail = list_response.data[0]
        
        # 创建更新请求
        request = SizeGroupUpdateRequest()
        num = self.generate_random_number()
        
        # 创建更新DTO
        size_group_update_dto = SizeGroupUpdateDTO(
            id=size_group_detail.id,
            name=f"测试尺码组(修改){num}"
        )
        request.size_group_update_dto = size_group_update_dto
        
        # 执行更新请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "尺码组更新请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, SizeGroupDetailResponse), "响应类型不正确"
        
        print(f"✅ 尺码组更新成功，ID: {response.data.id}")
        print(f"更新后尺码组名称: {response.data.name}")


class TestSizeGroupDeleteRequest(TestBase):
    """尺码组删除请求测试类"""
    
    def test_delete_size_group(self):
        """
        测试删除尺码组
        对应Java版本的 SizeGroupDeleteRequestTest.testDeleteSizeGroup() 方法
        """
        # 首先创建一个尺码组用于删除
        save_request = SizeGroupSaveRequest()
        num = self.generate_random_number()
        
        save_dto = SizeGroupSaveDTO(name=f"待删除尺码组{num}")
        save_request.size_group_save_dto = save_dto
        
        http_request, save_response = self.execute_request(save_request)
        self.assert_success(save_response, "Create size group failed")
        self.assert_response_code(save_response, "0")
        
        group_id = save_response.data.id
        print(f"创建待删除尺码组成功，ID: {group_id}")
        
        # 删除尺码组
        delete_request = SizeGroupDeleteRequest()
        delete_request.ids = [group_id]
        
        http_request, delete_response = self.execute_request(delete_request)
        
        # 验证删除响应
        self.assert_success(delete_response, "尺码组删除请求失败")
        self.assert_response_code(delete_response, "0")
        
        # 验证响应类型
        assert isinstance(delete_response, BaseResponse), "响应类型不正确"
        
        print(f"✅ 尺码组删除成功，ID: {group_id}")


class TestSizeGroupDetailRequest(TestBase):
    """尺码组详情请求测试类"""
    
    def test_size_group_detail_request(self):
        """
        测试尺码组详情请求
        对应Java版本的 SizeGroupDetailRequestTest.testSizeGroupDetailRequest() 方法
        """
        request = SizeGroupDetailRequest()
        request.size_group_id = 757  # 替换为有效的测试ID
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "尺码组详情请求失败")
        
        # 验证尺码组ID正确
        assert response.data.id == 757, "尺码组id错误"
        
        # 验证响应类型
        assert isinstance(response, SizeGroupDetailResponse), "响应类型不正确"
        
        print(f"✅ 尺码组详情获取成功")
        print(f"尺码组ID: {response.data.id}")
        print(f"尺码组名称: {response.data.name}")


class TestSizeGroupListRequest(TestBase):
    """尺码组列表请求测试类"""
    
    def test_size_group_list_request(self):
        """
        测试尺码组列表请求
        对应Java版本的 SizeGroupListRequestTest.testSizeGroupListRequest() 方法
        """
        request = SizeGroupListRequest()
        request.name = "测试尺码组"  # 示例过滤器
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "尺码组列表请求失败")
        
        # 验证响应数据不为空
        assert response.data is not None, "Response data should not be null"
        
        # 验证响应类型
        assert isinstance(response, SizeGroupListResponse), "响应类型不正确"
        
        print(f"✅ 尺码组列表获取成功，找到 {len(response.data)} 个结果")


# 提供测试实例的fixtures
@pytest.fixture
def size_group_save_test():
    return TestSizeGroupSaveRequest()

@pytest.fixture
def size_group_update_test():
    return TestSizeGroupUpdateRequest()

@pytest.fixture
def size_group_delete_test():
    return TestSizeGroupDeleteRequest()

@pytest.fixture
def size_group_detail_test():
    return TestSizeGroupDetailRequest()

@pytest.fixture
def size_group_list_test():
    return TestSizeGroupListRequest()


# 集成测试函数
def test_size_group_save_integration(size_group_save_test):
    """集成测试：尺码组保存完整流程"""
    size_group_save_test.test_size_group_save_request()

def test_size_group_update_integration(size_group_update_test):
    """集成测试：尺码组更新完整流程"""
    size_group_update_test.test_update_size_group()

def test_size_group_delete_integration(size_group_delete_test):
    """集成测试：尺码组删除完整流程"""
    size_group_delete_test.test_delete_size_group()

def test_size_group_detail_integration(size_group_detail_test):
    """集成测试：尺码组详情完整流程"""
    size_group_detail_test.test_size_group_detail_request()

def test_size_group_list_integration(size_group_list_test):
    """集成测试：尺码组列表完整流程"""
    size_group_list_test.test_size_group_list_request()


if __name__ == "__main__":
    # 直接运行测试
    print("开始尺码组保存测试...")
    save_test = TestSizeGroupSaveRequest()
    save_test.test_size_group_save_request()
    
    print("\n开始尺码组更新测试...")
    update_test = TestSizeGroupUpdateRequest()
    update_test.test_update_size_group()
    
    print("\n开始尺码组删除测试...")
    delete_test = TestSizeGroupDeleteRequest()
    delete_test.test_delete_size_group()
    
    print("\n开始尺码组详情测试...")
    detail_test = TestSizeGroupDetailRequest()
    detail_test.test_size_group_detail_request()
    
    print("\n开始尺码组列表测试...")
    list_test = TestSizeGroupListRequest()
    list_test.test_size_group_list_request()
    
    print("\n✅ 所有尺码组测试通过")