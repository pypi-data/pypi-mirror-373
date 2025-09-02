"""仓库相关的API请求和响应模型"""
from .base import BaseRequest, BaseResponse


class StorehouseSaveDTO:
    """仓库保存数据传输对象"""
    
    def __init__(self):
        self.name = None  # 名称（必填）
        self.type = None  # 类型（必填）

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type
        }


class StorehouseUpdateDTO:
    """仓库更新数据传输对象"""
    
    def __init__(self):
        self.id = None  # 仓库ID（必填）
        self.name = None  # 名称
        self.type = None  # 类型

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type
        }


class StorehouseDetail:
    """仓库详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.type = data.get('type')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class StorehouseSaveRequest(BaseRequest):
    """新增仓库请求"""
    
    def __init__(self):
        super().__init__()
        self.storehouse_save_dto = None

    def get_api_url(self):
        return "api/open/storehouse/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return StorehouseDetailResponse

    def get_request_body(self):
        if self.storehouse_save_dto:
            return {"storehouseSaveDto": self.storehouse_save_dto.to_dict()}
        return {}


class StorehouseUpdateRequest(BaseRequest):
    """更新仓库请求"""
    
    def __init__(self):
        super().__init__()
        self.storehouse_update_dto = None

    def get_api_url(self):
        return "api/open/storehouse/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return StorehouseDetailResponse

    def get_request_body(self):
        if self.storehouse_update_dto:
            return {"storehouseUpdateDto": self.storehouse_update_dto.to_dict()}
        return {}


class StorehouseDetailRequest(BaseRequest):
    """仓库详情请求"""
    
    def __init__(self):
        super().__init__()
        self.storehouse_id = None

    def get_api_url(self):
        return "api/open/storehouse/base/detail"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return StorehouseDetailResponse

    def get_request_body(self):
        return {"storehouseId": self.storehouse_id}


class StorehouseDeleteRequest(BaseRequest):
    """删除仓库请求"""
    
    def __init__(self):
        super().__init__()
        self.storehouse_id = None

    def get_api_url(self):
        return "api/open/storehouse/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse

    def get_request_body(self):
        return {"storehouseId": self.storehouse_id}


class StorehouseListRequest(BaseRequest):
    """仓库列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 仓库名称
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/storehouse/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return StorehouseListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class StorehouseDetailResponse(BaseResponse):
    """仓库详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = StorehouseDetail(response_data['data'])
        else:
            self.data = None


class StorehouseListResponse(BaseResponse):
    """仓库列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [StorehouseDetail(item) for item in response_data['data']]
        else:
            self.data = []