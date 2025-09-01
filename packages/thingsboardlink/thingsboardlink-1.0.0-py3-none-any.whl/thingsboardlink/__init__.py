"""
ThingsBoardLink - 专为 Python 开发者设计的高级 IoT 平台交互工具包
本软件包封装了 ThingsBoard 的 REST API，提供面向对象的接口，
让开发者能够轻松管理设备、处理遥测数据、控制警报等核心功能。

A high-level IoT platform interaction toolkit designed for Python developers
This package encapsulates ThingsBoard's REST API, providing object-oriented interfaces
that allow developers to easily manage devices, process telemetry data, control alarms, and other core functions.

主要功能 | Main Features:
- 设备管理 | Device Management
- 遥测数据处理 | Telemetry Data Processing  
- 属性管理 | Attribute Management
- 警报管理 | Alarm Management
- RPC 调用 | RPC Calls
- 实体关系管理 | Entity Relationship Management
"""

# 版本信息 | Version information
__version__ = "1.0.0"
__author__ = "Miraitowa-la"
__email__ = "2056978412@qq.com"
__description__ = "一个专为 Python 开发者设计的高级 IoT 平台交互工具包 | A high-level IoT platform interaction toolkit designed for Python developers"

# 导入核心类 | Import core classes
from .client import ThingsBoardClient
from .exceptions import (
    ThingsBoardError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    APIError,
    ConnectionError,
    TimeoutError,
    ConfigurationError,
    RateLimitError,
    DeviceError,
    TelemetryError,
    AlarmError,
    RPCError
)
from .models import (
    Device,
    DeviceCredentials,
    TelemetryData,
    Attribute,
    Alarm,
    RPCRequest,
    RPCResponse,
    EntityRelation,
    EntityId,
    PageData,
    TimeseriesData,
    EntityType,
    AlarmSeverity,
    AlarmStatus,
    AttributeScope
)
from .services import (
    DeviceService,
    TelemetryService,
    AttributeService,
    AlarmService,
    RpcService,
    RelationService
)

# 公开的 API | Public API
__all__ = [
    # 版本信息 | Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",

    # 核心客户端 | Core client
    "ThingsBoardClient",

    # 异常类 | Exception classes
    "ThingsBoardError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "APIError",
    "ConnectionError",
    "TimeoutError",
    "ConfigurationError",
    "RateLimitError",
    "DeviceError",
    "TelemetryError",
    "AlarmError",
    "RPCError",

    # 数据模型 | Data models
    "Device",
    "DeviceCredentials",
    "TelemetryData",
    "Attribute",
    "Alarm",
    "RPCRequest",
    "RPCResponse",
    "EntityRelation",
    "EntityId",
    "PageData",
    "TimeseriesData",
    "EntityType",
    "AlarmSeverity",
    "AlarmStatus",
    "AttributeScope",

    # 服务类 | Service classes
    "DeviceService",
    "TelemetryService",
    "AttributeService",
    "AlarmService",
    "RpcService",
    "RelationService"
]


# 便捷函数 | Convenience functions
def create_client(base_url: str, username: str = None, password: str = None, **kwargs) -> ThingsBoardClient:
    """创建 ThingsBoard 客户端的便捷函数 | Convenience function to create ThingsBoard client
    
    Args:
        base_url: ThingsBoard 服务器基础 URL | ThingsBoard server base URL
        username: 用户名（可选） | Username (optional)
        password: 密码（可选） | Password (optional)
        **kwargs: 其他客户端参数 | Other client parameters
        
    Returns:
        ThingsBoardClient: 客户端实例 | Client instance
        
    Example:
        client = create_client(
            "http://localhost:8080",
            "tenant@thingsboard.org",
            "tenant"
        )
    """
    return ThingsBoardClient(
        base_url=base_url,
        username=username,
        password=password,
        **kwargs
    )


def get_version() -> str:
    """获取软件包版本 | Get package version
    
    Returns:
        str: 版本号 | Version number
    """
    return __version__
