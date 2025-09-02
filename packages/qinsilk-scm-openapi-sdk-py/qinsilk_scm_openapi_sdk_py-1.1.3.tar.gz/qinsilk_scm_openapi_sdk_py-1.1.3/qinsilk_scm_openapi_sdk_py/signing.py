import hashlib
import hmac
import typing
import json
from datetime import datetime, date

SIGN_METHOD_MD5 = "md5"
SIGN_METHOD_HMAC = "hmac"
SIGN_METHOD_HMAC_SHA256 = "hmac-sha256"
CHARSET_UTF8 = "utf-8"


class SigningJSONEncoder(json.JSONEncoder):
    """签名专用的JSON编码器，处理datetime等特殊类型"""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def sign_top_request(params: typing.Dict[str, typing.Any], secret: str, sign_method: str) -> str:
    """
    给TOP请求签名。
    :param params: 请求主体内容
    :param secret: 签名密钥
    :param sign_method: 签名方法，目前支持：空（老md5)、md5, hmac_md5, hmac-sha256 三种
    :return: 签名
    """
    # 第一步：检查参数是否已经排序
    keys = sorted(params.keys())

    # 第二步：把所有参数名和参数值串在一起
    query = ""
    if sign_method == SIGN_METHOD_MD5:
        query += secret

    for key in keys:
        value = params[key]
        if value is None:
            continue

        value_str = ""
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, cls=SigningJSONEncoder, separators=(',', ':'), ensure_ascii=False)

        elif isinstance(value, (datetime, date)):
            value_str = value.isoformat()
        else:
            value_str = str(value)

        # 匹配Java的逻辑：检查去除引号后是否为"null"，以及是否为空白字符串
        value_no_quotes = value_str.replace('"', '')
        if value_str and value_no_quotes != "null" and value_str.strip():
            query += f"{key}{value_str}"

    # 第三步：使用MD5/HMAC加密
    if sign_method == SIGN_METHOD_HMAC:
        bytes_to_sign = query.encode(CHARSET_UTF8)
        secret_bytes = secret.encode(CHARSET_UTF8)
        signature = hmac.new(secret_bytes, bytes_to_sign, hashlib.md5).digest()
    elif sign_method == SIGN_METHOD_HMAC_SHA256:
        bytes_to_sign = query.encode(CHARSET_UTF8)
        secret_bytes = secret.encode(CHARSET_UTF8)
        signature = hmac.new(secret_bytes, bytes_to_sign, hashlib.sha256).digest()
    else:
        query += secret
        bytes_to_sign = query.encode(CHARSET_UTF8)
        signature = hashlib.md5(bytes_to_sign).digest()
    print(query)
    # 第四步：把二进制转化为大写的十六进制
    return signature.hex().upper()


if __name__ == '__main__':
    params = {}
    params['accessToken'] = "q5rOthX88DcKoFWlY2r38vph1O0RPldRgT6VkciRgkOfdYJxmHuYRdnxRTPd"
    params['timestamp'] = "1750829616248"
    params['name'] = "黑色"
    res= sign_top_request(params, "5e56f4b66ee74fbabf22594230600ef0", SIGN_METHOD_MD5)
    print(res)

