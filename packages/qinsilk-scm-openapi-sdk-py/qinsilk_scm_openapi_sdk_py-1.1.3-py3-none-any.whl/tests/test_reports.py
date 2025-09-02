"""
报表相关请求测试
对应Java版本的6个报表测试：
- com.qinsilk.scm.openapi.sdk.biz.report.goods.workprocess.GoodsWorkProcessReportListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.report.pick.detail.SalaryDetailReportListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.report.produce.detail.MaterialPickDetailReportListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.report.produce.workprocess.GoodsWorkProcessReportListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.report.purchase.detail.MaterialPurchaseDetailReportListRequestTest
- com.qinsilk.scm.openapi.sdk.biz.report.salary.detail.SalaryDetailReportListResponseTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.report import (
    # 生产单报表
    ProduceDetailReportListRequest, ProduceDetailReportListResponse,
    ProduceWorkProcessListRequest, ProduceWorkProcessListResponse,
    ProduceOrderDTO,
    
    # 商品工序报表
    GoodsWorkProcessDetailListRequest, GoodsWorkProcessDetailListResponse,
    
    # 薪资计件报表
    SalaryDetailReportListRequest, SalaryDetailReportListResponse,
    
    # 物料采购报表
    MaterialPurchaseDetailReportListRequest, MaterialPurchaseDetailReportListResponse,
    
    # 领料单报表
    MaterialPickDetailReportListRequest, MaterialPickDetailReportListResponse
)
from tests.test_base import TestBase


class TestGoodsWorkProcessReportList(TestBase):
    """商品工序报表列表测试类"""
    
    def test_query_goods_work_process_report_list(self):
        """
        测试查询商品工序报表列表
        对应Java版本的 GoodsWorkProcessReportListRequestTest.testQueryPickDetailReportList() 方法
        """
        request = GoodsWorkProcessDetailListRequest()
        # 设置必填的商品ID集合
        request.goods_ids = [1, 2]  # 示例商品ID，实际使用时需要替换为实际的商品ID
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "商品工序报表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, GoodsWorkProcessDetailListResponse), "响应类型不正确"
        
        print(f"✅ 商品工序报表列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


class TestSalaryDetailReportList(TestBase):
    """薪资计件报表列表测试类"""
    
    def test_query_salary_detail_report_list(self):
        """
        测试查询薪资计件报表列表
        对应Java版本的 SalaryDetailReportListResponseTest.testQueryPickDetailReportList() 方法
        """
        request = SalaryDetailReportListRequest()
        # 设置必填的业务时间参数
        import time
        current_time = int(time.time() * 1000)
        one_month_ago = current_time - (30 * 24 * 60 * 60 * 1000)  # 30天前
        request.business_begin_time = one_month_ago
        request.business_end_time = current_time
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "薪资计件报表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, SalaryDetailReportListResponse), "响应类型不正确"
        
        print(f"✅ 薪资计件报表列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


class TestMaterialPurchaseDetailReportList(TestBase):
    """物料采购明细报表列表测试类"""
    
    def test_query_material_purchase_detail_report_list(self):
        """
        测试查询物料采购明细报表列表
        对应Java版本的 MaterialPurchaseDetailReportListRequestTest
        """
        request = MaterialPurchaseDetailReportListRequest()
        request.purchase_orders_sn = "WLCG2504301120250028"  # 示例采购单号
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "物料采购明细报表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, MaterialPurchaseDetailReportListResponse), "响应类型不正确"
        
        print(f"✅ 物料采购明细报表列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


class TestMaterialPickDetailReportList(TestBase):
    """领料单明细报表列表测试类"""
    
    def test_query_material_pick_detail_report_list(self):
        """
        测试查询领料单明细报表列表
        对应Java版本的 MaterialPickDetailReportListRequestTest
        """
        request = MaterialPickDetailReportListRequest()
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "领料单明细报表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, MaterialPickDetailReportListResponse), "响应类型不正确"
        
        print(f"✅ 领料单明细报表列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


class TestProduceDetailReportList(TestBase):
    """生产单明细报表列表测试类"""
    
    def test_query_produce_detail_report_list(self):
        """
        测试查询生产单明细报表列表
        """
        request = ProduceDetailReportListRequest()
        
        # 设置生产单查询条件
        produce_dto = ProduceOrderDTO()
        produce_dto.orders_sn = "SC2503171026083083"  # 示例生产单号
        request.produce = produce_dto
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "生产单明细报表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, ProduceDetailReportListResponse), "响应类型不正确"
        
        print(f"✅ 生产单明细报表列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


class TestProduceWorkProcessList(TestBase):
    """生产单工序列表测试类"""
    
    def test_query_produce_work_process_list(self):
        """
        测试查询生产单工序列表
        """
        request = ProduceWorkProcessListRequest()
        
        # 设置生产单查询条件
        produce_dto = ProduceOrderDTO()
        produce_dto.orders_sn = "SC2503171026083083"  # 示例生产单号
        request.produce = produce_dto
        
        http_request, response = self.execute_request(request)
        
        # 验证响应
        self.assert_success(response, "生产单工序列表请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, ProduceWorkProcessListResponse), "响应类型不正确"
        
        print(f"✅ 生产单工序列表获取成功")
        print(f"数据条数: {len(response.data) if response.data else 0}")


# 提供测试实例的fixtures
@pytest.fixture
def goods_work_process_report_test():
    return TestGoodsWorkProcessReportList()

@pytest.fixture
def salary_detail_report_test():
    return TestSalaryDetailReportList()

@pytest.fixture
def material_purchase_detail_report_test():
    return TestMaterialPurchaseDetailReportList()

@pytest.fixture
def material_pick_detail_report_test():
    return TestMaterialPickDetailReportList()

@pytest.fixture
def produce_detail_report_test():
    return TestProduceDetailReportList()

@pytest.fixture
def produce_work_process_test():
    return TestProduceWorkProcessList()


# 集成测试函数
def test_goods_work_process_report_integration(goods_work_process_report_test):
    """集成测试：商品工序报表完整流程"""
    goods_work_process_report_test.test_query_goods_work_process_report_list()

def test_salary_detail_report_integration(salary_detail_report_test):
    """集成测试：薪资计件报表完整流程"""
    salary_detail_report_test.test_query_salary_detail_report_list()

def test_material_purchase_detail_report_integration(material_purchase_detail_report_test):
    """集成测试：物料采购明细报表完整流程"""
    material_purchase_detail_report_test.test_query_material_purchase_detail_report_list()

def test_material_pick_detail_report_integration(material_pick_detail_report_test):
    """集成测试：领料单明细报表完整流程"""
    material_pick_detail_report_test.test_query_material_pick_detail_report_list()

def test_produce_detail_report_integration(produce_detail_report_test):
    """集成测试：生产单明细报表完整流程"""
    produce_detail_report_test.test_query_produce_detail_report_list()

def test_produce_work_process_integration(produce_work_process_test):
    """集成测试：生产单工序列表完整流程"""
    produce_work_process_test.test_query_produce_work_process_list()


if __name__ == "__main__":
    # 直接运行测试
    print("开始商品工序报表测试...")
    goods_test = TestGoodsWorkProcessReportList()
    goods_test.test_query_goods_work_process_report_list()
    
    print("\n开始薪资计件报表测试...")
    salary_test = TestSalaryDetailReportList()
    salary_test.test_query_salary_detail_report_list()
    
    print("\n开始物料采购明细报表测试...")
    purchase_test = TestMaterialPurchaseDetailReportList()
    purchase_test.test_query_material_purchase_detail_report_list()
    
    print("\n开始领料单明细报表测试...")
    pick_test = TestMaterialPickDetailReportList()
    pick_test.test_query_material_pick_detail_report_list()
    
    print("\n开始生产单明细报表测试...")
    produce_detail_test = TestProduceDetailReportList()
    produce_detail_test.test_query_produce_detail_report_list()
    
    print("\n开始生产单工序列表测试...")
    produce_process_test = TestProduceWorkProcessList()
    produce_process_test.test_query_produce_work_process_list()
    
    print("\n✅ 所有报表测试通过")