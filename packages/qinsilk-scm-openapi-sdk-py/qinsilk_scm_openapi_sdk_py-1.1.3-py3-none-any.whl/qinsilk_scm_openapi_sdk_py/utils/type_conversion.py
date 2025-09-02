"""
类型转换工具模块
包含类型解析、类型推断、泛型处理等功能
"""
import re
import inspect
from dataclasses import is_dataclass
from typing import get_origin, get_args, Union


def is_dataclass_type(type_obj):
    """检查类型是否为dataclass"""
    result = (is_dataclass(type_obj) or 
            (inspect.isclass(type_obj) and hasattr(type_obj, '__dataclass_fields__')))
    print(f"DEBUG: is_dataclass_type({type_obj}) = {result}")
    return result


def extract_list_element_type(actual_type, original_field_type, field_name, field_value):
    """提取List类型的元素类型"""
    # 方法1: 使用get_args获取类型参数
    type_args = get_args(actual_type)
    if type_args:
        return type_args[0]
    
    # 方法2: 从原始类型中查找List类型参数
    original_args = get_args(original_field_type)
    for arg in original_args:
        if get_origin(arg) in (list, type([])):
            inner_args = get_args(arg)
            if inner_args:
                return inner_args[0]
    
    # 方法3: 通过字符串解析类型
    type_str = str(original_field_type)
    list_match = re.search(r'List\[([^\]]+)\]', type_str)
    if list_match:
        type_name = list_match.group(1)
        return resolve_type_by_name(type_name)
    
    # 方法4: 根据字段名和数据内容推断
    if field_name == 'data' and field_value and len(field_value) > 0:
        return infer_type_from_data(field_value[0])
    
    return None


def resolve_type_by_name(type_name):
    """根据类型名称解析类型"""
    # 清理类型名称
    clean_name = type_name.strip()
    
    # 处理完整的模块路径
    if '.' in clean_name:
        # 提取类名
        clean_name = clean_name.split('.')[-1]
    
    # 定义类型映射表
    type_mappings = {
        # Goods相关类型
        'GoodsListDetail': ('qinsilk_scm_openapi_sdk_py.models.goods', 'GoodsListDetail'),
        'GoodsDetail': ('qinsilk_scm_openapi_sdk_py.models.goods', 'GoodsDetail'),
        'GoodsPrice': ('qinsilk_scm_openapi_sdk_py.models.goods', 'GoodsPrice'),
        'SkuDetail': ('qinsilk_scm_openapi_sdk_py.models.goods', 'SkuDetail'),
        'SkuDetailVO': ('qinsilk_scm_openapi_sdk_py.models.goods', 'SkuDetailVO'),
        
        # Color相关类型
        'ColorBaseDetail': ('qinsilk_scm_openapi_sdk_py.models.color', 'ColorBaseDetail'),
        
        # Size相关类型
        'SizeDetail': ('qinsilk_scm_openapi_sdk_py.models.size', 'SizeDetail'),
        'SizeGroupDetail': ('qinsilk_scm_openapi_sdk_py.models.size', 'SizeGroupDetail'),
        
        # 其他常见类型可以在这里添加
    }
    
    if clean_name in type_mappings:
        module_path, class_name = type_mappings[clean_name]
        try:
            # 动态导入模块
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            print(f"DEBUG: 无法导入类型 {clean_name}: {e}")
            
    # 如果未找到匹配，返回None
    print(f"DEBUG: 未找到类型映射: {clean_name}")
    return None


