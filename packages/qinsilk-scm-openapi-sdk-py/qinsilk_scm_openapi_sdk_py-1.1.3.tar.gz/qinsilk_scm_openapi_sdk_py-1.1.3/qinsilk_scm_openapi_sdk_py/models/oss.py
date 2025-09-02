"""
OSS对象存储相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class SignedUrlData:
    """临时授权URL数据"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.file_suffix = data.get('fileSuffix')
        self.file_type = data.get('fileType')
        self.signed_url = data.get('signedUrl')
        self.module_flag = data.get('moduleFlag')
        self.content_type = data.get('contentType')
        self.url = data.get('url')
        self.store_name = data.get('storeName')
        self.file_name = data.get('fileName')


class ApplySignedUrlRequest(BaseRequest):
    """申请临时上传URL请求"""
    
    def __init__(self):
        super().__init__()
        self.file_suffix = None  # 文件后缀（必填）
        self.file_type = None  # 文件类型,图片-1 视频-2 通用-3（必填）
        self.module_flag = None  # 模块标识，不传则使用默认值：0
        self.content_type = None  # 内容类型（必填）
        self.file_name = None  # 文件名
        self.http_method = None  # 上传文件类型 目前仅支持 PUT,POST（必填）

    def get_api_url(self):
        return "api/open/oss/apply/signedUrl"

    def get_version(self):
        return "1.1"
    
    def response_class(self):
        return ApplySignedUrlResponse

    def get_request_body(self):
        body = {
            'fileSuffix': self.file_suffix,
            'fileType': self.file_type,
            'contentType': self.content_type,
            'httpMethod': self.http_method
        }
        if self.module_flag is not None:
            body['moduleFlag'] = self.module_flag
        if self.file_name:
            body['fileName'] = self.file_name
        return body


class ApplySignedUrlResponse(BaseResponse):
    """申请临时授权URL响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = SignedUrlData(response_data['data'])
        else:
            self.data = None