# Qinsilk SCM OpenAPI SDK (Python)

[![PyPI version](https://badge.fury.io/py/qinsilk-scm-openapi-sdk-py.svg)](https://badge.fury.io/py/qinsilk-scm-openapi-sdk-py)
[![Python versions](https://img.shields.io/pypi/pyversions/qinsilk-scm-openapi-sdk-py.svg)](https://pypi.org/project/qinsilk-scm-openapi-sdk-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

秦丝生产 ERP 系统开放平台的 Python SDK，提供了完整的 API 调用封装，支持商品管理、订单处理、报表查询等核心业务功能。

## 特性

- 🔐 **安全认证**: 完整的 OAuth2 认证流程和数字签名机制
- 📦 **模块化设计**: 按业务模块组织，支持按需导入
- 🔄 **类型安全**: 完整的类型注解和数据验证
- 🛠️ **易于使用**: 简洁的 API 设计和丰富的使用示例
- 🧪 **测试覆盖**: 完整的单元测试覆盖
- 📚 **文档完善**: 详细的 API 文档和使用指南

## 版本历史

### v1.1.1 (当前版本)

🔧 **重要更新**: 全面同步 Java SDK 功能

- **新增功能**:

  - 新增品牌管理、用户管理、波段管理等基础数据模块
  - 新增生产订单管理功能
  - 新增多种生产报表查询功能
  - 新增 OSS 文件上传支持
  - 新增物料类型管理功能

- **架构优化**:

  - 统一代码风格，移除 dataclass 混用
  - 优化序列化和反序列化机制
  - 改进错误处理和异常管理
  - 增强类型转换和验证逻辑

- **签名修复**:

  - 修复了 `access_token` 在签名计算中缺失的问题
  - 完全匹配 Java 版本的签名算法
  - 优化 POST 请求参数处理
  - 改进 null 值和空白字符串处理

- **测试完善**:
  - 新增 32 个测试用例
  - 覆盖所有主要业务模块
  - 与 Java SDK 保持测试逻辑一致

## 功能模块

### 📊 基础数据管理

| 模块            | 功能               | 状态 |
| --------------- | ------------------ | ---- |
| `brand`         | 品牌信息管理       | ✅   |
| `goods`         | 商品信息管理       | ✅   |
| `color`         | 颜色和颜色分组管理 | ✅   |
| `size`          | 尺码和尺码分组管理 | ✅   |
| `material`      | 物料信息管理       | ✅   |
| `material_type` | 物料类型管理       | ✅   |
| `supplier`      | 供应商信息管理     | ✅   |
| `storehouse`    | 仓库信息管理       | ✅   |
| `user`          | 用户信息管理       | ✅   |
| `ranges`        | 波段信息管理       | ✅   |

### 📋 业务单据

| 模块    | 功能         | 状态 |
| ------- | ------------ | ---- |
| `order` | 生产订单管理 | ✅   |

### 📈 报表查询

| 报表类型         | 功能描述             | 状态 |
| ---------------- | -------------------- | ---- |
| 生产单明细报表   | 查询生产单的详细信息 | ✅   |
| 生产单工序报表   | 查询生产工序进度     | ✅   |
| 商品工序明细报表 | 查询商品工序详情     | ✅   |
| 薪资计件报表     | 查询员工计件薪资     | ✅   |
| 采购单明细报表   | 查询采购单详情       | ✅   |
| 领料单明细报表   | 查询领料单详情       | ✅   |

### 🗂️ 文件服务

| 模块  | 功能                  | 状态 |
| ----- | --------------------- | ---- |
| `oss` | 文件上传临时 URL 申请 | ✅   |

### 🔐 认证授权

| 功能        | 描述                 | 状态 |
| ----------- | -------------------- | ---- |
| OAuth2 认证 | 客户端认证和令牌获取 | ✅   |
| 数字签名    | API 请求安全签名     | ✅   |

## 系统要求

- **Python**: 3.6 或更高版本
- **依赖库**:
  - `requests >= 2.25.0`: HTTP 请求处理
  - `python-dotenv >= 0.19.0`: 环境变量管理

## 安装指南

### 从 PyPI 安装 (推荐)

```bash
pip install qinsilk-scm-openapi-sdk-py
```

### 从源码安装

```bash
git clone https://github.com/qinsilk/qinsilk-starter.git
cd qinsilk-starter/qinsilk_scm_openapi_sdk_py
pip install -r requirements.txt
pip install -e .
```

### 开发环境安装

```bash
# 安装开发依赖
pip install -r requirements.txt

# 安装测试依赖
pip install pytest pytest-cov pytest-mock
```

## 快速开始

### 1. 初始化客户端

#### 方式一：直接配置

```python
from qinsilk_scm_openapi_sdk_py import OpenClient, OpenConfig

# 配置客户端
config = OpenConfig(
    client_id="your_client_id",
    client_secret="your_client_secret",
    server_url="https://your.api.server/"
)

client = OpenClient(config)
```

#### 方式二：环境变量配置 (推荐)

创建 `.env` 文件：

```env
SCM_CLIENT_ID=your_client_id
SCM_CLIENT_SECRET=your_client_secret
SCM_SERVER_URL=https://your.api.server/
```

然后在代码中：

```python
from qinsilk_scm_openapi_sdk_py import OpenClient, OpenConfig
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenConfig 会自动读取环境变量
config = OpenConfig()
client = OpenClient(config)
```

### 2. 获取访问令牌

```python
from qinsilk_scm_openapi_sdk_py.models.token import ClientTokenRequest

# 获取访问令牌
token_request = ClientTokenRequest()
_, token_response = client.execute(token_request)

if token_response.is_success():
    access_token = token_response.access_token
    print(f"获取到访问令牌: {access_token}")

    # 设置访问令牌到客户端配置
    client.config.access_token = access_token
else:
    print(f"获取令牌失败: {token_response.message}")
```

### 3. 基础数据管理示例

#### 品牌管理

```python
from qinsilk_scm_openapi_sdk_py.models.brand import (
    BrandSaveRequest, BrandUpdateRequest, BrandListRequest, BrandDetailRequest
)

# 保存品牌
brand_save = BrandSaveRequest()
brand_save.brand_name = "测试品牌"
brand_save.brand_english_name = "Test Brand"
brand_save.brand_desc = "品牌描述"

_, save_response = client.execute(brand_save)
if save_response.is_success():
    brand_id = save_response.data.id
    print(f"品牌创建成功，ID: {brand_id}")

# 查询品牌列表
brand_list = BrandListRequest()
_, list_response = client.execute(brand_list)
if list_response.is_success():
    for brand in list_response.data.result:
        print(f"品牌: {brand.brand_name}")
```

#### 商品管理

```python
from qinsilk_scm_openapi_sdk_py.models.goods import (
    GoodsSaveRequest, GoodsListRequest, GoodsDetailRequest
)

# 保存商品
goods_save = GoodsSaveRequest()
goods_save.goods_name = "测试商品"
goods_save.goods_sn = "TEST001"
goods_save.goods_english_name = "Test Goods"

_, save_response = client.execute(goods_save)
if save_response.is_success():
    goods_id = save_response.data.id
    print(f"商品创建成功，ID: {goods_id}")

# 查询商品列表
goods_list = GoodsListRequest(page=1, size=10)
_, list_response = client.execute(goods_list)
if list_response.is_success():
    for goods in list_response.data.result:
        print(f"商品: {goods.goods_name}")
```

#### 报表查询

```python
from qinsilk_scm_openapi_sdk_py.models.report import (
    ProduceDetailReportRequest, ProduceProcessReportRequest
)
from datetime import datetime, timedelta

# 查询生产单明细报表
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")

report_request = ProduceDetailReportRequest(
    start_date=start_date,
    end_date=end_date,
    page=1,
    size=20
)

_, report_response = client.execute(report_request)
if report_response.is_success():
    for record in report_response.data.result:
        print(f"生产单号: {record.order_sn}")
```

### 4. 异常处理

```python
from qinsilk_scm_openapi_sdk_py import OpenException, ErrorCode

try:
    _, response = client.execute(request)
    if response.is_success():
        print("请求成功")
    else:
        print(f"业务错误: {response.message}")
except OpenException as e:
    if e.error_code == ErrorCode.NETWORK_ERROR:
        print("网络错误，请检查网络连接")
    elif e.error_code == ErrorCode.AUTH_ERROR:
        print("认证失败，请检查客户端配置")
    else:
        print(f"未知错误: {e.message}")
```

## 项目结构

```
qinsilk_scm_openapi_sdk_py/
├── qinsilk_scm_openapi_sdk_py/          # 核心 SDK 包
│   ├── __init__.py                      # 包初始化和公共接口
│   ├── client.py                        # 核心客户端和配置
│   ├── signing.py                       # API 签名处理
│   ├── exceptions.py                    # 异常定义
│   ├── models/                          # 数据模型
│   │   ├── __init__.py                  # 模型包初始化
│   │   ├── base.py                      # 基础请求/响应模型
│   │   ├── token.py                     # 认证令牌模型
│   │   ├── brand.py                     # 品牌管理模型
│   │   ├── goods.py                     # 商品管理模型
│   │   ├── color.py                     # 颜色管理模型
│   │   ├── size.py                      # 尺码管理模型
│   │   ├── material.py                  # 物料管理模型
│   │   ├── material_type.py             # 物料类型模型
│   │   ├── supplier.py                  # 供应商管理模型
│   │   ├── storehouse.py                # 仓库管理模型
│   │   ├── user.py                      # 用户管理模型
│   │   ├── ranges.py                    # 波段管理模型
│   │   ├── order.py                     # 订单管理模型
│   │   ├── report.py                    # 报表查询模型
│   │   └── oss.py                       # 文件上传模型
│   └── utils/                           # 工具模块
│       ├── serialization.py             # 序列化工具
│       ├── type_conversion.py           # 类型转换工具
│       └── dataclass_helper.py          # 数据类助手
├── examples/                            # 使用示例
│   ├── .env                            # 环境变量模板
│   ├── example_brand.py                # 品牌管理示例
│   ├── example_goods.py                # 商品管理示例
│   ├── example_user.py                 # 用户管理示例
│   ├── example_report.py               # 报表查询示例
│   ├── example_oss.py                  # 文件上传示例
│   └── ...                             # 其他模块示例
├── tests/                              # 测试用例
│   ├── test_*.py                       # 各模块测试文件
│   ├── constant.py                     # 测试常量
│   └── test_base.py                    # 测试基类
├── requirements.txt                     # 项目依赖
├── setup.py                            # 包配置
├── pytest.ini                         # 测试配置
└── README.md                           # 项目文档
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_brand_save.py

# 运行测试并生成覆盖率报告
pytest --cov=qinsilk_scm_openapi_sdk_py --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black qinsilk_scm_openapi_sdk_py/

# 检查代码风格
flake8 qinsilk_scm_openapi_sdk_py/
```

### 构建和发布

```bash
# 安装构建工具
python -m pip install --upgrade setuptools wheel twine

# 构建包
python setup.py sdist bdist_wheel

# 发布到 PyPI
twine upload dist/*
```

## API 参考

### 核心类

- **`OpenClient`**: 主要的 API 客户端类
- **`OpenConfig`**: 客户端配置类
- **`BaseRequest`**: 所有请求的基类
- **`BaseResponse`**: 所有响应的基类
- **`OpenException`**: SDK 异常基类

### 配置选项

| 参数            | 类型 | 描述              | 环境变量            |
| --------------- | ---- | ----------------- | ------------------- |
| `client_id`     | str  | 客户端 ID         | `SCM_CLIENT_ID`     |
| `client_secret` | str  | 客户端密钥        | `SCM_CLIENT_SECRET` |
| `server_url`    | str  | API 服务器地址    | `SCM_SERVER_URL`    |
| `access_token`  | str  | 访问令牌 (可选)   | `SCM_ACCESS_TOKEN`  |
| `timeout`       | int  | 请求超时时间 (秒) | `SCM_TIMEOUT`       |

## 许可证

本项目基于 [MIT 许可证](https://opensource.org/licenses/MIT) 开源。

## 贡献

欢迎贡献代码！请确保：

1. 遵循现有的代码风格
2. 添加适当的测试用例
3. 更新相关文档
4. 确保所有测试通过

## 支持

如果您在使用过程中遇到问题，请：

1. 查看 [示例代码](examples/)
2. 检查 [测试用例](tests/)
3. 提交 [Issue](https://github.com/qinsilk/qinsilk-starter/issues)

## 更新日志

详见 [版本历史](#版本历史) 部分。
