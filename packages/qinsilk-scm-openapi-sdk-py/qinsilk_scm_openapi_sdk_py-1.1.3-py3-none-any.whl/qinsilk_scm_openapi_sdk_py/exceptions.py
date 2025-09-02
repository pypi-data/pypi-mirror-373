
import enum


class ErrorCode(enum.Enum):
    UNKNOWN_ERROR = (1, "未知错误")
    CONNECT_TIMEOUT = (2, "连接超时")
    READ_TIMEOUT = (3, "读取超时")
    INVALID_REQUEST = (4, "非法请求")
    INVALID_RESPONSE = (5, "非法响应")
    INVALID_ACCESS_TOKEN = (6, "无效的访问令牌")
    FORBIDDEN = (7, "权限不足")
    SERVER_ERROR = (8, "服务端错误")

    def __init__(self, code, message):
        self.code = code
        self.message = message


class OpenException(Exception):
    def __init__(self, error_code: ErrorCode, exception=None, trace_id=None):
        self.code = error_code.code
        self.message = error_code.message
        self.exception = exception
        self.trace_id = trace_id
        super().__init__(f"Error {self.code}: {self.message}")

    def __str__(self):
        return f"OpenException(code={self.code}, message='{self.message}', trace_id='{self.trace_id}')" 