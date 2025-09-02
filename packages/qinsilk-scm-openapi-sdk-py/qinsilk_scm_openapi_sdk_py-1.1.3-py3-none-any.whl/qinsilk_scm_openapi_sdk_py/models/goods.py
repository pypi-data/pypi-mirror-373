"""
商品相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse
from datetime import datetime


class GoodsPrice:
    """商品价格"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.type = data.get('type')
        self.price = data.get('price')


class SkuDetail:
    """简化的SKU详情，用于基本显示"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.sku_id = data.get('skuId')
        self.color_id = data.get('colorId')
        self.size_id = data.get('sizeId')
        self.sku_bar_code = data.get('skuBarCode')


class SkuDetailVO:
    """完整的SKU详情显示对象，用于查询结果显示"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.color_id = data.get('colorId')  # 颜色Id（必填）
        self.size_id = data.get('sizeId')    # 尺码Id（必填）
        self.sku_id = data.get('skuId')      # 单品ID
        self.sku_bar_code = data.get('skuBarCode')  # 单品条码


class GoodsDetail:
    """商品详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.goods_name = data.get('goodsName')
        self.design_sn = data.get('designSn')
        self.goods_sn = data.get('goodsSn')
        self.sex = data.get('sex')
        self.style_id = data.get('styleId')
        self.season_id = data.get('seasonId')
        self.year = data.get('year')
        self.month = data.get('month')
        self.ranges_id = data.get('rangesId')
        self.silhouette = data.get('silhouette')
        self.designer = data.get('designer')
        self.pattern_maker_id = data.get('patternMakerId')
        self.remark = data.get('remark')
        
        # 处理价格列表
        if data.get('priceList'):
            self.price_list = [GoodsPrice(item) for item in data['priceList']]
        else:
            self.price_list = None
            
        # 处理SKU列表
        if data.get('skuList'):
            self.sku_list = [SkuDetailVO(item) for item in data['skuList']]
        else:
            self.sku_list = None


class GoodsListDetail:
    """商品列表详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.goods_name = data.get('goodsName')
        self.design_sn = data.get('designSn')
        self.goods_sn = data.get('goodsSn')
        self.sex = data.get('sex')
        self.style_id = data.get('styleId')
        self.season_id = data.get('seasonId')
        self.year = data.get('year')
        self.month = data.get('month')
        self.ranges_id = data.get('rangesId')
        self.silhouette = data.get('silhouette')
        self.designer = data.get('designer')
        self.pattern_maker_id = data.get('patternMakerId')
        self.remark = data.get('remark')
        
        # 添加API响应中的额外字段
        self.goods_img_url = data.get('goodsImgUrl')
        self.designer_name = data.get('designerName')
        self.pattern_maker_name = data.get('patternMakerName')
        self.goods_colors = data.get('goodsColors')
        self.goods_sizes = data.get('goodsSizes')
        self.is_sealed_sample = data.get('isSealedSample')
        self.stored_number = data.get('storedNumber')
        self.win_number = data.get('winNumber')
        self.wout_number = data.get('woutNumber')
        self.available_number = data.get('availableNumber')
        self.produce_number = data.get('produceNumber')
        self.ie_price = data.get('iePrice')
        self.goods_material_list = data.get('goodsMaterialList')
        self.factory_id = data.get('factoryId')
        self.supplier_sn = data.get('supplierSn')
        self.follower_id = data.get('followerId')
        self.composition = data.get('composition')
        self.sample_source = data.get('sampleSource')
        self.bar_code = data.get('barCode')
        self.is_on_sale = data.get('isOnSale')
        self.first_order_time = data.get('firstOrderTime')
        self.handler_id = data.get('handlerId')
        self.handler_name = data.get('handlerName')
        self.last_handler_name = data.get('lastHandlerName')
        self.last_handler_id = data.get('lastHandlerId')
        self.update_time = data.get('updateTime')
        self.create_time = data.get('createTime')


class GoodsSkuDTO:
    """商品SKU数据传输对象，用于保存请求"""
    
    def __init__(self, color_id=None, size_id=None, sku_bar_code=None, is_disable=None):
        self.color_id = color_id      # 颜色Id（必填）
        self.size_id = size_id       # 尺码Id（必填）
        self.sku_bar_code = sku_bar_code  # 单品条码
        self.is_disable = is_disable    # 是否禁用 1-禁用

    def to_dict(self):
        return {
            'colorId': self.color_id,
            'sizeId': self.size_id,
            'skuBarCode': self.sku_bar_code,
            'isDisable': self.is_disable
        }


