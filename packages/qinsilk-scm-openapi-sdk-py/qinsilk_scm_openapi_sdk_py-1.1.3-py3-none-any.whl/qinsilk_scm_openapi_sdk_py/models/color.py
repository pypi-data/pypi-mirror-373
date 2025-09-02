"""
颜色相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


# #################################################################
# Color Group
# #################################################################

class ColorGroupSaveDTO:
    """颜色组保存数据传输对象"""
    
    def __init__(self, name=None, id=None):
        self.name = name  # 颜色组名称（必填）
        self.id = id

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id
        }


class ColorGroupDetail:
    """颜色组详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')


class ColorGroupSaveRequest(BaseRequest):
    """新增颜色组请求"""
    
    def __init__(self):
        super().__init__()
        self.color_group_save_dto = None

    def get_api_url(self):
        return "api/open/color/group/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorGroupDetailResponse

    def get_request_body(self):
        if self.color_group_save_dto:
            return {"colorGroupSaveDto": self.color_group_save_dto.to_dict()}
        return {}


class ColorGroupDetailRequest(BaseRequest):
    """颜色组详情请求"""
    
    def __init__(self):
        super().__init__()
        self.color_group_id = None

    def get_api_url(self):
        return "api/open/color/group/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorGroupDetailResponse

    def get_request_body(self):
        return {"colorGroupId": self.color_group_id}


class ColorGroupListRequest(BaseRequest):
    """颜色组列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 颜色组名称
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/color/group/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorGroupListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class ColorGroupUpdateDTO:
    """颜色组更新数据传输对象"""
    
    def __init__(self, id=None, name=None):
        self.id = id  # 颜色组ID（必填）
        self.name = name  # 颜色组名称（必填）

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class ColorGroupUpdateRequest(BaseRequest):
    """更新颜色组请求"""
    
    def __init__(self):
        super().__init__()
        self.color_group_update_dto = None

    def get_api_url(self):
        return "api/open/color/group/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorGroupDetailResponse

    def get_request_body(self):
        if self.color_group_update_dto:
            return {"colorGroupUpdateDto": self.color_group_update_dto.to_dict()}
        return {}


class ColorGroupDeleteRequest(BaseRequest):
    """删除颜色组请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 要删除的颜色组ID列表

    def get_api_url(self):
        return "api/open/color/group/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class ColorGroupDetailResponse(BaseResponse):
    """颜色组详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = ColorGroupDetail(response_data['data'])
        else:
            self.data = None


class ColorGroupListResponse(BaseResponse):
    """颜色组列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [ColorGroupDetail(item) for item in response_data['data']]
        else:
            self.data = []


# #################################################################
# Color Base
# #################################################################

class ColorBaseSaveDTO:
    """颜色保存数据传输对象"""
    
    def __init__(self, name=None, color_group_id=None, color_value=None, show_order=None, status=None, is_default=None, remark=None):
        self.name = name  # 颜色名称（必填）
        self.color_group_id = color_group_id  # 颜色组ID（必填）
        self.color_value = color_value  # 颜色值
        self.show_order = show_order  # 排序
        self.status = status  # 状态
        self.is_default = is_default  # 是否默认
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'name': self.name,
            'colorGroupId': self.color_group_id,
            'colorValue': self.color_value,
            'showOrder': self.show_order,
            'status': self.status,
            'isDefault': self.is_default,
            'remark': self.remark
        }


class ColorBaseDetail:
    """颜色详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.color_value = data.get('colorValue')
        self.color_group_id = data.get('colorGroupId')
        self.show_order = data.get('showOrder')
        self.status = data.get('status')
        self.is_default = data.get('isDefault')
        self.remark = data.get('remark')


class ColorBaseSaveRequest(BaseRequest):
    """新增颜色请求"""
    
    def __init__(self):
        super().__init__()
        self.color_save_dto = None

    def get_api_url(self):
        return "api/open/color/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorBaseDetailResponse

    def get_request_body(self):
        if self.color_save_dto:
            return {"colorSaveDto": self.color_save_dto.to_dict()}
        return {}


class ColorBaseDetailRequest(BaseRequest):
    """颜色详情请求"""
    
    def __init__(self):
        super().__init__()
        self.color_id = None

    def get_api_url(self):
        return "api/open/color/base/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorBaseDetailResponse

    def get_request_body(self):
        return {"colorId": self.color_id}


class ColorBaseListRequest(BaseRequest):
    """颜色列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 颜色名称
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/color/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorBaseListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class ColorBaseDetailResponse(BaseResponse):
    """颜色详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = ColorBaseDetail(response_data['data'])
        else:
            self.data = None


class ColorBaseUpdateDTO:
    """颜色更新数据传输对象"""
    
    def __init__(self, id=None, name=None, color_group_id=None, color_value=None, show_order=None, status=None, is_default=None, remark=None):
        self.id = id  # 颜色ID（必填）
        self.name = name  # 颜色名称（必填）
        self.color_group_id = color_group_id  # 颜色组ID（必填）
        self.color_value = color_value  # 颜色值
        self.show_order = show_order  # 排序
        self.status = status  # 状态
        self.is_default = is_default  # 是否默认
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'colorGroupId': self.color_group_id,
            'colorValue': self.color_value,
            'showOrder': self.show_order,
            'status': self.status,
            'isDefault': self.is_default,
            'remark': self.remark
        }


class ColorBaseUpdateRequest(BaseRequest):
    """更新颜色请求"""
    
    def __init__(self):
        super().__init__()
        self.color_update_dto = None

    def get_api_url(self):
        return "api/open/color/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorBaseDetailResponse

    def get_request_body(self):
        if self.color_update_dto:
            return {"colorUpdateDto": self.color_update_dto.to_dict()}
        return {}


class ColorBaseDeleteRequest(BaseRequest):
    """删除颜色请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 要删除的颜色ID列表

    def get_api_url(self):
        return "api/open/color/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class ColorBaseListRequest(BaseRequest):
    """颜色列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 颜色名称
        self.value = None  # 颜色值
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/color/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ColorBaseListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        if self.value:
            body["value"] = self.value
        return body


class ColorBaseDetailResponse(BaseResponse):
    """颜色详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = ColorBaseDetail(response_data['data'])
        else:
            self.data = None


class ColorBaseListResponse(BaseResponse):
    """颜色列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [ColorBaseDetail(item) for item in response_data['data']]
        else:
            self.data = []