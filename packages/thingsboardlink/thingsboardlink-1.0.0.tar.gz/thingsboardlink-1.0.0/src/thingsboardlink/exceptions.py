"""
ThingsBoardLink 异常处理模块 | ThingsBoardLink Exception Handling Module

本模块定义了 ThingsBoardLink 软件包中使用的所有自定义异常类。
这些异常类提供了详细的错误信息和分层的异常处理机制。

This module defines all custom exception classes used in the ThingsBoardLink package.
These exception classes provide detailed error information and hierarchical exception handling.
"""

from typing import Dict, Any, Optional


class ThingsBoardError(Exception):
    """
    ThingsBoard 基础异常类 | ThingsBoard Base Exception

    所有 ThingsBoardLink 相关异常的基类。
    提供统一的异常处理接口和基础功能。

    Base class for all ThingsBoardLink related exceptions.
    Provides unified exception handling interface and basic functionality.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化异常 | Initialize exception
        
        Args:
            message: 错误消息 | Error message
            details: 错误详情字典 | Error details dictionary
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """返回异常的字符串表示 | Return string representation of exception"""
        if self.details:
            return f"{self.message}. 详情 | Details: {self.details}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式 | Convert exception to dictionary format"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(ThingsBoardError):
    """
    认证错误 | Authentication Error

    当用户认证失败时抛出此异常。
    包括登录失败、令牌过期、权限不足等情况。

    Raised when user authentication fails.
    Includes login failure, token expiration, insufficient permissions, etc.
    """
    
    def __init__(self, message: str = "认证失败 | Authentication failed", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class NotFoundError(ThingsBoardError):
    """
    资源未找到错误 | Resource Not Found Error

    当请求的资源不存在时抛出此异常。
    包括设备、用户、警报等资源未找到的情况。

    Raised when the requested resource does not exist.
    Includes cases where devices, users, alarms, etc. are not found.
    """
    
    def __init__(self, resource_type: str = "资源 | Resource", 
                 resource_id: Optional[str] = None,
                 message: Optional[str] = None):
        if message is None:
            if resource_id:
                message = f"{resource_type} '{resource_id}' 未找到 | {resource_type} '{resource_id}' not found"
            else:
                message = f"{resource_type} 未找到 | {resource_type} not found"
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, details)


class ValidationError(ThingsBoardError):
    """
    数据验证错误 | Data Validation Error

    当输入数据不符合预期格式或约束时抛出此异常。
    包括参数类型错误、值范围错误、必填字段缺失等情况。

    Raised when input data does not meet expected format or constraints.
    Includes parameter type errors, value range errors, missing required fields, etc.
    """
    
    def __init__(self, field_name: Optional[str] = None, 
                 expected_type: Optional[str] = None,
                 actual_value: Any = None,
                 message: Optional[str] = None):
        if message is None:
            if field_name and expected_type:
                message = f"字段 '{field_name}' 验证失败，期望类型: {expected_type} | Field '{field_name}' validation failed, expected type: {expected_type}"
            else:
                message = "数据验证失败 | Data validation failed"
        
        details = {
            "field_name": field_name,
            "expected_type": expected_type,
            "actual_value": actual_value
        }
        super().__init__(message, details)


class APIError(ThingsBoardError):
    """
    API 调用错误 | API Call Error

    当 API 调用返回错误状态码时抛出此异常。
    包含详细的 HTTP 状态码和响应数据。

    Raised when API call returns error status code.
    Contains detailed HTTP status code and response data.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None,
                 request_url: Optional[str] = None,
                 request_method: Optional[str] = None):
        details = {
            "status_code": status_code,
            "response_data": response_data,
            "request_url": request_url,
            "request_method": request_method
        }
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_url = request_url
        self.request_method = request_method
    
    @classmethod
    def from_response(cls, response, message: Optional[str] = None):
        """
        从 HTTP 响应创建 API 错误 | Create API error from HTTP response
        
        Args:
            response: HTTP 响应对象 | HTTP response object
            message: 自定义错误消息 | Custom error message
            
        Returns:
            APIError: API 错误实例 | API error instance
        """
        if message is None:
            message = f"API 调用失败，状态码: {response.status_code} | API call failed, status code: {response.status_code}"
        
        try:
            response_data = response.json()
        except (ValueError, AttributeError):
            response_data = {"raw_response": response.text if hasattr(response, 'text') else str(response)}
        
        return cls(
            message=message,
            status_code=getattr(response, 'status_code', None),
            response_data=response_data,
            request_url=getattr(response, 'url', None),
            request_method=getattr(response.request, 'method', None) if hasattr(response, 'request') else None
        )


