"""
报表相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


# ===== 生产单报表 =====

class ProduceOrderDTO:
    """生产单查询条件"""
    
    def __init__(self):
        self.orders_sn = None  # 单号

    def to_dict(self):
        return {
            'ordersSn': self.orders_sn
        }


class ProduceDetailReportListRequest(BaseRequest):
    """生产单明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.produce = None  # ProduceOrderDTO
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/produce/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.produce:
            body['produce'] = self.produce.to_dict()
        return body


class ProduceDetailReportListResponse(BaseResponse):
    """生产单明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


class ProduceWorkProcessListRequest(BaseRequest):
    """生产单工序列表请求"""
    
    def __init__(self):
        super().__init__()
        self.produce = None  # ProduceOrderDTO
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/produce/workprocess/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceWorkProcessListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.produce:
            body['produce'] = self.produce.to_dict()
        return body


class ProduceWorkProcessListResponse(BaseResponse):
    """生产单工序列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 商品工序报表 =====

class GoodsWorkProcessDetailListRequest(BaseRequest):
    """商品工序明细列表请求"""
    
    def __init__(self):
        super().__init__()
        self.goods_ids = None  # 商品id集合（必填）
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/goods/workprocess/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return GoodsWorkProcessDetailListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size,
            "goodsIds": self.goods_ids
        }
        return body


class GoodsWorkProcessDetailListResponse(BaseResponse):
    """商品工序明细列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 薪资计件报表 =====

class SalaryDetailReportListRequest(BaseRequest):
    """薪资计件明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.business_begin_time = None  # 业务起始时间（必填）
        self.business_end_time = None  # 业务结束时间（必填）
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/salary/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SalaryDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size,
            "businessBeginTime": self.business_begin_time,
            "businessEndTime": self.business_end_time
        }
        return body


class SalaryDetailReportListResponse(BaseResponse):
    """薪资计件明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 采购单报表 =====

class MaterialPurchaseDetailReportListRequest(BaseRequest):
    """物料采购明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.purchase_orders_sn = None  # 采购单号
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/material/purchase/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPurchaseDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.purchase_orders_sn:
            body['purchaseOrdersSn'] = self.purchase_orders_sn
        return body


class MaterialPurchaseDetailReportListResponse(BaseResponse):
    """物料采购明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 领料单报表 =====

class MaterialPickDetailReportListRequest(BaseRequest):
    """领料单明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/pick/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPickDetailReportListResponse

    def get_request_body(self):
        return {
            "page": self.page,
            "size": self.size
        }


class MaterialPickDetailReportListResponse(BaseResponse):
    """领料单明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []