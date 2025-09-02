"""
波段相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class RangesSaveDTO:
    """波段保存数据传输对象"""
    
    def __init__(self):
        self.name = None  # 名称（必填）
        self.show_order = None  # 排序
        self.remark = None  # 备注

    def to_dict(self):
        return {
            'name': self.name,
            'showOrder': self.show_order,
            'remark': self.remark
        }


class RangesUpdateDTO:
    """波段更新数据传输对象"""
    
    def __init__(self):
        self.id = None  # 波段ID（必填）
        self.name = None  # 名称
        self.show_order = None  # 排序
        self.remark = None  # 备注

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'showOrder': self.show_order,
            'remark': self.remark
        }


class RangesDetail:
    """波段详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.show_order = data.get('showOrder')
        self.remark = data.get('remark')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class RangesSaveRequest(BaseRequest):
    """新增波段请求"""
    
    def __init__(self):
        super().__init__()
        self.ranges_save_dto = None

    def get_api_url(self):
        return "api/open/ranges/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return RangesDetailResponse

    def get_request_body(self):
        if self.ranges_save_dto:
            return {"rangesSaveDto": self.ranges_save_dto.to_dict()}
        return {}


class RangesUpdateRequest(BaseRequest):
    """更新波段请求"""
    
    def __init__(self):
        super().__init__()
        self.ranges_update_dto = None

    def get_api_url(self):
        return "api/open/ranges/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return RangesDetailResponse

    def get_request_body(self):
        if self.ranges_update_dto:
            return {"rangesUpdateDto": self.ranges_update_dto.to_dict()}
        return {}


class RangesDetailRequest(BaseRequest):
    """波段详情请求"""
    
    def __init__(self):
        super().__init__()
        self.ranges_id = None

    def get_api_url(self):
        return "api/open/ranges/base/detail"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return RangesDetailResponse

    def get_request_body(self):
        return {"rangesId": self.ranges_id}


class RangesDeleteRequest(BaseRequest):
    """删除波段请求"""
    
    def __init__(self):
        super().__init__()
        self.ranges_id = None

    def get_api_url(self):
        return "api/open/ranges/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse

    def get_request_body(self):
        return {"rangesId": self.ranges_id}


class RangesListRequest(BaseRequest):
    """波段列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 波段名称
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/ranges/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return RangesListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        return body


class RangesDetailResponse(BaseResponse):
    """波段详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = RangesDetail(response_data['data'])
        else:
            self.data = None


class RangesListResponse(BaseResponse):
    """波段列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [RangesDetail(item) for item in response_data['data']]
        else:
            self.data = []