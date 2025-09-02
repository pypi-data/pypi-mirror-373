"""
物料相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class MaterialDetail:
    """物料详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.name = data.get('name')
        self.type = data.get('type')
        self.type_id = data.get('typeId')
        self.sn = data.get('sn')
        self.barcode = data.get('barcode')
        self.category_id = data.get('categoryId')
        self.unit_id = data.get('unitId')
        self.price = data.get('price')
        self.composition = data.get('composition')
        self.post_process = data.get('postProcess')
        self.part = data.get('part')
        self.fabric_width = data.get('fabricWidth')
        self.gram_weight = data.get('gramWeight')
        self.qunce = data.get('qunce')
        self.roll_weight = data.get('rollWeight')
        self.net_weight = data.get('netWeight')
        self.meter_output = data.get('meterOutput')
        self.paper_bucket = data.get('paperBucket')
        self.empty_gap = data.get('emptyGap')
        self.empty_gap_rate = data.get('emptyGapRate')
        self.default_supplier_id = data.get('defaultSupplierId')
        self.supplier_sn = data.get('supplierSn')
        self.multiplying_power = data.get('multiplyingPower')
        self.round_way = data.get('roundWay')
        self.state = data.get('state')
        self.remark = data.get('remark')
        self.img_url = data.get('imgUrl')
        self.enable_property = data.get('enableProperty')
        self.enable_sku = data.get('enableSku')
        self.enable_sku_price = data.get('enableSkuPrice')
        self.handler_id = data.get('handlerId')
        self.last_handler_id = data.get('lastHandlerId')
        self.loss_rate = data.get('lossRate')
        self.shrink_rate = data.get('shrinkRate')
        self.fabric_type = data.get('fabricType')
        self.loss_rate_stair_enable = data.get('lossRateStairEnable')
        self.loss_rate_stair_type = data.get('lossRateStairType')


class MaterialListRequest(BaseRequest):
    """物料列表请求"""
    
    def __init__(self):
        super().__init__()
        self.material_sn = None
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/material/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.material_sn:
            body["materialSn"] = self.material_sn
        return body


class MaterialDetailRequest(BaseRequest):
    """物料详情请求"""
    
    def __init__(self):
        super().__init__()
        self.material_id = None

    def get_api_url(self):
        return "api/open/material/base/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialDetailResponse

    def get_request_body(self):
        return {"materialId": self.material_id}


class MaterialListResponse(BaseResponse):
    """物料列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [MaterialDetail(item) for item in response_data['data']]
        else:
            self.data = []


class MaterialDetailResponse(BaseResponse):
    """物料详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = MaterialDetail(response_data['data'])
        else:
            self.data = None


# #################################################################
# Material Purchase
# #################################################################

class MaterialPurchaseDetail:
    """物料采购详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        # 使用驼峰命名风格，直接从原始响应数据中获取字段
        self.orders_sn = data.get('ordersSn')
        self.group_orders_sn = data.get('groupOrdersSn')
        self.count_rule = data.get('countRule')
        self.supplier_id = data.get('supplierId')
        self.storehouse_id = data.get('storehouseId')
        self.payment = data.get('payment')
        self.total_wipe_zero = data.get('totalWipeZero')
        self.account_id = data.get('accountId')
        self.remark = data.get('remark')
        self.handler_id = data.get('handlerId')
        self.last_handler_id = data.get('lastHandlerId')
        self.state = data.get('state')
        self.business_time = data.get('businessTime')
        self.expect_time = data.get('expectTime')


class MaterialPurchaseListRequest(BaseRequest):
    """物料采购列表请求"""
    
    def __init__(self):
        super().__init__()
        self.order_sn = None
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/material/purchase/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPurchaseListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.order_sn:
            body["orderSn"] = self.order_sn
        return body


class MaterialPurchaseDetailRequest(BaseRequest):
    """物料采购详情请求"""
    
    def __init__(self):
        super().__init__()
        self.order_sn = None  # 订单号

    def get_api_url(self):
        return "api/open/material/purchase/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPurchaseDetailResponse

    def get_request_body(self):
        return {"orderSn": self.order_sn}


class MaterialPurchaseListResponse(BaseResponse):
    """物料采购列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [MaterialPurchaseDetail(item) for item in response_data['data']]
        else:
            self.data = []


class MaterialPurchaseDetailResponse(BaseResponse):
    """物料采购详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = MaterialPurchaseDetail(response_data['data'])
        else:
            self.data = None