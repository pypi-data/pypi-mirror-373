"""
物料采购相关请求测试
对应Java版本的：
- com.qinsilk.scm.openapi.sdk.biz.material.purchase.MaterialPurchaseDetailRequestTest
- com.qinsilk.scm.openapi.sdk.biz.material.purchase.MaterialPurchaseListRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.material import (
    MaterialPurchaseDetailRequest, MaterialPurchaseDetailResponse,
    MaterialPurchaseListRequest, MaterialPurchaseListResponse
)
from tests.test_base import TestBase


class TestMaterialPurchaseDetailRequest(TestBase):
    """物料采购详情请求测试类"""
    
    def test_set_order_sn(self):
        """
        测试设置订单号获取物料采购详情
        对应Java版本的 MaterialPurchaseDetailRequestTest.setOrderSn() 方法
        """
        request = MaterialPurchaseDetailRequest()
        request.order_sn = "WLCG2504301120250028"  # 对应Java版本的订单号
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "物料采购详情请求失败")
        
        # 验证订单号正确（对应Java版本的Assert.isTrue）
        assert response.data.orders_sn == "WLCG2504301120250028", f"查询物料采购单错误: 期望='WLCG2504301120250028', 实际='{response.data.orders_sn}'"
        
        # 验证响应类型
        assert isinstance(response, MaterialPurchaseDetailResponse), "响应类型不正确"
        
        print(f"✅ 物料采购详情获取成功")
        print(f"订单号: {response.data.orders_sn}")
        print(f"供应商ID: {response.data.supplier_id}")
        print(f"仓库ID: {response.data.storehouse_id}")
        print(f"业务时间: {response.data.business_time}")


class TestMaterialPurchaseListRequest(TestBase):
    """物料采购列表请求测试类"""
    
    def test_search_order_sn(self):
        """
        测试按订单号搜索物料采购列表
        对应Java版本的 MaterialPurchaseListRequestTest.testSearchOrderSn() 方法
        """
        request = MaterialPurchaseListRequest()
        request.order_sn = "WLCG2504301120250028"  # 对应Java版本的订单号
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "物料采购列表请求失败")
        
        # 验证列表不为空且第一个订单号正确（对应Java版本的Assert.isTrue）
        assert len(response.data) > 0, "物料采购列表为空"
        assert response.data[0].orders_sn == "WLCG2504301120250028", "查询物料采购单错误"
        
        # 验证响应类型
        assert isinstance(response, MaterialPurchaseListResponse), "响应类型不正确"
        
        print(f"✅ 物料采购列表获取成功")
        print(f"找到 {len(response.data)} 个采购单")
        print(f"第一个订单号: {response.data[0].orders_sn}")
        print(f"供应商ID: {response.data[0].supplier_id}")


# 提供测试实例的fixtures
@pytest.fixture
def material_purchase_detail_test():
    return TestMaterialPurchaseDetailRequest()

@pytest.fixture
def material_purchase_list_test():
    return TestMaterialPurchaseListRequest()


# 集成测试函数
def test_material_purchase_detail_integration(material_purchase_detail_test):
    """集成测试：物料采购详情完整流程"""
    material_purchase_detail_test.test_set_order_sn()

def test_material_purchase_list_integration(material_purchase_list_test):
    """集成测试：物料采购列表完整流程"""
    material_purchase_list_test.test_search_order_sn()


if __name__ == "__main__":
    # 直接运行测试
    print("开始物料采购详情测试...")
    detail_test = TestMaterialPurchaseDetailRequest()
    detail_test.test_set_order_sn()
    
    print("\n开始物料采购列表测试...")
    list_test = TestMaterialPurchaseListRequest()
    list_test.test_search_order_sn()
    
    print("\n✅ 所有物料采购测试通过")