class ConnectionError(ThingsBoardError):
    """
    连接错误 | Connection Error

    当无法连接到 ThingsBoard 服务器时抛出此异常。
    包括网络连接失败、服务器不可达等情况。

    Raised when unable to connect to ThingsBoard server.
    Includes network connection failures, server unreachable, etc.
    """
    
    def __init__(self, message: str = "无法连接到 ThingsBoard 服务器 | Unable to connect to ThingsBoard server",
                 server_url: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if server_url:
            details["server_url"] = server_url
        super().__init__(message, details)


class TimeoutError(ThingsBoardError):
    """
    超时错误 | Timeout Error

    当请求超时时抛出此异常。
    包括连接超时、读取超时等情况。

    Raised when request times out.
    Includes connection timeout, read timeout, etc.
    """
    
    def __init__(self, message: str = "请求超时 | Request timeout",
                 timeout_seconds: Optional[float] = None,
                 operation: Optional[str] = None):
        details = {
            "timeout_seconds": timeout_seconds,
            "operation": operation
        }
        super().__init__(message, details)


class ConfigurationError(ThingsBoardError):
    """
    配置错误 | Configuration Error

    当配置参数无效或缺失时抛出此异常。
    包括服务器地址错误、认证信息缺失等情况。

    Raised when configuration parameters are invalid or missing.
    Includes server address errors, missing authentication information, etc.
    """
    
    def __init__(self, message: str = "配置错误 | Configuration error",
                 config_key: Optional[str] = None,
                 expected_value: Optional[str] = None):
        details = {
            "config_key": config_key,
            "expected_value": expected_value
        }
        super().__init__(message, details)


class RateLimitError(APIError):
    """
    速率限制错误 | Rate Limit Error

    当 API 调用超过速率限制时抛出此异常。
    包含重试建议和限制信息。

    Raised when API calls exceed rate limits.
    Contains retry suggestions and limit information.
    """
    
    def __init__(self, message: str = "API 调用速率超限 | API call rate limit exceeded",
                 retry_after: Optional[int] = None,
                 limit_type: Optional[str] = None):
        details = {
            "retry_after": retry_after,
            "limit_type": limit_type
        }
        super().__init__(message, status_code=429, response_data=details)


class DeviceError(ThingsBoardError):
    """
    设备相关错误 | Device Related Error

    设备操作相关的错误。
    包括设备创建失败、设备状态异常等情况。

    Device operation related errors.
    Includes device creation failure, abnormal device status, etc.
    """
    
    def __init__(self, message: str, device_id: Optional[str] = None,
                 device_name: Optional[str] = None):
        details = {
            "device_id": device_id,
            "device_name": device_name
        }
        super().__init__(message, details)


class TelemetryError(ThingsBoardError):
    """
    遥测数据相关错误 | Telemetry Data Related Error

    遥测数据操作相关的错误。
    包括数据格式错误、上传失败等情况。

    Telemetry data operation related errors.
    Includes data format errors, upload failures, etc.
    """
    
    def __init__(self, message: str, data_key: Optional[str] = None,
                 data_value: Any = None):
        details = {
            "data_key": data_key,
            "data_value": data_value
        }
        super().__init__(message, details)


class AlarmError(ThingsBoardError):
    """
    警报相关错误 | Alarm Related Error
    
    警报操作相关的错误。
    包括警报创建失败、状态更新失败等情况。
    
    Alarm operation related errors.
    Includes alarm creation failure, status update failure, etc.
    """
    
    def __init__(self, message: str, alarm_id: Optional[str] = None,
                 alarm_type: Optional[str] = None):
        details = {
            "alarm_id": alarm_id,
            "alarm_type": alarm_type
        }
        super().__init__(message, details)


class RPCError(ThingsBoardError):
    """
    RPC 调用相关错误 | RPC Call Related Error
    
    RPC 调用相关的错误。
    包括调用超时、设备无响应等情况。
    
    RPC call related errors.
    Includes call timeout, device no response, etc.
    """
    
    def __init__(self, message: str, method_name: Optional[str] = None,
                 device_id: Optional[str] = None,
                 timeout_seconds: Optional[float] = None):
        details = {
            "method_name": method_name,
            "device_id": device_id,
            "timeout_seconds": timeout_seconds
        }
        super().__init__(message, details)