def infer_type_from_data(data_sample):
    """从数据样本推断类型"""
    if not isinstance(data_sample, dict):
        return None
    
    # 根据字段特征推断类型
    keys = set(data_sample.keys())
    
    # 商品相关类型推断
    if 'id' in keys and 'goods_name' in keys:
        if 'goods_sn' in keys or 'design_sn' in keys:
            # 具有商品特征的对象
            if len(keys) > 10:  # GoodsListDetail字段较多
                try:
                    from qinsilk_scm_openapi_sdk_py.models.goods import GoodsListDetail
                    return GoodsListDetail
                except ImportError:
                    pass
            else:  # GoodsDetail字段较少
                try:
                    from qinsilk_scm_openapi_sdk_py.models.goods import GoodsDetail
                    return GoodsDetail
                except ImportError:
                    pass
    
    # 颜色相关类型推断
    if 'id' in keys and 'color_value' in keys:
        try:
            from qinsilk_scm_openapi_sdk_py.models.color import ColorBaseDetail
            return ColorBaseDetail
        except ImportError:
            pass
    
    # 尺码相关类型推断
    if 'id' in keys and 'name' in keys:
        if 'size_group_id' in keys:
            # SizeDetail
            try:
                from qinsilk_scm_openapi_sdk_py.models.size import SizeDetail
                return SizeDetail
            except ImportError:
                pass
        elif len(keys) <= 3:  # SizeGroupDetail字段较少
            try:
                from qinsilk_scm_openapi_sdk_py.models.size import SizeGroupDetail
                return SizeGroupDetail
            except ImportError:
                pass
    
    # SKU相关类型推断
    if 'color_id' in keys and 'size_id' in keys:
        if 'sku_id' in keys:
            try:
                from qinsilk_scm_openapi_sdk_py.models.goods import SkuDetailVO
                return SkuDetailVO
            except ImportError:
                pass
        else:
            try:
                from qinsilk_scm_openapi_sdk_py.models.goods import SkuDetail
                return SkuDetail
            except ImportError:
                pass
    
    # 价格相关类型推断
    if 'type' in keys and 'price' in keys:
        try:
            from qinsilk_scm_openapi_sdk_py.models.goods import GoodsPrice
            return GoodsPrice
        except ImportError:
            pass
    
    print(f"DEBUG: 无法从数据推断类型: {keys}")
    return None


def extract_optional_type(field_type):
    """解包Optional类型，返回(is_optional, actual_type)"""
    actual_type = field_type
    is_optional = False
    
    # 方法1: 标准Union检测
    if get_origin(field_type) is Union and type(None) in get_args(field_type):
        is_optional = True
        non_none_types = [t for t in get_args(field_type) if t is not type(None)]
        if non_none_types:
            actual_type = non_none_types[0]
    
    # 方法2: 字符串匹配检测（兼容Python 3.12）
    elif str(field_type).startswith('typing.Union[') and 'NoneType' in str(field_type):
        is_optional = True
        # 从字符串中提取类型名
        type_str = str(field_type)
        # 匹配 typing.Union[SomeType, NoneType] 或 typing.Union[NoneType, SomeType]
        match = re.search(r'typing\.Union\[([^,]+), NoneType\]|typing\.Union\[NoneType, ([^,]+)\]', type_str)
        if match:
            type_name = match.group(1) or match.group(2)
            # 通用类型解析
            resolved_type = resolve_type_by_name(type_name.strip())
            if resolved_type:
                actual_type = resolved_type
    
    # 方法3: 直接检查字符串表示
    elif 'Optional[' in str(field_type):
        is_optional = True
        type_str = str(field_type)
        # 提取Optional[Type]中的Type
        match = re.search(r'Optional\[([^\]]+)\]', type_str)
        if match:
            type_name = match.group(1)
            # 通用类型解析
            resolved_type = resolve_type_by_name(type_name.strip())
            if resolved_type:
                actual_type = resolved_type
    
    return is_optional, actual_type


def is_list_type(type_obj):
    """检查是否为List类型"""
    origin = get_origin(type_obj)
    return (
        origin in (list, type([])) or 
        (hasattr(type_obj, '__origin__') and type_obj.__origin__ is list) or
        str(type_obj).startswith('typing.List') or
        str(type_obj).startswith('List[') or
        'List[' in str(type_obj) or
        (hasattr(type_obj, '_name') and type_obj._name == 'List')
    )