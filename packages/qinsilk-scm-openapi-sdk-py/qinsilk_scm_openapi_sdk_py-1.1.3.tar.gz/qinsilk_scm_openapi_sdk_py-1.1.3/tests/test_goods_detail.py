"""
商品详情请求测试
对应Java版本的 com.qinsilk.scm.openapi.sdk.biz.goods.base.GoodsDetailRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.goods import (
    GoodsDetailRequest, GoodsDetailResponse
)
from tests.test_base import TestBase


class TestGoodsDetailRequest(TestBase):
    """商品详情请求测试类"""
    
    def test_goods_detail_request(self):
        """
        测试商品详情查询
        对应Java版本的 testGoodsDetailRequest() 方法
        """
        # 创建商品详情请求 - 使用与Java版本相同的测试商品ID
        goods_detail_request = GoodsDetailRequest()
        goods_detail_request.goods_id = 89079  # 对应Java版本的89079L
        
        # 执行请求
        http_request, response = self.execute_request(goods_detail_request)
        
        # 验证响应成功
        self.assert_success(response, "商品详情查询失败")
        
        # 验证响应类型
        assert isinstance(response, GoodsDetailResponse), "响应类型不正确"
        
        # 验证商品ID - 对应Java版本的Assert.isTrue(Objects.equal(89079L, ...))
        assert response.data is not None, "商品数据不能为空"
        assert response.data.id == 89079, f"商品ID错误，期望: 89079, 实际: {response.data.id}"
        
        print(f"✅ 商品详情查询成功，商品ID: {response.data.id}")
        
        # 验证商品基本信息
        if response.data.goods_name:
            print(f"商品名称: {response.data.goods_name}")
        if response.data.design_sn:
            print(f"设计款号: {response.data.design_sn}")


@pytest.fixture
def goods_detail_test():
    """提供商品详情测试实例的fixture"""
    return TestGoodsDetailRequest()


def test_goods_detail_integration(goods_detail_test):
    """集成测试：商品详情查询完整流程"""
    goods_detail_test.test_goods_detail_request()


if __name__ == "__main__":
    # 直接运行测试
    test_instance = TestGoodsDetailRequest()
    test_instance.test_goods_detail_request()
    print("✅ 商品详情测试通过")