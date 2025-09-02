"""
物料类型相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class MaterialTypeSaveDTO:
    """物料类型保存数据传输对象"""
    
    def __init__(self):
        self.name = None  # 物料类型名称（必填）
        self.state = None  # 启用状态 -1-启用 -0-拒绝
        self.show_order = None  # 排序
        self.remark = None  # 备注
        self.type = None  # 物料类型：1-面料，0-辅料，2-其他
        self.enable_fabric_type = None  # 启用面料属性:1-启用，0-关闭

    def to_dict(self):
        return {
            'name': self.name,
            'state': self.state,
            'showOrder': self.show_order,
            'remark': self.remark,
            'type': self.type,
            'enableFabricType': self.enable_fabric_type
        }


class MaterialTypeUpdateDTO:
    """物料类型更新数据传输对象"""
    
    def __init__(self):
        self.id = None  # 物料类型ID（必填）
        self.name = None  # 物料类型名称
        self.state = None  # 启用状态 -1-启用 -0-拒绝
        self.show_order = None  # 排序
        self.remark = None  # 备注
        self.type = None  # 物料类型：1-面料，0-辅料，2-其他
        self.enable_fabric_type = None  # 启用面料属性:1-启用，0-关闭

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'showOrder': self.show_order,
            'remark': self.remark,
            'type': self.type,
            'enableFabricType': self.enable_fabric_type
        }


class MaterialTypeDetail:
    """物料类型详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.state = data.get('state')
        self.show_order = data.get('showOrder')
        self.remark = data.get('remark')
        self.type = data.get('type')
        self.enable_fabric_type = data.get('enableFabricType')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class MaterialTypeSaveRequest(BaseRequest):
    """新增物料类型请求"""
    
    def __init__(self):
        super().__init__()
        self.material_type_save_dto = None

    def get_api_url(self):
        return "api/open/material/type/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialTypeDetailResponse

    def get_request_body(self):
        if self.material_type_save_dto:
            return {"materialTypeSaveDto": self.material_type_save_dto.to_dict()}
        return {}


class MaterialTypeUpdateRequest(BaseRequest):
    """更新物料类型请求"""
    
    def __init__(self):
        super().__init__()
        self.material_type_update_dto = None

    def get_api_url(self):
        return "api/open/material/type/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialTypeDetailResponse

    def get_request_body(self):
        if self.material_type_update_dto:
            return {"materialTypeUpdateDto": self.material_type_update_dto.to_dict()}
        return {}


class MaterialTypeDetailRequest(BaseRequest):
    """物料类型详情请求"""
    
    def __init__(self):
        super().__init__()
        self.material_type_id = None

    def get_api_url(self):
        return "api/open/material/type/base/detail"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialTypeDetailResponse

    def get_request_body(self):
        return {"materialTypeId": self.material_type_id}


class MaterialTypeDeleteRequest(BaseRequest):
    """删除物料类型请求"""
    
    def __init__(self):
        super().__init__()
        self.material_type_id = None

    def get_api_url(self):
        return "api/open/material/type/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse

    def get_request_body(self):
        return {"materialTypeId": self.material_type_id}


class MaterialTypeListRequest(BaseRequest):
    """物料类型列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 物料类型名称
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/material/type/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialTypeListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class MaterialTypeDetailResponse(BaseResponse):
    """物料类型详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = MaterialTypeDetail(response_data['data'])
        else:
            self.data = None


class MaterialTypeListResponse(BaseResponse):
    """物料类型列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [MaterialTypeDetail(item) for item in response_data['data']]
        else:
            self.data = []