"""
尺码更新、删除、详情、列表请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.size.base.SizeUpdateRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.base.SizeDeleteRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.base.SizeDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.size.base.SizeListRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.size import (
    SizeListRequest, SizeListResponse,
    SizeDetailRequest, SizeDetailResponse,
    SizeUpdateRequest, SizeUpdateDTO,
    SizeDeleteRequest,
    SizeSaveRequest, SizeSaveDTO,
    SizeGroupListRequest, SizeGroupListResponse
)
from qinsilk_scm_openapi_sdk_py.models.base import BaseResponse
from tests.test_base import TestBase


class TestSizeUpdateRequest(TestBase):
    """尺码更新请求测试类"""
    
    def test_update_size(self):
        """
        测试更新尺码
        对应Java版本的 SizeUpdateRequestTest.testUpdateSize() 方法
        """
        # 首先获取尺码组列表，找到可用的尺码组
        size_group_list_request = SizeGroupListRequest()
        size_group_list_request.page = 1
        size_group_list_request.size = 1
        
        http_request, size_group_list_response = self.execute_request(size_group_list_request)
        self.assert_success(size_group_list_response, "获取尺码组列表失败")
        assert len(size_group_list_response.data) > 0, "No size group to use"
        
        size_group_id = size_group_list_response.data[0].id
        
        # 创建一个尺码用于更新
        add_request = SizeSaveRequest()
        num = self.generate_random_number()
        
        size_save_dto = SizeSaveDTO(
            name=f"测试尺码{num}",
            size_group_id=757,  # 对应Java版本的757L
            is_default=0
        )
        add_request.size_save_dto = size_save_dto
        
        http_request, add_response = self.execute_request(add_request)
        self.assert_success(add_response, "创建测试尺码失败")
        
        size_data = add_response.data
        
        # 创建更新请求
        request = SizeUpdateRequest()
        num2 = self.generate_random_number()
        
        # 创建更新DTO - 对应Java版本的SizeUpdateDTO
        size_update_dto = SizeUpdateDTO(
            id=size_data.id,
            name=f"测试尺码(修改){num2}",
            size_group_id=size_group_id,
            is_default=size_data.is_default
        )
        request.size_update_dto = size_update_dto
        
        # 执行更新请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "尺码更新请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, SizeDetailResponse), "响应类型不正确"
        
        print(f"✅ 尺码更新成功，ID: {response.data.id}")
        print(f"更新后尺码名称: {response.data.name}")


class TestSizeDeleteRequest(TestBase):
    """尺码删除请求测试类"""
    
    def test_delete_size(self):
        """
        测试删除尺码
        对应Java版本的 SizeDeleteRequestTest.testDeleteSize() 方法
        """
        # 首先获取尺码组列表，找到可用的尺码组
        size_group_list_request = SizeGroupListRequest()
        size_group_list_request.page = 1
        size_group_list_request.size = 1
        
        http_request, size_group_list_response = self.execute_request(size_group_list_request)
        self.assert_success(size_group_list_response, "获取尺码组列表失败")
        assert len(size_group_list_response.data) > 0, "No size group to use"
        
        size_group_id = size_group_list_response.data[0].id
        
        # 创建一个尺码用于删除
        save_request = SizeSaveRequest()
        num = self.generate_random_number()
        
        save_dto = SizeSaveDTO(
            name=f"待删除尺码{num}",
            size_group_id=size_group_id,
            is_default=0)