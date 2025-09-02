"""
订单相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse
from datetime import datetime


class ProduceOrderDTO:
    """生产单数据传输对象"""
    
    def __init__(self):
        self.orders_sn = None  # 单号
        self.produce_batch_sn = None  # 生产批次号
        self.type = None  # 生产类型，1-自主生产 2-单工序外发 3-委外加工 4-成品采购（必填）
        self.supplier_id = None  # 供应商id
        self.order_type = None  # 订单类型id
        self.storehouse_id = None  # 仓库id（必填）
        self.business_time = None  # 业务日期（必填）
        self.delivery_time = None  # 计划交货日期（必填）

    def to_dict(self):
        body = {
            'type': self.type,
            'storehouseId': self.storehouse_id,
        }
        if self.orders_sn:
            body['ordersSn'] = self.orders_sn
        if self.produce_batch_sn:
            body['produceBatchSn'] = self.produce_batch_sn
        if self.supplier_id:
            body['supplierId'] = self.supplier_id
        if self.order_type:
            body['orderType'] = self.order_type
        if self.business_time:
            if isinstance(self.business_time, datetime):
                body['businessTime'] = self.business_time.isoformat()
            else:
                body['businessTime'] = self.business_time
        if self.delivery_time:
            if isinstance(self.delivery_time, datetime):
                body['deliveryTime'] = self.delivery_time.isoformat()
            else:
                body['deliveryTime'] = self.delivery_time
        return body


class ProduceOrderDtDTO:
    """生产单商品数据传输对象"""
    
    def __init__(self):
        self.goods_id = None  # 商品ID
        self.sku_id = None  # 商品SKU ID
        self.number = None  # 数量
        self.remark = None  # 备注

    def to_dict(self):
        return {
            'goodsId': self.goods_id,
            'skuId': self.sku_id,
            'number': self.number,
            'remark': self.remark
        }


class ProduceOrderDetail:
    """生产单详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        # 使用驼峰命名风格，直接从原始响应数据中获取字段
        self.id = data.get('id')
        self.orders_sn = data.get('ordersSn')
        self.produce_batch_sn = data.get('produceBatchSn')
        self.type = data.get('type')
        self.supplier_id = data.get('supplierId')
        self.order_type = data.get('orderType')
        self.storehouse_id = data.get('storehouseId')
        self.business_time = data.get('businessTime')
        self.delivery_time = data.get('deliveryTime')
        self.status = data.get('status')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class ProduceOrderSaveRequest(BaseRequest):
    """创建生产单请求"""
    
    def __init__(self):
        super().__init__()
        self.produce = None  # ProduceOrderDTO
        self.order_goods_list = None  # List[ProduceOrderDtDTO]

    def get_api_url(self):
        return "api/open/order/produce/save"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceOrderSaveResponse

    def get_request_body(self):
        body = {}
        if self.produce:
            body['produce'] = self.produce.to_dict()
        if self.order_goods_list:
            body['orderGoodsList'] = [item.to_dict() for item in self.order_goods_list]
        return body


class ProduceOrderDetailRequest(BaseRequest):
    """生产单详情请求"""
    
    def __init__(self):
        super().__init__()
        self.order_sn = None  # 单号

    def get_api_url(self):
        return "api/open/order/produce/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceOrderDetailResponse

    def get_request_body(self):
        return {"orderSn": self.order_sn}


class ProduceOrderListRequest(BaseRequest):
    """生产单列表请求"""
    
    def __init__(self):
        super().__init__()
        self.order_sn = None  # 单号
        self.type = None  # 生产类型
        self.status = None  # 状态
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/order/produce/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceOrderListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.order_sn:
            body["orderSn"] = self.order_sn
        if self.type:
            body["type"] = self.type
        if self.status:
            body["status"] = self.status
        return body


class ProduceOrderSaveResponse(BaseResponse):
    """创建生产单响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = ProduceOrderDetail(response_data['data'])
        else:
            self.data = None


class ProduceOrderDetailResponse(BaseResponse):
    """生产单详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = ProduceOrderDetail(response_data['data'])
        else:
            self.data = None


class ProduceOrderListResponse(BaseResponse):
    """生产单列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [ProduceOrderDetail(item) for item in response_data['data']]
        else:
            self.data = []