"""
生产订单相关请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.order.produce.ProduceOrderDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.order.produce.ProduceOrderListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.order.produce.ProduceOrderSaveRequestTest
"""
import pytest
from datetime import datetime
from qinsilk_scm_openapi_sdk_py.models.order import (
    ProduceOrderDetailRequest, ProduceOrderDetailResponse,
    ProduceOrderListRequest, ProduceOrderListResponse,
    ProduceOrderSaveRequest, ProduceOrderDTO, ProduceOrderDtDTO, ProduceOrderSaveResponse
)
from tests.test_base import TestBase


class TestProduceOrderDetailRequest(TestBase):
    """生产订单详情请求测试类"""
    
    def test_get_detail(self):
        """
        测试获取生产订单详情
        对应Java版本的 ProduceOrderDetailRequestTest.testGetDetail() 方法
        """
        request = ProduceOrderDetailRequest()
        request.order_sn = "SC2503171026083083"  # 对应Java版本的订单号
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "生产订单详情请求失败")
        
        # 验证订单号正确（对应Java版本的Assert.isTrue）
        assert response.data.orders_sn == "SC2503171026083083", "生产单错误"
        
        # 验证响应类型
        assert isinstance(response, ProduceOrderDetailResponse), "响应类型不正确"
        
        print(f"✅ 生产订单详情获取成功")
        print(f"订单号: {response.data.orders_sn}")
        print(f"订单ID: {response.data.id}")
        print(f"生产类型: {response.data.type}")


class TestProduceOrderListRequest(TestBase):
    """生产订单列表请求测试类"""
    
    def test_get_list(self):
        """
        测试获取生产订单列表
        对应Java版本的 ProduceOrderListRequestTest.testGetList() 方法
        """
        # 首先不带参数获取列表，以确保有数据
        list_request = ProduceOrderListRequest()
        http_request, list_response = self.execute_request(list_request)
        self.assert_success(list_response, "获取生产订单列表失败")
        
        if len(list_response.data) == 0:
            print("⚠️ 生产订单列表为空，跳过测试")
            return
        
        # 使用第一个订单号进行查询测试
        test_order_sn = list_response.data[0].orders_sn
        print(f"使用订单号进行测试: {test_order_sn}")
        
        request = ProduceOrderListRequest()
        request.order_sn = test_order_sn
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "生产订单列表请求失败")
        
        # 直接验证第一个订单号正确（对应Java版本的Assert.isTrue）
        # Java版本直接访问getData().get(0)，不检查列表是否为空
        assert response.data[0].orders_sn == test_order_sn, "生产单错误"
        
        # 验证响应类型
        assert isinstance(response, ProduceOrderListResponse), "响应类型不正确"
        
        print(f"✅ 生产订单列表获取成功")
        print(f"找到 {len(response.data)} 个订单")
        print(f"第一个订单号: {response.data[0].orders_sn}")


class TestProduceOrderSaveRequest(TestBase):
    """生产订单保存请求测试类"""
    
    def test_create_produce(self):
        """
        测试创建生产订单
        对应Java版本的 ProduceOrderSaveRequestTest.testCreateProduce() 方法
        """
        request = ProduceOrderSaveRequest()
        
        # 设置ProduceOrderDTO - 对应Java版本的ProduceOrderDTO
        produce_order_dto = ProduceOrderDTO()
        produce_order_dto.type = 1  # 对应Java版本的order.type
        produce_order_dto.storehouse_id = 4826  # 对应Java版本的order.storehouseId
        
        # 设置业务日期 - 对应Java版本的解析业务日期
        # Java版本使用的是: "2025-03-17T02:56:08.000Z"
        business_date = datetime.fromisoformat("2025-03-17T02:56:08.000")
        produce_order_dto.business_time = business_date
        
        # 将produceOrderDTO设置到request中
        request.produce = produce_order_dto
        
        # 设置orderGoodsList - 对应Java版本的orderGoodsList
        order_goods_list = []
        
        # 添加第一个商品
        goods1 = ProduceOrderDtDTO()
        goods1.goods_id = 88589  # 对应Java版本的88589L
        goods1.sku_id = 224382  # 对应Java版本的224382L
        goods1.number = 100
        order_goods_list.append(goods1)
        
        # 添加第二个商品
        goods2 = ProduceOrderDtDTO()
        goods2.goods_id = 88589  # 对应Java版本的88589L
        goods2.sku_id = 224383  # 对应Java版本的224383L
        goods2.number = 100
        order_goods_list.append(goods2)
        
        # 添加第三个商品
        goods3 = ProduceOrderDtDTO()
        goods3.goods_id = 88589  # 对应Java版本的88589L
        goods3.sku_id = 224384  # 对应Java版本的224384L
        goods3.number = 100
        order_goods_list.append(goods3)
        
        # 添加第四个商品
        goods4 = ProduceOrderDtDTO()
        goods4.goods_id = 88589  # 对应Java版本的88589L
        goods4.sku_id = 224385  # 对应Java版本的224385L
        goods4.number = 100
        order_goods_list.append(goods4)
        
        # 将orderGoodsList设置到request中
        request.order_goods_list = order_goods_list
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "生产订单创建请求失败")
        
        # 验证订单号不为空（对应Java版本的Assert.notNull）
        assert response.data.orders_sn is not None, "生产单错误"
        
        # 验证响应类型
        assert isinstance(response, ProduceOrderSaveResponse), "响应类型不正确"
        
        print(f"✅ 生产订单创建成功")
        print(f"生成的订单号: {response.data.orders_sn}")
        print(f"订单ID: {response.data.id}")
        print(f"生产类型: {response.data.type}")
        print(f"仓库ID: {response.data.storehouse_id}")


# 提供测试实例的fixtures
@pytest.fixture
def produce_order_detail_test():
    return TestProduceOrderDetailRequest()

@pytest.fixture
def produce_order_list_test():
    return TestProduceOrderListRequest()

@pytest.fixture
def produce_order_save_test():
    return TestProduceOrderSaveRequest()


# 集成测试函数
def test_produce_order_detail_integration(produce_order_detail_test):
    """集成测试：生产订单详情完整流程"""
    produce_order_detail_test.test_get_detail()

def test_produce_order_list_integration(produce_order_list_test):
    """集成测试：生产订单列表完整流程"""
    produce_order_list_test.test_get_list()

def test_produce_order_save_integration(produce_order_save_test):
    """集成测试：生产订单保存完整流程"""
    produce_order_save_test.test_create_produce()


if __name__ == "__main__":
    # 直接运行测试
    print("开始生产订单详情测试...")
    detail_test = TestProduceOrderDetailRequest()
    detail_test.test_get_detail()
    
    print("\n开始生产订单列表测试...")
    list_test = TestProduceOrderListRequest()
    list_test.test_get_list()
    
    print("\n开始生产订单保存测试...")
    save_test = TestProduceOrderSaveRequest()
    save_test.test_create_produce()
    
    print("\n✅ 所有生产订单测试通过")