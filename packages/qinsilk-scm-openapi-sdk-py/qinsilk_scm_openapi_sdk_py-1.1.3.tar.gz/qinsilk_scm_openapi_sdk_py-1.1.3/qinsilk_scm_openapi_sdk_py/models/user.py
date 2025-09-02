"""
用户相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class UserSaveDTO:
    """用户保存数据传输对象"""
    
    def __init__(self):
        self.work_sn = None  # 工号（必填）
        self.login_name = None  # 登陆名（必填）
        self.account_type = None  # 是否子账号，0：主账号，1：子账号，2：微信账号
        self.name = None  # 真实姓名（必填）
        self.phone = None  # 手机号
        self.department_id = None  # 部门Id
        self.position_id = None  # 职位Id
        self.remark = None  # 备注
        self.bank_card = None  # 银行卡号

    def to_dict(self):
        return {
            'workSn': self.work_sn,
            'loginName': self.login_name,
            'accountType': self.account_type,
            'name': self.name,
            'phone': self.phone,
            'departmentId': self.department_id,
            'positionId': self.position_id,
            'remark': self.remark,
            'bankCard': self.bank_card
        }


class UserUpdateDTO:
    """用户更新数据传输对象"""
    
    def __init__(self):
        self.id = None  # 用户ID（必填）
        self.work_sn = None  # 工号
        self.login_name = None  # 登陆名
        self.account_type = None  # 是否子账号，0：主账号，1：子账号，2：微信账号
        self.name = None  # 真实姓名
        self.phone = None  # 手机号
        self.department_id = None  # 部门Id
        self.position_id = None  # 职位Id
        self.remark = None  # 备注
        self.bank_card = None  # 银行卡号

    def to_dict(self):
        return {
            'id': self.id,
            'workSn': self.work_sn,
            'loginName': self.login_name,
            'accountType': self.account_type,
            'name': self.name,
            'phone': self.phone,
            'departmentId': self.department_id,
            'positionId': self.position_id,
            'remark': self.remark,
            'bankCard': self.bank_card
        }


class UserDetail:
    """用户详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.work_sn = data.get('workSn')
        self.login_name = data.get('loginName')
        self.account_type = data.get('accountType')
        self.name = data.get('name')
        self.phone = data.get('phone')
        self.department_id = data.get('departmentId')
        self.position_id = data.get('positionId')
        self.remark = data.get('remark')
        self.bank_card = data.get('bankCard')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class UserSaveRequest(BaseRequest):
    """新增用户请求"""
    
    def __init__(self):
        super().__init__()
        self.user_save_dto = None

    def get_api_url(self):
        return "api/open/user/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return UserDetailResponse
    
    def get_request_body(self):
        if self.user_save_dto:
            return {"userSaveDto": self.user_save_dto.to_dict()}
        return {}


class UserDeleteRequest(BaseRequest):
    """删除用户请求"""
    
    def __init__(self):
        super().__init__()
        self.user_id = None

    def get_api_url(self):
        return "api/open/user/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse
    
    def get_request_body(self):
        return {"userId": self.user_id}


class UserDetailRequest(BaseRequest):
    """用户详情请求"""
    
    def __init__(self):
        super().__init__()
        self.id = None  # 用户ID

    def get_api_url(self):
        return "api/open/user/base/detail"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return UserDetailResponse
    
    def get_request_body(self):
        return {"id": self.id}


class UserUpdateRequest(BaseRequest):
    """更新用户请求"""
    
    def __init__(self):
        super().__init__()
        self.user_update_dto = None

    def get_api_url(self):
        return "api/open/user/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return UserDetailResponse
    
    def get_request_body(self):
        if self.user_update_dto:
            return {"userUpdateDto": self.user_update_dto.to_dict()}
        return {}


class UserListRequest(BaseRequest):
    """用户列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 用户名称
        self.phone = None  # 手机号
        self.login_name = None  # 登录名
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/user/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return UserListResponse
    
    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        if self.phone:
            body["phone"] = self.phone
        if self.login_name:
            body["loginName"] = self.login_name
        return body


class UserDetailResponse(BaseResponse):
    """用户详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = UserDetail(response_data['data'])
        else:
            self.data = None


class UserListResponse(BaseResponse):
    """用户列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [UserDetail(item) for item in response_data['data']]
        else:
            self.data = []