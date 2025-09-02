"""
DataClass助手模块
包含从字典实例化dataclass对象的复杂逻辑
"""
from dataclasses import fields, is_dataclass
from .type_conversion import (
    is_dataclass_type, 
    extract_list_element_type, 
    extract_optional_type,
    is_list_type
)


def instantiate_dataclass_from_dict(cls, data):
    """从字典实例化dataclass"""
    if not is_dataclass(cls) or not isinstance(data, dict):
        return cls() if callable(cls) else cls

    kwargs = {}
    cls_fields = {f.name: f.type for f in fields(cls)}

    for name, value in data.items():
        if name in cls_fields and value is not None:
            field_type = cls_fields[name]
            print(f"DEBUG: 处理字段 {name}, 原始类型: {field_type}, 值类型: {type(value)}")
            
            # 解包Optional类型
            is_optional, actual_type = extract_optional_type(field_type)
            
            print(f"DEBUG: Optional检测结果: is_optional={is_optional}, actual_type={actual_type}")
            if is_optional and actual_type != field_type:
                print(f"DEBUG: Optional类型解包: {field_type} -> {actual_type}")

            # 检查是否为List类型
            if is_list_type(actual_type) and isinstance(value, list):
                print(f"DEBUG: 处理List类型字段 {name}")
                # 处理List类型
                item_type = extract_list_element_type(actual_type, field_type, name, value)
                
                if item_type and is_dataclass_type(item_type):
                    print(f"DEBUG: List元素类型 {item_type} 是dataclass")
                    # 转换列表中的每个元素
                    converted_items = []
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            try:
                                converted_item = instantiate_dataclass_from_dict(item_type, item)
                                converted_items.append(converted_item)
                            except Exception:
                                converted_items.append(item)
                        else:
                            converted_items.append(item)
                    kwargs[name] = converted_items
                else:
                    kwargs[name] = value
            elif is_dataclass_type(actual_type) and isinstance(value, dict):
                print(f"DEBUG: 单个dataclass字段 {name}, 类型: {actual_type}")
                # 处理单个dataclass对象
                try:
                    converted_obj = instantiate_dataclass_from_dict(actual_type, value)
                    kwargs[name] = converted_obj
                    print(f"DEBUG: 成功转换字段 {name} 为 {type(converted_obj).__name__}")
                except Exception as e:
                    print(f"DEBUG: 转换字段 {name} 失败: {e}")
                    kwargs[name] = value
            else:
                print(f"DEBUG: 使用原始值处理字段 {name}")
                kwargs[name] = value
        else:
            # 字段不存在或值为None
            if name in cls_fields:
                kwargs[name] = value

    try:
        result = cls(**kwargs)
        print(f"DEBUG: 成功创建 {cls.__name__} 实例")
        return result
    except Exception as e:
        print(f"DEBUG: 创建 {cls.__name__} 实例失败: {e}")
        # 如果实例化失败，返回空实例
        return cls() if callable(cls) else data