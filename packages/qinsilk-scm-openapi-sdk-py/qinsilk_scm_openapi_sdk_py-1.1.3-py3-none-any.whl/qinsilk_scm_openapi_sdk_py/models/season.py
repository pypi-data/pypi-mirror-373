"""
季节相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class SeasonSaveDTO:
    """季节保存数据传输对象"""
    
    def __init__(self):
        self.name = None  # 名称（必填）
        self.code = None  # 编码（必填）
        self.is_enable = None  # 启用状态，1-启用，0-禁用
        self.remark = None  # 备注
        self.show_order = None  # 排序

    def to_dict(self):
        return {
            'name': self.name,
            'code': self.code,
            'isEnable': self.is_enable,
            'remark': self.remark,
            'showOrder': self.show_order
        }


class SeasonUpdateDTO:
    """季节更新数据传输对象"""
    
    def __init__(self):
        self.id = None  # 季节ID（必填）
        self.name = None  # 名称
        self.code = None  # 编码
        self.is_enable = None  # 启用状态，1-启用，0-禁用
        self.remark = None  # 备注
        self.show_order = None  # 排序

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'isEnable': self.is_enable,
            'remark': self.remark,
            'showOrder': self.show_order
        }


class SeasonDetail:
    """季节详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.code = data.get('code')
        self.is_enable = data.get('isEnable')
        self.remark = data.get('remark')
        self.show_order = data.get('showOrder')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class SeasonSaveRequest(BaseRequest):
    """新增季节请求"""
    
    def __init__(self):
        super().__init__()
        self.season_save_dto = None

    def get_api_url(self):
        return "api/open/season/base/add"

    def get_version(self):
        return "1.2"
    
    def response_class(self):
        return SeasonDetailResponse

    def get_request_body(self):
        if self.season_save_dto:
            return {"seasonSaveDto": self.season_save_dto.to_dict()}
        return {}


class SeasonUpdateRequest(BaseRequest):
    """更新季节请求"""
    
    def __init__(self):
        super().__init__()
        self.season_update_dto = None

    def get_api_url(self):
        return "api/open/season/base/update"

    def get_version(self):
        return "1.2"
    
    def response_class(self):
        return SeasonDetailResponse

    def get_request_body(self):
        if self.season_update_dto:
            return {"seasonUpdateDto": self.season_update_dto.to_dict()}
        return {}


class SeasonDetailRequest(BaseRequest):
    """季节详情请求"""
    
    def __init__(self):
        super().__init__()
        self.season_id = None

    def get_api_url(self):
        return "api/open/season/base/get"

    def get_version(self):
        return "1.2"
    
    def response_class(self):
        return SeasonDetailResponse

    def get_request_body(self):
        return {"seasonId": self.season_id}


class SeasonDeleteRequest(BaseRequest):
    """删除季节请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 主键集合（必填）

    def get_api_url(self):
        return "api/open/season/base/delete"

    def get_version(self):
        return "1.2"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class SeasonListRequest(BaseRequest):
    """季节列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 季节名称
        self.code = None  # 季节编码
        self.is_enable = None  # 启用状态，1-启用，0-禁用
        self.remark = None  # 备注
        self.show_order = None  # 排序
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/season/base/list"

    def get_version(self):
        return "1.2"
    
    def response_class(self):
        return SeasonListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        if self.code:
            body["code"] = self.code
        if self.is_enable is not None:
            body["isEnable"] = self.is_enable
        if self.remark:
            body["remark"] = self.remark
        if self.show_order is not None:
            body["showOrder"] = self.show_order
        return body


class SeasonDetailResponse(BaseResponse):
    """季节详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = SeasonDetail(response_data['data'])
        else:
            self.data = None


class SeasonListResponse(BaseResponse):
    """季节列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [SeasonDetail(item) for item in response_data['data']]
        else:
            self.data = []