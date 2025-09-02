"""
快速验证脚本 - 验证Python SDK基本功能是否正常
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qinsilk_scm_openapi_sdk_py.client import OpenClient, OpenConfig
from qinsilk_scm_openapi_sdk_py.models.goods import GoodsListRequest
from tests.constant import API_URL, CLIENT_ID, CLIENT_SECRET


def quick_test():
    """快速测试基本连接和功能"""
    print("🔄 正在进行Python SDK快速验证...")
    
    try:
        # 1. 创建客户端
        config = OpenConfig(
            server_url=API_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        client = OpenClient(config)
        print("✅ 客户端创建成功")
        
        # 2. 测试简单的列表查询
        request = GoodsListRequest()
        request.page = 1
        request.size = 1
        
        print("🔄 正在测试API连接...")
        http_request, response = client.execute(request)
        
        if response.is_success():
            print("✅ API连接测试成功")
            print(f"   响应码: {response.code}")
            if hasattr(response, 'data') and response.data:
                print(f"   返回数据条数: {len(response.data)}")
        else:
            print(f"❌ API请求失败: {getattr(response, 'message', 'unknown error')}")
            return False
            
        print("\n🎉 Python SDK基本功能验证成功！")
        print("📝 现在可以运行完整的测试套件:")
        print("   python tests/run_tests.py")
        print("   或者: pytest")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查网络连接")
        print("2. 验证API配置信息")
        print("3. 确认依赖包已正确安装")
        return False


if __name__ == "__main__":
    quick_test()