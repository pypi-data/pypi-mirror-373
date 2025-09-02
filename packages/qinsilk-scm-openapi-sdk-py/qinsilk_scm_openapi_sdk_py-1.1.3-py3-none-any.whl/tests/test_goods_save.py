"""
商品保存请求测试
对应Java版本的 com.qinsilk.scm.openapi.sdk.biz.goods.base.GoodsSaveRequestTest
"""
import pytest
from qinsilk_scm_openapi_sdk_py.models.goods import (
    GoodsSaveRequest, GoodsSaveDTO, GoodsSkuDTO, GoodsDetailResponse
)
from tests.test_base import TestBase, generate_test_goods_sn, generate_test_sku_barcode


class TestGoodsSaveRequest(TestBase):
    """商品保存请求测试类"""
    
    def test_add_goods(self):
        """
        测试新增商品
        对应Java版本的 testAddGoods() 方法
        """
        # 创建商品保存请求
        request = GoodsSaveRequest()
        
        # 创建商品基本信息DTO - 对应Java版本的GoodsSaveDTO
        goods_save_dto = GoodsSaveDTO(
            show_order=1,  # 必填字段
            name="测试商品",
            goods_sn=generate_test_goods_sn(),
            img_url="https://thumb.qinsilk.com/goods/album/1106946/20220406/feca2c9e74ed458e859303b4304f2bfa.jpg",
            enable_sku_bar_code=1  # 单品条码，1开启，0关闭（必填）
        )
        request.goods = goods_save_dto
        
        # 创建商品SKU信息 - 对应Java版本的GoodsSkuDTO  
        goods_sku_dto = GoodsSkuDTO(
            color_id=30962,  # 对应Java版本的30962L
            size_id=12601,   # 对应Java版本的12601L
            sku_bar_code=generate_test_sku_barcode()
        )
        request.goods_sku_vo_list = [goods_sku_dto]
        
        # 执行请求 - 对应Java版本的openClient.execute()
        http_request, response = self.execute_request(request)
        
        # 验证响应 - 对应Java版本的Assert.isTrue()
        self.assert_success(response, "商品保存请求失败")
        self.assert_response_code(response, "0")
        
        # 验证响应类型
        assert isinstance(response, GoodsDetailResponse), "响应类型不正确"
        
        # 验证返回的商品数据
        if response.data:
            assert response.data.id is not None, "商品ID不能为空"
            print(f"✅ 商品保存成功，ID: {response.data.id}")
        
        # 测试第二次保存（生成新的随机数）
        num = self.generate_random_number()
        goods_save_dto.goods_sn = f"test-open-add-goods{num}"
        goods_sku_dto.sku_bar_code = f"1234567890123{num}"
        
        # 再次执行请求验证
        http_request2, response2 = self.execute_request(request)
        self.assert_success(response2, "第二次商品保存请求失败")


@pytest.fixture
def goods_save_test():
    """提供商品保存测试实例的fixture"""
    return TestGoodsSaveRequest()


def test_goods_save_integration(goods_save_test):
    """集成测试：商品保存完整流程"""
    goods_save_test.test_add_goods()


if __name__ == "__main__":
    # 直接运行测试
    test_instance = TestGoodsSaveRequest()
    test_instance.test_add_goods()
    print("✅ 商品保存测试通过")