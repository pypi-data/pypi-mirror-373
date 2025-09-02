"""
测试套件运行脚本
对应Java版本的测试类，提供批量测试执行
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_goods_save import TestGoodsSaveRequest
from tests.test_goods_detail import TestGoodsDetailRequest  
from tests.test_goods_list import TestGoodsListRequest
from tests.test_color_save import TestColorSaveRequest
from tests.test_size_save import TestSizeSaveRequest


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 Python SDK 测试套件")
    print("=" * 60)
    
    # 商品相关测试
    print("\n📦 商品模块测试")
    print("-" * 30)
    
    try:
        # 商品保存测试
        print("1. 商品保存测试...")
        goods_save_test = TestGoodsSaveRequest()
        goods_save_test.test_add_goods()
        print("   ✅ 通过")
        
        # 商品详情测试
        print("2. 商品详情测试...")
        goods_detail_test = TestGoodsDetailRequest()
        goods_detail_test.test_goods_detail_request()
        print("   ✅ 通过")
        
        # 商品列表测试
        print("3. 商品列表测试...")
        goods_list_test = TestGoodsListRequest()
        goods_list_test.test_goods_sn()
        goods_list_test.test_design_sn()
        goods_list_test.test_custom_design_sn()
        print("   ✅ 通过")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    # 颜色相关测试
    print("\n🎨 颜色模块测试")
    print("-" * 30)
    
    try:
        # 颜色保存测试
        print("1. 颜色保存测试...")
        color_save_test = TestColorSaveRequest()
        color_save_test.test_add_color()
        print("   ✅ 通过")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    # 尺码相关测试
    print("\n📏 尺码模块测试")
    print("-" * 30)
    
    try:
        # 尺码保存测试
        print("1. 尺码保存测试...")
        size_save_test = TestSizeSaveRequest()
        size_save_test.test_add_size()
        print("   ✅ 通过")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！Python SDK 测试套件执行完成")
    return True


def run_goods_tests():
    """仅运行商品相关测试"""
    print("📦 运行商品模块测试")
    
    try:
        goods_save_test = TestGoodsSaveRequest()
        goods_save_test.test_add_goods()
        
        goods_detail_test = TestGoodsDetailRequest()
        goods_detail_test.test_goods_detail_request()
        
        goods_list_test = TestGoodsListRequest()
        goods_list_test.test_goods_sn()
        goods_list_test.test_design_sn()
        goods_list_test.test_custom_design_sn()
        
        print("✅ 商品模块测试通过")
        return True
    except Exception as e:
        print(f"❌ 商品模块测试失败: {e}")
        return False


def run_size_tests():
    """仅运行尺码相关测试"""
    print("📏 运行尺码模块测试")
    
    try:
        size_save_test = TestSizeSaveRequest()
        size_save_test.test_add_size()
        
        print("✅ 尺码模块测试通过")
        return True
    except Exception as e:
        print(f"❌ 尺码模块测试失败: {e}")
        return False


def run_color_tests():
    """仅运行颜色相关测试"""
    print("🎨 运行颜色模块测试")
    
    try:
        color_save_test = TestColorSaveRequest()
        color_save_test.test_add_color()
        
        print("✅ 颜色模块测试通过")
        return True
    except Exception as e:
        print(f"❌ 颜色模块测试失败: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "goods":
            run_goods_tests()
        elif test_type == "color":
            run_color_tests()
        elif test_type == "size":
            run_size_tests()
        else:
            print("支持的测试类型: goods, color, size")
    else:
        run_all_tests()