class GoodsSaveDTO:
    """商品保存数据传输对象"""
    
    def __init__(self, show_order=None, is_sealed_sample=None, retail_price_area=None, trade_price=None, goods_sn=None, design_sn=None, name=None, sample_source=None, supplier_sn=None, dev_time=None, client_id=None, plan_id=None, bland_id=None, category_id=None, execute_standard_id=None, security_type_id=None, sex=None, style_id=None, season_id=None, year=None, ranges_id=None, silhouette=None, designer=None, pattern_maker_id=None, is_on_sale=None, remark=None, tag_price=None, cost_price=None, retail_price_factory=None, img_url=None, size_len_display=None, handler_id=None, follower_id=None, enable_sku_bar_code=None, enable_sku_storage_location=None, gram_weight=None, composition=None, bom_state=None, factory_id=None, month=None, warn_number_top=None, warn_number_low=None, tag=None, grade=None, is_sample=None, bulk_goods_state=None, make_sample_state=None, review_state=None, design_order_id=None):
        self.show_order = show_order
        self.is_sealed_sample = is_sealed_sample
        self.retail_price_area = retail_price_area
        self.trade_price = trade_price
        self.goods_sn = goods_sn
        self.design_sn = design_sn
        self.name = name
        self.sample_source = sample_source
        self.supplier_sn = supplier_sn
        self.dev_time = dev_time
        self.client_id = client_id
        self.plan_id = plan_id
        self.bland_id = bland_id
        self.category_id = category_id
        self.execute_standard_id = execute_standard_id
        self.security_type_id = security_type_id
        self.sex = sex
        self.style_id = style_id
        self.season_id = season_id
        self.year = year
        self.ranges_id = ranges_id
        self.silhouette = silhouette
        self.designer = designer
        self.pattern_maker_id = pattern_maker_id
        self.is_on_sale = is_on_sale
        self.remark = remark
        self.tag_price = tag_price
        self.cost_price = cost_price
        self.retail_price_factory = retail_price_factory
        self.img_url = img_url
        self.size_len_display = size_len_display
        self.handler_id = handler_id
        self.follower_id = follower_id
        self.enable_sku_bar_code = enable_sku_bar_code
        self.enable_sku_storage_location = enable_sku_storage_location
        self.gram_weight = gram_weight
        self.composition = composition
        self.bom_state = bom_state
        self.factory_id = factory_id
        self.month = month
        self.warn_number_top = warn_number_top
        self.warn_number_low = warn_number_low
        self.tag = tag
        self.grade = grade
        self.is_sample = is_sample
        self.bulk_goods_state = bulk_goods_state
        self.make_sample_state = make_sample_state
        self.review_state = review_state
        self.design_order_id = design_order_id

    def to_dict(self):
        result = {}
        # 只添加非None的字段
        field_mapping = {
            'show_order': 'showOrder',
            'is_sealed_sample': 'isSealedSample',
            'retail_price_area': 'retailPriceArea',
            'trade_price': 'tradePrice',
            'goods_sn': 'goodsSn',
            'design_sn': 'designSn',
            'name': 'name',
            'sample_source': 'sampleSource',
            'supplier_sn': 'supplierSn',
            'dev_time': 'devTime',
            'client_id': 'clientId',
            'plan_id': 'planId',
            'bland_id': 'blandId',
            'category_id': 'categoryId',
            'execute_standard_id': 'executeStandardId',
            'security_type_id': 'securityTypeId',
            'sex': 'sex',
            'style_id': 'styleId',
            'season_id': 'seasonId',
            'year': 'year',
            'ranges_id': 'rangesId',
            'silhouette': 'silhouette',
            'designer': 'designer',
            'pattern_maker_id': 'patternMakerId',
            'is_on_sale': 'isOnSale',
            'remark': 'remark',
            'tag_price': 'tagPrice',
            'cost_price': 'costPrice',
            'retail_price_factory': 'retailPriceFactory',
            'img_url': 'imgUrl',
            'size_len_display': 'sizeLenDisplay',
            'handler_id': 'handlerId',
            'follower_id': 'followerId',
            'enable_sku_bar_code': 'enableSkuBarCode',
            'enable_sku_storage_location': 'enableSkuStorageLocation',
            'gram_weight': 'gramWeight',
            'composition': 'composition',
            'bom_state': 'bomState',
            'factory_id': 'factoryId',
            'month': 'month',
            'warn_number_top': 'warnNumberTop',
            'warn_number_low': 'warnNumberLow',
            'tag': 'tag',
            'grade': 'grade',
            'is_sample': 'isSample',
            'bulk_goods_state': 'bulkGoodsState',
            'make_sample_state': 'makeSampleState',
            'review_state': 'reviewState',
            'design_order_id': 'designOrderId'
        }
        
        for python_field, api_field in field_mapping.items():
            value = getattr(self, python_field)
            if value is not None:
                # 特殊处理datetime类型
                if isinstance(value, datetime):
                    result[api_field] = value.isoformat()
                else:
                    result[api_field] = value
                    
        return result


class GoodsListRequest(BaseRequest):
    """商品列表请求"""
    
    def __init__(self):
        super().__init__()
        self.goods_sn = None
        self.design_sn = None
        self.custom_design_sn = None
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/goods/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return GoodsListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.goods_sn:
            body["goodsSn"] = self.goods_sn
        if self.design_sn:
            body["designSn"] = self.design_sn
        if self.custom_design_sn:
            body["customDesignSn"] = self.custom_design_sn
        return body


class GoodsDetailRequest(BaseRequest):
    """商品详情请求"""
    
    def __init__(self):
        super().__init__()
        self.goods_id = None

    def get_api_url(self):
        return "api/open/goods/base/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return GoodsDetailResponse

    def get_request_body(self):
        return {"goodsId": self.goods_id}


class GoodsSaveRequest(BaseRequest):
    """商品保存请求"""
    
    def __init__(self):
        super().__init__()
        self.goods = None                    # 商品信息（必填）
        self.goods_sku_vo_list = None        # 单品信息（必填）

    def get_api_url(self):
        return "api/open/goods/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return GoodsDetailResponse

    def get_request_body(self):
        body = {}
        if self.goods:
            body['goods'] = self.goods.to_dict()
        if self.goods_sku_vo_list:
            body['goodsSkuVOList'] = [sku.to_dict() for sku in self.goods_sku_vo_list]
        return body


class GoodsListResponse(BaseResponse):
    """商品列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [GoodsListDetail(item) for item in response_data['data']]
        else:
            self.data = []


class GoodsDetailResponse(BaseResponse):
    """商品详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = GoodsDetail(response_data['data'])
        else:
            self.data = None