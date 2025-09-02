"""
序列化工具模块
包含JSON编码器、字典键转换、数据清理等功能
"""
import json
import re
from datetime import datetime, date


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime等特殊类型"""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def to_snake_case(name: str) -> str:
    """将驼峰命名转换为下划线命名"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_camel_case(name: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = name.split('_')
    result = components[0]
    
    for word in components[1:]:
        # 标准驼峰命名：只将首字母大写，其余小写
        result += word.capitalize()
    
    return result


def convert_dict_keys_to_snake_case(data):
    """递归地将字典的键从驼峰命名转换为下划线命名"""
    if isinstance(data, dict):
        return {to_snake_case(k): convert_dict_keys_to_snake_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys_to_snake_case(item) for item in data]
    else:
        return data


def convert_dict_keys_to_camel_case(data):
    """递归地将字典的键从下划线命名转换为驼峰命名"""
    if isinstance(data, dict):
        return {to_camel_case(k): convert_dict_keys_to_camel_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys_to_camel_case(item) for item in data]
    else:
        return data


def remove_none_values(data):
    """递归地移除None值，模拟Java的JSON序列化行为"""
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if v is not None:
                cleaned_v = remove_none_values(v)
                if cleaned_v is not None:
                    result[k] = cleaned_v
        return result
    elif isinstance(data, list):
        return [remove_none_values(item) for item in data if item is not None]
    elif isinstance(data, (datetime, date)):
        # datetime对象保持原样，会在JSON序列化时通过CustomJSONEncoder处理
        return data
    else:
        return data