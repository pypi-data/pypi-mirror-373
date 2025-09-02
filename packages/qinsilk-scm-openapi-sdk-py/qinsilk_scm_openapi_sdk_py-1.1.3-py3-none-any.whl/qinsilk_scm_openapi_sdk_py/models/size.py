"""
尺码相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


# #################################################################
# Size Group
# #################################################################

class SizeGroupSaveDTO:
    """尺码组保存数据传输对象"""
    
    def __init__(self, name=None, id=None):
        self.name = name  # 尺码组名称（必填）
        self.id = id

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id
        }


class SizeGroupDetail:
    """尺码组详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')


class SizeGroupSaveRequest(BaseRequest):
    """新增尺码组请求"""
    
    def __init__(self):
        super().__init__()
        self.size_group_save_dto = None

    def get_api_url(self):
        return "api/open/size/group/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeGroupDetailResponse

    def get_request_body(self):
        if self.size_group_save_dto:
            return {"sizeGroupSaveDTO": self.size_group_save_dto.to_dict()}
        return {}


class SizeGroupDetailRequest(BaseRequest):
    """尺码组详情请求"""
    
    def __init__(self):
        super().__init__()
        self.size_group_id = None

    def get_api_url(self):
        return "api/open/size/group/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeGroupDetailResponse

    def get_request_body(self):
        return {"sizeGroupId": self.size_group_id}


class SizeGroupListRequest(BaseRequest):
    """尺码组列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 尺码组名称
        self.page = 1
        self.size = 10  # 修复：改为与Java版本一致的默认值10

    def get_api_url(self):
        return "api/open/size/group/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeGroupListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class SizeGroupUpdateDTO:
    """尺码组更新数据传输对象"""
    
    def __init__(self, id=None, name=None):
        self.id = id  # 尺码组ID（必填）
        self.name = name  # 尺码组名称（必填）

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class SizeGroupUpdateRequest(BaseRequest):
    """更新尺码组请求"""
    
    def __init__(self):
        super().__init__()
        self.size_group_update_dto = None

    def get_api_url(self):
        return "api/open/size/group/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeGroupDetailResponse

    def get_request_body(self):
        if self.size_group_update_dto:
            return {"sizeGroupUpdateDto": self.size_group_update_dto.to_dict()}
        return {}


class SizeGroupDeleteRequest(BaseRequest):
    """删除尺码组请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 要删除的尺码组ID列表

    def get_api_url(self):
        return "api/open/size/group/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class SizeGroupDetailResponse(BaseResponse):
    """尺码组详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = SizeGroupDetail(response_data['data'])
        else:
            self.data = None


class SizeGroupListResponse(BaseResponse):
    """尺码组列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [SizeGroupDetail(item) for item in response_data['data']]
        else:
            self.data = []


# #################################################################
# Size Base
# #################################################################

class SizeSaveDTO:
    """尺码保存数据传输对象"""
    
    def __init__(self, name=None, size_group_id=None, is_default=None, show_order=None, status=None, remark=None):
        self.name = name  # 尺码名称（必填）
        self.size_group_id = size_group_id  # 尺码组ID（必填）
        self.is_default = is_default  # 是否默认（必填）
        self.show_order = show_order  # 排序
        self.status = status  # 状态
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'name': self.name,
            'sizeGroupId': self.size_group_id,
            'isDefault': self.is_default,
            'showOrder': self.show_order,
            'status': self.status,
            'remark': self.remark
        }


class SizeDetail:
    """尺码详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.size_group_id = data.get('sizeGroupId')
        self.show_order = data.get('showOrder')
        self.status = data.get('status')
        self.is_default = data.get('isDefault')
        self.remark = data.get('remark')


class SizeSaveRequest(BaseRequest):
    """新增尺码请求"""
    
    def __init__(self):
        super().__init__()
        self.size_save_dto = None

    def get_api_url(self):
        return "api/open/size/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeDetailResponse

    def get_request_body(self):
        if self.size_save_dto:
            return {"sizeSaveDto": self.size_save_dto.to_dict()}
        return {}


class SizeDetailRequest(BaseRequest):
    """尺码详情请求"""
    
    def __init__(self):
        super().__init__()
        self.size_id = None

    def get_api_url(self):
        return "api/open/size/base/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeDetailResponse

    def get_request_body(self):
        return {"sizeId": self.size_id}


class SizeListRequest(BaseRequest):
    """尺码列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 尺码名称
        self.page = 1
        self.size = 10  # 修复：改为与Java版本一致的默认值10

    def get_api_url(self):
        return "api/open/size/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class SizeUpdateDTO:
    """尺码更新数据传输对象"""
    
    def __init__(self, id=None, name=None, size_group_id=None, is_default=None, show_order=None, status=None, remark=None):
        self.id = id  # 尺码ID（必填）
        self.name = name  # 尺码名称（必填）
        self.size_group_id = size_group_id  # 尺码组ID（必填）
        self.is_default = is_default  # 是否默认
        self.show_order = show_order  # 排序
        self.status = status  # 状态
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sizeGroupId': self.size_group_id,
            'isDefault': self.is_default,
            'showOrder': self.show_order,
            'status': self.status,
            'remark': self.remark
        }


class SizeUpdateRequest(BaseRequest):
    """更新尺码请求"""
    
    def __init__(self):
        super().__init__()
        self.size_update_dto = None

    def get_api_url(self):
        return "api/open/size/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SizeDetailResponse

    def get_request_body(self):
        if self.size_update_dto:
            return {"sizeUpdateDto": self.size_update_dto.to_dict()}
        return {}


class SizeDeleteRequest(BaseRequest):
    """删除尺码请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 要删除的尺码ID列表

    def get_api_url(self):
        return "api/open/size/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class SizeDetailResponse(BaseResponse):
    """尺码详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = SizeDetail(response_data['data'])
        else:
            self.data = None


class SizeListResponse(BaseResponse):
    """尺码列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [SizeDetail(item) for item in response_data['data']]
        else:
            self.data = []